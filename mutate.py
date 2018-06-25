import random
import logging
import copy
import os
import sys
import json
import string
import pdb
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAX_ITERATIONS = 1

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
    if literal.__class__ == str:
        return mutateStr(literal)
    elif literal.__class__ == int or literal.__class__ == float:
        return mutateNum(literal)
    elif literal.__class__ == list:
        return mutateList(literal)
    elif literal.__class__ == dict:
        return mutateDict(literal)
    else:
        logger.error('Tried to mutate unknown literal of type %s' % literal.__class__)

if __name__ == "__main__":
    test_path = sys.argv[1]
    dir_path = os.path.dirname(test_path)
    original_sequence = json.loads(open(test_path).read())

    good_sequences = [original_sequence]
    bad_sequences = []
    
    i = 0
    while i < MAX_ITERATIONS:
        # Pick a random good sequence and copy it
        random_sequence = good_sequences[random.randint(0, len(good_sequences) - 1)]
        new_sequence = copy.deepcopy(random_sequence)

        # Pick a index to mutate and mutate it
        index = random.randint(0, len(random_sequence) - 1)
        new_sequence[index] = mutate(new_sequence[index])

        # Check if sequence has been seen
        
        # Generate the test case
        file_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        file_path = os.path.join(dir_path, file_name) 
        fp = open(file_path, 'w')
        logger.info('Generated new sequence: %s' % new_sequence)
        fp.write(json.dumps(new_sequence))
        fp.close()

        # Test the new sequence
        command = "cd %s; python driver.py %s" % (dir_path, file_name)
        logger.info('Running command: %s' % command)
        popen_results = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = popen_results.stdout.read()
        logger.debug(stdout)
        stderr = popen_results.stderr.read()
        os.remove(file_path)
        
        # If the sequence is good, add it good sequences
        valid = True
        if len(stderr) == 0:
            good_sequences.append(new_sequence)
        else:
            bad_sequences.append(new_sequence)

        i += 1

