import random
import logging
import copy
import os
import sys
import json
import string
import pdb
import subprocess
import hashlib
import time
import math
import six

from shutil import copyfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PYTHON3_MARKER = '__PYTHON3__'
MAX_RUNTIME = 60
MAX_ITERATIONS = 100
NUM_CASES = 25
SOLUTION_FILE = 'solution.py'
SEED_FILE = 'seed.json'

def isPython3():
    return sys.version_info >= (3, 0)

interpreter = 'python3' if isPython3() else 'python'

class Mutation():
    def __init__(self, sequence):
        self.input_set = self.generateInputSet(sequence)
        self.random = False
        self.index = 0

    def flatten(self, l):
        return [item for sublist in l for item in sublist]

    def generateInputSet(self, sequence):
        ''' Generates a list mapping index in the sequence to a list of potential values '''
        input_set = []
        for ele in sequence:
            if isinstance(ele, six.string_types):
                input_set.append(ele.split(''))
            elif ele.__class__ == dict:
                continue
            elif ele.__class__ == list:
                s = []
                for subele in ele:
                    #rs = self.flatten(self.generateInputSet(subele))
                    #s.append(rs)
                    s.append([subele])
                        
                input_set.append(self.flatten(s))
            else:
                input_set.append([ele])
        return input_set
       
    def getFromInputSet(self):
        l = self.input_set[self.index]
        return l[random.randint(0, len(l) - 1)]

    def mutateNum(self, literal):
        if not self.random:
            return self.getFromInputSet()    
        else:
            is_edge = random.randint(0, 50) < 2
            if is_edge:
                return sys.maxsize if is_edge == 0 else -sys.maxsize - 1
            else:
                return literal + random.randint(-10, 10)

    def setRandomMethod(self):
        self.random = random.randint(0, 1) == 0

    def mutateStr(self, literal):
        s = ''
        is_edge = random.randint(0, 50) < 2
        if is_edge:
            num_characters = random.randint(1, 25)
        else:
            num_characters = 256 if is_edge == 0 else 0

        for c in range(0, num_characters):
            s += random.choice(string.letters)
        return s

    def mutateList(self, literal):
        for i, ele in enumerate(literal):
            literal[i] = self.mutate(ele)
        return literal

    def mutateDict(literal):
        return literal

    def mutate(self, literal):
        if isinstance(literal, six.string_types):
            return self.mutateStr(literal)
        elif literal.__class__ == int or literal.__class__ == float:
            return self.mutateNum(literal)
        elif literal.__class__ == list:
            return self.mutateList(literal)
        elif literal.__class__ == dict:
            return self.mutateDict(literal)
        else:
            logger.error('Tried to mutate unknown literal of type %s' % literal.__class__)

def getSequenceKey(sequence_string):
    return hashlib.md5(sequence_string.encode('utf-8')).hexdigest()

def getNumMutations(iteration, num_good_sequences):
    threshold_breached = iteration > MAX_ITERATIONS / 2
    lacking_sequences = num_good_sequences < NUM_CASES
    if threshold_breached and lacking_sequences:
        return int(math.log(iteration))
    return 1

def test(dir_path, sequence_string):
    # Generate the test case
    file_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
    file_path = os.path.join(dir_path, file_name) 
    fp = open(file_path, 'w')
    fp.write(sequence_string)
    fp.close()
    command = "cd %s; timeout 10s sh -c '%s driver.py %s %s; rm %s'" % (dir_path, interpreter, SOLUTION_FILE, file_name, file_name)
    logger.debug('Running command: %s' % command)
    results = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return results

if __name__ == "__main__":
    dir_path = sys.argv[1]
    test_path = os.path.join(dir_path, SEED_FILE)
    original_sequence = json.loads(open(test_path).read())

    if len(original_sequence) == 0:
        logger.error('No inputs to mutate, exiting...')
        sys.exit()

    good_sequences = [original_sequence]
    bad_sequences = []

    outputs = []
    outputs_map = {}
    
    i = 0
    start_time = time.time()
    mutation = Mutation(original_sequence)
    while i < MAX_ITERATIONS and time.time() - start_time < MAX_RUNTIME:
        sequences = len(good_sequences)

        # Pick a random good sequence and copy it
        index = random.randint(int(sequences / 2), sequences - 1)
        random_sequence = good_sequences[index]
        new_sequence = copy.deepcopy(random_sequence)
        
        if i != 0:
            # Pick a index to mutate and mutate it
            num_mutations = getNumMutations(i, sequences)
            for n in range(num_mutations):
                index = random.randint(0, len(random_sequence) - 1)
                mutation.index = index
                mutation.setRandomMethod()
                new_sequence[index] = mutation.mutate(new_sequence[index])
            logger.debug('Generated new sequence: %s' % new_sequence)

        # Check if sequence has been seen
        sequence_string = json.dumps(new_sequence)
        key = getSequenceKey(sequence_string)
        if key in outputs_map:
            continue

        # Test the new sequence
        popen_results = test(dir_path, sequence_string)
        stdout = popen_results.stdout.read()
        outputs_map[key] = stdout.decode('utf-8')
        stderr = popen_results.stderr.read()
        
        # If the sequence is good, add it good sequences
        valid_stderr = len(stderr) == 0
        valid_stdout = stdout not in outputs and len(stdout) > 0

        if valid_stdout and valid_stderr:
            outputs.append(stdout)
            good_sequences.append(new_sequence)
        else:
            if not valid_stderr:
                logger.debug('Bad sequence with error: %s' % stderr)
                bad_sequences.append(new_sequence)
                
        i += 1 
    
    # Write cases to files
    cases_dir = os.path.join(dir_path, 'cases')
    if not os.path.exists(cases_dir):
        os.mkdir(cases_dir)

    answers_dir = os.path.join(dir_path, 'answers')
    if not os.path.exists(answers_dir):
        os.mkdir(answers_dir)
    
    # If is python3, create a marker denoting that it is
    python3_marker = os.path.join(dir_path, PYTHON3_MARKER)
    if isPython3():
        if not os.path.exists(PYTHON3_MARKER):
            open(python3_marker, 'a').close()
    else:
        if os.path.exists(python3_marker):
            os.remove(python3_marker)
        

    i = 0
    num_sequences = len(good_sequences)
    while i < NUM_CASES:
        if i == num_sequences:
            break
        
        if i == 0:
            sequence_num = 0
        else:
            sequence_num = num_sequences - 1 - i

        sequence = good_sequences[sequence_num]
        sequence_string = json.dumps(sequence)

        # Write test case 
        case_path = os.path.join(cases_dir, str(i))
        fp = open(case_path, 'w')
        fp.write(sequence_string)
        fp.close

        # Write answer
        answer_path = os.path.join(answers_dir, str(i))
        fp = open(answer_path, 'w')
        key = getSequenceKey(sequence_string)
        fp.write(outputs_map[key])
        fp.close() 

        i += 1

