AUTOMATED USAGE:

    sh adapt-all.sh FOLDER_PATH

The folder should have multiple directories; each directory should have a
python folder containing the python file. The python file should have a
unique name; it is advisable to name the file after the problem name.

INDIVIDUAL USAGE:

    sh adapt-one.sh DIR_PATH/PYTHON_FILE_NAME.py

MANUAL USAGE:

    1. python lib/prepare.py DIR_PATH/PYTHON_FILE_NAME.py

        - Creates a folder called 'output' with a PYTHON_FILE_NAME folder
          inside of it. Inside this folder are several files:
            - driver.py
            - solution.py
            - seed.json
            - skeleton.py

    2. python lib/mutate.py output/PYTHON_FILE_NAME

        - Creates a 'cases' folder in the PYTHON_FILE_NAME folder

    3. python lib/upload.py output/PYTHON_FILE_NAME

        - Adapts the generated files to Kodethon's problem format

SCRAPING AND PARSING:  
    scrape.py and parse.py must be in same directory. 

    SCRAPING:
        1. In scrape.py, edit pages variable to point to a dictionary of
        links, where the key is the subtopic and the value is a list of URLs.

        2. To scrape, call scrape_links and pass in the PAGES variable and the
        TOPIC as a string.
            - Generates directories to path 'raw/TOPIC/SUBTOPIC' (parallel to
              scrape.py and parse.py) and creates
              an HTML file for raw scraped HTML from each link.

    PARSING:
        1. In parse.py, change TOPIC to TOPIC used in scrape.py.

