import sys
import os
import logging
import json
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DESCRIPTION_FILE = 'description.txt'
AUTOGRADER_REL_PATH = '../autograder'
CASES_FOLDER = 'cases'
CONTAINER_NAME_ENV = 'KODETHON_CONTAINER_NAME'
USER_ID_ENV = 'KODETHON_USER_ID'
ACCESS_TOKEN_ENV = 'KODETHON_ACCESS_TOKEN'
URL = 'http://localhost:3456/course/test/import'

def beautifyTitle(title):
    title = title.replace('-', ' ')
    return title.title()

if __name__ == "__main__":
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        logger.error("%s does not exist!" % file_path)
        sys.exit()

    if os.environ[CONTAINER_NAME_ENV] == None:
        logger.error("%s is not set." % CONTAINER_NAME_ENV)
        sys.exit()

    if os.environ[USER_ID_ENV] == None:
        logger.error("%s is not set." % USER_ID_ENV)
        sys.exit()

    if os.environ[ACCESS_TOKEN_ENV] == None:
        logger.error("%s is not set." % ACCESS_TOKEN_ENV)
        sys.exit()

    dir_path = os.path.dirname(file_path)
    dirname = os.path.basename(dir_path)
    description_path = os.path.join(dir_path, DESCRIPTION_FILE)
    if not os.path.exists(description_path):
        logger.error("%s does not exist!" % description_path)
        sys.exit()

    fp = open(description_path, 'r')
    description = fp.read().strip()
    fp.close()

    cases_path = os.path.join(dir_path, CASES_FOLDER)
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
            'arguments' : os.path.join(AUTOGRADER_REL_PATH, CASES_FOLDER, filename),
            'answer' : answer
        })
    
    package = {
        'user_id' : os.environ['KODETHON_USER_ID'],
        'access_token' : os.environ['KODETHON_ACCESS_TOKEN'],
        'container_name' : os.environ['KODETHON_CONTAINER_NAME'],
        'test_name': beautifyTitle(dirname),
        'style' : 'diff',
        'cases' : cases,
        'description' : description,
        'run_command' : 'python %s/driver.py' % AUTOGRADER_REL_PATH
    }
    #print json.dumps(package, indent=4, sort_keys=True)
    r = requests.post(URL, data = package)
