# Usage

## Automated Usage:

### Batch Usage:
    
```
sh adapt-all.sh FOLDER_PATH
```

The folder should have multiple directories; each directory should have a
python folder containing the python file. The python file should have a
unique name; it is advisable to name the file after the problem name.

### Individual Usage:

```
sh adapt-one.sh DIR_PATH/PYTHON_FILE_NAME.py
```

## Manual Usage:

1. Create a folder called 'output' with a PYTHON_FILE_NAME folder inside of it. 

```
python lib/prepare.py DIR_PATH/PYTHON_FILE_NAME.py
```

The below files should be created in the folder:
    - driver.py
    - solution.py
    - seed.json
    - skeleton.py

2. Create a 'cases' folder in the PYTHON_FILE_NAME folder filled with generated test cases.

``` 
python lib/mutate.py output/PYTHON_FILE_NAME
```

3. Adapt the generated files to Kodethon's problem format.

```
python lib/upload.py output/PYTHON_FILE_NAME
```

### Uploading:

1. Rename and update config/credentials.yml.sample to
config/credentials.yml
2. Update the file accordingly
3. sh upload-category.sh FOLDER_PATH

The folder should contain the folders named after the problem

## Getting the Programs

scrape.py and parse.py must be in same directory. 

### Scraping

1. In scrape.py, edit pages variable to point to a dictionary of
links, where the key is the subtopic and the value is a list of URLs.

2. To scrape, call scrape_links and pass in the PAGES variable and the
TOPIC as a string.
    - Generates directories to path 'raw/TOPIC/SUBTOPIC' (parallel to
      scrape.py and parse.py) and creates
      an HTML file for raw scraped HTML from each link.

### Parsing

1. In parse.py, change TOPIC to TOPIC used in scrape.py.

