USAGE:
    driver.sh SRC_FOLDER_PATH

The src folder should have multiple directories; each directory should have a
python folder containing the python file. The python file should have a
unique name.

INDIVIDUAL USAGE:

    1. python lib/prepare.py PYTHON_FILE_PATH

        - Creates a folder called 'output' with a PYTHON_FILE_NAME folder
          inside of it. Inside this folder are several files:
            - driver.py
            - solution.py
            - seed.json
            - skeleton.py

    2. python lib/mutate.py output/PYTHON_FILE_NAME/seed.json

        - Creates a 'cases' folder in the PYTHON_FILE_NAME folder

    3. python lib/upload.py output/PYTHON_FILE_NAME/

        - Adapts the generated files to Kodethon's problem format
