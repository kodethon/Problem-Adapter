import sys
import os
import logging
import json
import requests
import base64
import pdb
import yaml
import subprocess

from termcolor import colored

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DESCRIPTION_FILE_ALT = 'description.txt'
DESCRIPTION_FILE = 'description.md'
CASES_FOLDER = 'cases'
USER_ID_ENV = 'KODETHON_USER_ID'
ACCESS_TOKEN_ENV = 'KODETHON_ACCESS_TOKEN'
ASSIGNMENT_ID_ENV = 'KODETHON_ASSIGNMENT_ID'
PROBLEM_CATEGORY = 'KODETHON_PROBLEM_CATEGORY'
HOST='https://kodethon.com:8080'
IMPORT_URL = HOST + '/course/tests/import'
UPLOAD_URL = HOST + '/file/upload'

PYTHON3_MARKER = '__PYTHON3__'
AUTOGRADER_REL_PATH = '../autograder'
HANDOUT_FOLDER = 'handout'
CASES_ZIP = 'cases.zip'
DRIVER_FILE = 'driver.py'
MAIN_FILE = 'solution.py'
SKELETON_FILE = 'skeleton.py'
SOLUTION_FILE = 'solution.py'
SEED_FILE = 'seed.json'
SUBMISSION_FOLDER = 'submission'
REFERENCE_FOLDER = '.ref'

with open("config/credentials.yml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        logger.error(exc)

def isPython3(file_path):
    return os.path.exists(os.path.join(file_path, PYTHON3_MARKER))

def beautifyTitle(title):
    title = title.replace('-', ' ')
    return title.title()

def generateCases(cases_path, answers_path):
    # Generate all the cases
    cases = []
    for filename in os.listdir(cases_path):
        fp = open(os.path.join(answers_path, filename), 'r')
        answer = fp.read()
        fp.close()
        cases.append({
            'argument' : "%s %s" % (MAIN_FILE, os.path.join(AUTOGRADER_REL_PATH, CASES_FOLDER, filename)),
            'answer' : answer
        })
    return cases

def createTest(test):
    package = {
        'user_id' : config[USER_ID_ENV],
        'access_token' : config[ACCESS_TOKEN_ENV],
        'name' : config[ASSIGNMENT_ID_ENV],
        'test_settings'  : json.dumps(test),
    }
    #print json.dumps(package, indent=4, sort_keys=True)
    r = requests.post(IMPORT_URL, data = package)
    if not r.ok:
        logger.debug(colored(r.content, 'red'))

def uploadCases(title, dirpath):
    fp = open(os.path.join(dirpath, CASES_ZIP), 'r')
    content = fp.read()

    fp.close()
    file_path = os.path.join('/', title, os.path.basename(AUTOGRADER_REL_PATH))
    package = {
        'user_id' : config[USER_ID_ENV],
        'access_token' : config[ACCESS_TOKEN_ENV],
        'name' : config[ASSIGNMENT_ID_ENV],       
        'file_name' : CASES_ZIP,
        'file_path' : file_path,
        'file_content' : base64.b64encode(content)
    }
    logger.info(colored("Uploading %s" % file_path, 'green'))
    r = requests.post(UPLOAD_URL, data = package)
    if not r.ok:
        logger.debug(colored(r.content, 'red'))

def uploadDriverFile(title, dirpath):
    fp = open(os.path.join(dirpath, DRIVER_FILE), 'r')
    content = fp.read()
    fp.close()

    file_path = os.path.join('/', title, os.path.basename(AUTOGRADER_REL_PATH))
    package = {
        'user_id' : config[USER_ID_ENV],
        'access_token' : config[ACCESS_TOKEN_ENV],
        'name' : config[ASSIGNMENT_ID_ENV],       
        'file_name' : DRIVER_FILE,
        'file_path' : file_path,
        'file_content' : base64.b64encode(content),
        'overwrite' : True
    }
    logger.info(colored("Uploading %s" % file_path, 'green'))
    r = requests.post(UPLOAD_URL, data = package)
    if not r.ok:
        logger.debug(colored(r.content, 'red'))

def uploadSkeletonFile(title, dirpath):
    fp = open(os.path.join(dirpath, SKELETON_FILE), 'r')
    content = fp.read()
    fp.close()

    file_path = os.path.join('/', title, os.path.basename(HANDOUT_FOLDER))
    package = {
        'user_id' : config[USER_ID_ENV],
        'access_token' : config[ACCESS_TOKEN_ENV],
        'name' : config[ASSIGNMENT_ID_ENV],       
        'file_name' : MAIN_FILE,
        'file_path' : file_path,
        'file_content' : base64.b64encode(content),
        'overwrite' : True
    }
    logger.info(colored("Uploading %s" % file_path, 'green'))
    r = requests.post(UPLOAD_URL, data = package)
    if not r.ok:
        logger.debug(colored(r.content, 'red'))

def uploadSolutionFile(title, dirpath):
    fp = open(os.path.join(dirpath, SOLUTION_FILE), 'r')
    content = fp.read()
    fp.close()

    file_path = os.path.join('/', title, os.path.basename(SUBMISSION_FOLDER))
    package = {
        'user_id' : config[USER_ID_ENV],
        'access_token' : config[ACCESS_TOKEN_ENV],
        'name' : config[ASSIGNMENT_ID_ENV],       
        'file_name' : MAIN_FILE,
        'file_path' : file_path,
        'file_content' : base64.b64encode(content),
        'overwrite' : True
    }
    logger.info(colored("Uploading %s" % file_path, 'green'))
    r = requests.post(UPLOAD_URL, data = package)
    if not r.ok:
        logger.debug(colored(r.content, 'red'))

def uploadReferenceFile(title, dirpath):
    fp = open(os.path.join(dirpath, SOLUTION_FILE), 'r')
    content = fp.read()
    fp.close()

    file_path = os.path.join('/', title, REFERENCE_FOLDER)
    package = {
        'user_id' : config[USER_ID_ENV],
        'access_token' : config[ACCESS_TOKEN_ENV],
        'name' : config[ASSIGNMENT_ID_ENV],       
        'file_name' : MAIN_FILE,
        'file_path' : file_path,
        'file_content' : base64.b64encode(content),
        'overwrite' : True
    }
    logger.info(colored("Uploading %s" % file_path, 'green'))
    r = requests.post(UPLOAD_URL, data = package)
    if not r.ok:
        logger.debug(colored(r.content, 'red'))

def uploadFiles(dirpath):
    dirname = os.path.basename(dirpath)
    title = beautifyTitle(dirname)   

    # Upload cases
    uploadCases(title, dirpath)
    
    # Upload driver file
    uploadDriverFile(title, dirpath)

    # Upload skeleton file
    uploadSkeletonFile(title, dirpath) 

    # Upload solution file
    uploadSolutionFile(title, dirpath) 

    # Upload reference file
    uploadReferenceFile(title, dirpath) 

def append_sample_input_output(description, dir_path):
    # Run the solution
    interpreter = 'python3' if isPython3(file_path) else 'python'
    command = "cd %s; %s driver.py %s %s" % (dir_path, interpreter, SOLUTION_FILE, SEED_FILE)
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = res.stderr.read() 
    if len(stderr):
        raise Exception(stderr)

    _output = res.stdout.read()

    fp = open(os.path.join(dir_path, SEED_FILE), 'r') 
    _input = fp.read()
    fp.close()

    description += "<br>"
    description += "Function Arguments:\n<pre>\n%s</pre>" % _input
    description += "<br>Progam Output:\n<pre>\n%s</pre>" % _output
    return description

if __name__ == "__main__":
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        logger.error("%s does not exist!" % file_path)
        sys.exit()

    if not os.path.isdir(file_path):
        logger.error("%s must be a directory!" % file_path)
        sys.exit()

    if file_path[len(file_path) - 1] != '/':
        file_path += '/'

    if USER_ID_ENV not in config:
        logger.error("%s is not set." % USER_ID_ENV)
        sys.exit()

    if ACCESS_TOKEN_ENV not in config:
        logger.error("%s is not set." % ACCESS_TOKEN_ENV)
        sys.exit()

    if ASSIGNMENT_ID_ENV not in config:
        logger.error("%s is not set." % ASSIGNMENT_ID_ENV)
        sys.exit()

    logger.info(colored('Uploading %s...' % file_path, 'cyan'))

    dir_path = os.path.dirname(file_path)
    description_path = os.path.join(dir_path, DESCRIPTION_FILE)
    if not os.path.exists(description_path):
        description_path = os.path.join(dir_path, DESCRIPTION_FILE_ALT)
        if not os.path.exists(description_path):
            logger.error("%s does not exist!" % description_path)
            sys.exit()

    fp = open(description_path, 'r')
    description = fp.read().strip()
    fp.close()
    description = append_sample_input_output(description, dir_path)

    cases_path = os.path.join(dir_path, CASES_FOLDER)
    if not os.path.exists(cases_path):
        logger.error("%s does not exist!" % cases_path)
        sys.exit()

    answers_path = os.path.join(dir_path, 'answers')
    if not os.path.exists(answers_path):
        logger.error("%s does not exist!" % answers_path)
        sys.exit()
        
    cases = generateCases(cases_path, answers_path)
    dirname = os.path.basename(dir_path)
    interpreter = 'python3' if isPython3(file_path) else 'python'
    createTest({
        'test_name': beautifyTitle(dirname),
        'cases' : cases,
        'Style' : 'Diff',
        'Description' : description,
        'Run Command' : '%s %s/%s' % (interpreter, AUTOGRADER_REL_PATH, DRIVER_FILE),
        'Ignore Whitespace' : 'All',
        'Category' : config[PROBLEM_CATEGORY],
        'Use Reference Program': True
    }) 
    uploadFiles(dir_path)
