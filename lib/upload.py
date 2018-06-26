import sys
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DESCRIPTION_FILE = 'description.txt'
AUTOGRADER_REL_PATH = '../autograder'

file_path = sys.argv[1]
if not os.path.exists(file_path):
    logger.error("%s does not exist!" % file_path)
    sys.exit()

dir_path = os.path.dirname(file_path)
description_path = os.path.join(dir_path, DESCRIPTION_FILE)
if not os.path.exists(description_path):
    logger.error("%s does not exist!" % description_path)
    sys.exit()

fp = open(description_path, 'r')
description = fp.read()
fp.close()

cases_path = os.path.join(dir_path, 'cases')
if not os.path.exists(cases_path):
    logger.error("%s does not exist!" % cases_path)
    sys.exit()

answers_path = os.path.join(dir_path, 'answers')
if not os.path.exists(answers_path):
    logger.error("%s does not exist!" % answers_path)
    sys.exit()

# Generate all the cases
cases = []
for filename in os.listdir(cases_path):
    fp = open(os.path.join(answers_path, filename), 'r')
    answer = fp.read()
    fp.close()
    cases.append({
        'number' : int(filename),
        'arguments' : os.path.join(AUTOGRADER_REL_PATH, filename),
        'answer' : answer
    })

print cases
