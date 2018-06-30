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

from shutil import copyfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAX_RUNTIME = 60 * 5
MAX_ITERATIONS = 100
NUM_CASES = 10
SOLUTION_FILE = 'solution.py'
SEED_FILE = 'seed.json'

def mutateNum(literal):
    return literal + random.randint(-10, 10)

def mutateStr(literal):
    string = ''
    for c in literal:
        string += random.choice(string.letters)
    return string

def mutateList(literal):
    for i, ele in enumerate(literal):
        literal[i] = mutate(ele)
    return literal

def mutateDict(literal):
    return literal

def mutate(literal):
    if literal.__class__ == str or literal.__class__ == unicode:
        return mutateStr(literal)
    elif literal.__class__ == int or literal.__class__ == float:
        return mutateNum(literal)
    elif literal.__class__ == list:
        return mutateList(literal)
    elif literal.__class__ == dict:
        return mutateDict(literal)
    else:
        logger.error('Tried to mutate unknown literal of type %s' % literal.__class__)

def getNumMutations(iteration, num_good_sequences):
    threshold_breached = iteration > MAX_ITERATIONS / 2
    lacking_sequences = num_good_sequences < NUM_CASES
    if threshold_breached and lacking_sequences:
        return int(math.log(iteration))
    return 1

if __name__ == "__main__":
    dir_path = sys.argv[1]
    test_path = os.path.join(dir_path, SEED_FILE)
    original_sequence = json.loads(open(test_path).read())

    good_sequences = [original_sequence]
    bad_sequences = []
    outputs = []
    outputs_map = {}
    
    i = 0
    start_time = time.time()
    while (i < MAX_ITERATIONS or len(good_sequences) < NUM_CASES) and time.time() - start_time < MAX_RUNTIME:
        # Pick a random good sequence and copy it
        index = random.randint(len(good_sequences) / 2, len(good_sequences) - 1)
        random_sequence = good_sequences[index]
        new_sequence = copy.deepcopy(random_sequence)
        
        if i != 0:
            # Pick a index to mutate and mutate it
            num_mutations = getNumMutations(i, len(good_sequences))
            for n in range(num_mutations):
                index = random.randint(0, len(random_sequence) - 1)
                new_sequence[index] = mutate(new_sequence[index])
        
        # Check if sequence has been seen
        sequence_string = json.dumps(new_sequence)
        key = hashlib.md5(sequence_string).hexdigest()
        if key in outputs_map:
            continue
        
        # Generate the test case
        file_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        file_path = os.path.join(dir_path, file_name) 
        fp = open(file_path, 'w')
        logger.debug('Generated new sequence: %s' % new_sequence)
        fp.write(sequence_string)
        fp.close()

        # Test the new sequence
        command = "cd %s; timeout 10s python driver.py %s %s" % (dir_path, SOLUTION_FILE, file_name)
        logger.debug('Running command: %s' % command)
        popen_results = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = popen_results.stdout.read()
        outputs_map[key] = stdout
        stderr = popen_results.stderr.read()
        os.remove(file_path)
        
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
    
    # Copy the base test
    #copyfile(test_path, os.path.join(cases_dir, '0'))

    # Write cases to files
    cases_dir = os.path.join(dir_path, 'cases')
    if not os.path.exists(cases_dir):
        os.mkdir(cases_dir)

    answers_dir = os.path.join(dir_path, 'answers')
    if not os.path.exists(answers_dir):
        os.mkdir(answers_dir)

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
        key = hashlib.md5(sequence_string).hexdigest()
        fp.write(outputs_map[key])
    
        i += 1


