# ASSUMPTION: functions are defined before they are called

import ast
import sys
import astor
import json
import os
import logging

import pdb

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

### HELPERS
def getArgs(node):
    args = []
    for arg in node.args.args:
        args.append(arg.id)
    return args

def isBinOp(node):
    return node.__class__ == ast.BinOp

def isLiteralNum(node):
    return node.__class__ == ast.Num

def isLiteralStr(node):
    return node.__class__ == ast.Str

def isLiteralList(node):
    return node.__class__ == ast.List

def isUnaryOp(node):
    return node.__class__ == ast.UnaryOp

def isVariable(node):
    return node.__class__ == ast.Name or node.__class__ == ast.Subscript

def getVariableName(node):
    if node.__class__ == ast.Name:
        return node.id
    if node.__class__ == ast.Subscript:
        return node.value.id

def isAttribute(node):
    return node.__class__ == ast.Attribute

def isFunctionCall(node):
    ''' FOOBAR() '''
    return node.__class__ == ast.Call

def isFunctionDef(node):
    ''' def FOOBAR '''
    return node.__class__ == ast.FunctionDef

def isClassDef(node):
    ''' class FOO '''
    return node.__class__ == ast.ClassDef

def isAssignment(node):
    return node.__class__ == ast.Assign

def getFunctionName(node):
    if node.__class__ == ast.FunctionDef:
        return node.name
    else:
        func = node.func
        if func.__class__  == ast.Name:
            return func.id
        else:
            return func.attr

def parseList(node):
    ''' Given node is of type list, returns an actual list '''
    ar = [] 
    for elt in node.elts:
        if isLiteralNum(elt):
            ar.append(elt.n) 
        elif isUnaryOp(elt):
            ar.append(-elt.operand.n)
        elif isLiteralStr(elt):
            ar.append(elt.s)
        elif isLiteralList(elt):
            ar.append(parseList(elt))
        else:
            logger.error('Tried to parse unknown ele of type %s' % elt.__class__)
    return ar

def parseRHS(node):
    ''' Returns literal value '''
    if isLiteralNum(node):
        return node.n
    elif isLiteralStr(node):
        return node.s
    elif isLiteralList(node):
        return parseList(node)
    else:
        logger.error('Tried to parse unknown RHS of type %s' % node.__class__)

def addStub(arg_num, marker):
    return "%s_INPUTS[%s]%s" % (marker, arg_num, marker)

def modifyRHS(rhs, args, arg_num, marker):
    if not isFunctionCall(rhs.value):
        args.append(parseRHS(rhs.value))
        rhs.value = ast.Str(addStub(arg_num, marker))
        return True
    return False

### OUTLINE
def getFunctionDefs(_ast):
    ''' Returns a dictionary of function definitions mapped to line numbers '''
    functions = {}
    for node in ast.walk(_ast):
        if isFunctionDef(node) or isClassDef(node):
            functions[node.name] = node.lineno
    return functions

def getFunctionCallers(_ast):
    ''' Returns a dictionary of function calls mapped to instances '''
    functions = {}
    for node in ast.walk(_ast):
        if isFunctionCall(node):
            func_name = getFunctionName(node) 
            if not func_name in functions:
                functions[func_name] = 0
            functions[func_name] += 1
    return functions

def tryInlineMain(code, split_point, functions, callers):
    if 'main' not in functions or 'main' not in callers:
        return None, None
    else:
        lineno = functions['main']
        num_callers = callers['main']
        if split_point > lineno and num_callers == 1:
            main, driver = splitSource(code, lineno)

            # Find the 'main' function body
            main_function_start = -1
            main_function_end = -1
            _ast = ast.parse(main)
            for node in ast.walk(_ast):
                if not isFunctionDef(node):
                    continue
                func_name = getFunctionName(node)
                if func_name != 'main':
                    continue
                main_function_start = node.lineno
                main_function_end = findFunctionEnd(main, node.lineno)
                break
                       
            lines = main.split("\n")
            main_function = "\n".join(lines[main_function_start:main_function_end])
            # main_function_start = lineno of 'def main', subtract 1 from it to get the line before it
            main = "\n".join(lines[0:main_function_start - 1]) + "\n".join(lines[main_function_end:])

            _ast = ast.parse(driver)
            for node in ast.walk(_ast):
                if not isFunctionCall(node):
                    continue
                func_name = getFunctionName(node)
                if func_name != 'main':
                    continue
                lines = driver.split("\n")
                lines[node.lineno - 1] = main_function 
                return main, "\n".join(lines)

def findSplitPoint(source, functions):
    ''' Line of code where functions definitions stop '''
    start = max(functions.values())
    return findFunctionEnd(source, start) 

def findFunctionEnd(source, start):
    lines = source.split("\n")
    for i in range(start, len(lines)):
        line = lines[i]
        if len(line) > 0 and not line[0].isspace():
            return i - 1
    return i

def splitSource(source, lineno):
    ''' Splits the source at lineno and returns both parts '''
    lines = source.split("\n")
    return "\n".join(lines[0:lineno + 1]), "\n".join(lines[lineno + 1:])

def removeFunctionBodies(_ast):
    for node in ast.walk(_ast):
        if not isFunctionDef(node):
            continue
        node.body = [ast.Pass()]

def getSymbol(node):
    symbol = ''
    if node.__class__ == ast.Attribute:
        symbol = node.attr
        node = node.value
        while node.__class__ == ast.Attribute:
            symbol = node.attr + '.' + symbol
            node = node.value
        symbol = node.id + '.' + symbol
    else:
        symbol = node.id
    return symbol

def modifyDriverArgs(functions, _ast, marker):
    args = []
    arg_num = 0

    # Pass 1
    st = {} # Symbol Table
    for node in ast.walk(_ast):
        if not isAssignment(node):
            continue
        # If assignment, update symbol table
        for target in node.targets:
            if isVariable(target):
                st[target.id] = node
            elif isAttribute(target):
                # If symbol has an attribute e.g. obj.attr, then try to modify it 
                symbol = getSymbol(target)
                # % (target.value.id, target.attr)
                logger.info('Processing symbol with attribute: %s' % symbol)
                modified = modifyRHS(node, args, arg_num, marker)
                arg_num = arg_num + 1 if modified else arg_num
                st[symbol] = node
            else:
                logger.error('Encountered a symbol with an unknown target type.')

    # Pass 2
    for node in ast.walk(_ast):
        if not isFunctionCall(node):
            continue
        
        # Skip not defined functions
        func_name = getFunctionName(node)
        if func_name not in functions:
            continue
        
        for arg in node.args:
            # If one of the args is a variable that has been defined,
            # replace the variable definiation with a stub
            if isVariable(arg):
                var_name = getVariableName(arg)

                # If the variable is not in the symbol table, 
                # then assume it is not something we should modify
                if not var_name in st:
                    continue

                logger.debug("Processing argument variable %s for function %s" % (var_name, func_name))

                rhs = st[var_name]
                if rhs == None:
                    continue

                modified = modifyRHS(rhs, args, arg_num, marker)
                # Function calls should be ignored...
                if not modified:
                    continue
                
                # Delete the symbol from the table
                del st[var_name]
            elif isLiteralNum(arg):
                logger.debug("Processing argument number %s for function %s" % (arg.n, func_name))
                args.append(arg.n)
                arg.n = addStub(arg_num, marker)
            elif isLiteralStr(arg):
                logger.debug("Processing argument string %s for function %s" % (arg.s, func_name))
                args.append(arg.s)
                arg.s = addStub(arg_num, marker)
            else:
                logger.debug("Skipping argument of type %s" % arg.__class__)
                continue
            arg_num += 1
    return args

def writeOutput(driver, main, skeleton, case):
    dest_dir = 'output'
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    filename = "%s" % (os.path.basename(sys.argv[1]).split('.')[0])
    sandbox = os.path.join(dest_dir, filename)
    if not os.path.exists(sandbox):
        os.mkdir(sandbox)

    fp = open(os.path.join(sandbox, 'driver.py'), 'w')
    fp.write(driver)
    fp.close()

    fp = open(os.path.join(sandbox, 'solution.py'), 'w')
    fp.write(main)
    fp.close()

    fp = open(os.path.join(sandbox, 'skeleton.py'), 'w')
    fp.write(skeleton)
    fp.close()

    fp = open(os.path.join(sandbox, 'seed.json'), 'w')
    fp.write(json.dumps(case))
    fp.close()

if __name__ == "__main__":
    logger.info('Processing %s' % sys.argv[1])

    # Read file contents
    fp = open(sys.argv[1])
    code = fp.read()
    try:
        _ast = ast.parse(code)
    except SyntaxError as e:
        logger.error('Could not parse %s' % sys.argv[1])
        logger.error(e)
        sys.exit()

    functions = getFunctionDefs(_ast)
    callers = getFunctionCallers(_ast)
    lineno = findSplitPoint(code, functions)

    # Generate modified source code
    main, driver = tryInlineMain(code, lineno, functions, callers)
    if not main or not driver:
        main, driver = splitSource(code, lineno)

    # Generate skeleton code
    _ast = ast.parse(main)
    removeFunctionBodies(_ast)
    skeleton = astor.to_source(_ast)

    _ast = ast.parse(driver)

    # Replace caller args with different value
    marker = "*****"

    case = modifyDriverArgs(functions, _ast, marker) 
    
    code = astor.to_source(_ast)
    code = code.replace("%s'" % marker, '')
    code = code.replace("'%s" % marker, '')
    driver = code.replace(main, '')
    driver = "import json\nimport sys\n\nexec(open(sys.argv[1]).read())\n\n_INPUTS = json.loads(open(sys.argv[2]).read())\n\n" + driver
    
    writeOutput(driver, main, skeleton, case) 
