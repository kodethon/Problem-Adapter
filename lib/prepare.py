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

def isVariable(node):
    return node.__class__ == ast.Name

def isAttribute(node):
    return node.__class__ == ast.Attribute

def isFunctionCall(node):
    ''' FOOBAR() '''
    return node.__class__ == ast.Call

def isFunctionDef(node):
    ''' def FOOBAR '''
    return node.__class__ == ast.FunctionDef

def isAssignment(node):
    return node.__class__ == ast.Assign

def getFunctionName(node):
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
        elif isLiteralStr(elt):
            ar.append(elt.s)
        else:
            logger.error('Tried to parse unknown ele of type %s' % node.__class__)
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

### OUTLINE
def getFunctionDefs(_ast):
    ''' Returns a dictionary of function definitions mapped to line numbers '''
    functions = {}
    for node in ast.walk(_ast):
        if isFunctionDef(node):
            functions[node.name] = node.lineno
    return functions

def findSplitPoint(source, functions):
    ''' Line of code where functions definitions stop '''

    lines = source.split("\n")
    count = 0
    start = max(functions.values())

    for line in lines[start:]:
        if len(line) == 0:
            continue

        if line[0] != ' ' and line[0] != "\t":
            return start + count + 1
        count += 1

def splitSource(source, lineno):
    ''' Splits the source at lineno and returns both parts '''
    lines = source.split("\n")
    return "\n".join(lines[0:lineno]), "\n".join(lines[lineno:])

def modifyDriverArgs(functions, _ast, marker):
    st = {} # Symbol Table
    for node in ast.walk(_ast):
        # If assignment, update symbol table
        if isAssignment(node):
            for target in node.targets:
                st[target.id] = node

    args = []
    arg_num = 0
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
            # Function calls should be ignored...
            if isVariable(arg) and arg.id in st:
                logger.debug("Processing argument variable %s for function %s" % (arg.id, func_name))
                rhv = st[arg.id]
                if isFunctionCall(rhv.value):
                    continue
                else:
                    args.append(parseRHS(rhv.value))
                    rhv.value = ast.Str(addStub(arg_num, marker))
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

def getFunctionCallers(_ast):
    ''' Returns a dictionary of function calls mapped to instances '''
    functions = {}
    for node in ast.walk(_ast):
        if isFunctionCall(node):
            if not node.name in functions:
                functions[node.name] = 0
            functions[node.name] += 1
    return functions

def writeOutput(driver, main, case):
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

    fp = open(os.path.join(sandbox, 'module.py'), 'w')
    fp.write(main)
    fp.close()

    fp = open(os.path.join(sandbox, 'test-0.json'), 'w')
    fp.write(json.dumps(case))

if __name__ == "__main__":
    # Read file contents
    fp = open(sys.argv[1])
    code = fp.read()
    _ast = ast.parse(code)

    functions = getFunctionDefs(_ast)
    lineno = findSplitPoint(code, functions)

    # Generate modified source code
    main, driver = splitSource(code, lineno)
    _ast = ast.parse(driver)

    # Replace caller args with different value
    marker = "*****"

    case = modifyDriverArgs(functions, _ast, marker) 
    code = astor.to_source(_ast)
    code = code.replace("%s'" % marker, '')
    code = code.replace("'%s" % marker, '')
    driver = code.replace(main, '')
    driver = "execfile('module.py')\n\nimport json\nimport sys\n\n_INPUTS = json.loads(open(sys.argv[1]).read())\n\n" + driver
    
    writeOutput(driver, main, case) 
