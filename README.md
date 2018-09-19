## Description

A tool to convert single file python programs to a driver, stub code, solution, and test cases. These individual components make up a Kodethon problem. This repository also provides a script to optionally upload the problem to Kodethon's problem library.

## Program Format

The python programs have to be a single file with the driver code defined after the function definitions.

For example:
``` python
# Function definition(s)
def add(a, b):
    return a + b

# Driver code
add(1, 2)
```

## Usage

### Manual

#### Step 1 

```
python lib/prepare.py DIR_PATH/PYTHON_FILE_NAME.py
```

Creates a folder called 'output' with a PYTHON_FILE_NAME folder inside of it. 
The below files should be created in the folder:
- driver.py
- solution.py
- seed.json
- skeleton.py

#### Step 2 

``` 
python lib/mutate.py output/PYTHON_FILE_NAME
```

Creates a 'cases' folder in the PYTHON_FILE_NAME folder filled with generated test cases.


#### Step 3

```
python lib/upload.py output/PYTHON_FILE_NAME
```

Adapts the generated files to Kodethon's problem format.


### Automated

Automated usage does the same thing as the manual usage except less commands have to be run.

#### Batch
    
```
sh adapt-all.sh FOLDER_PATH
```

The folder should have multiple directories; each directory should have a
python folder containing the python file. The python file should have a
unique name; it is advisable to name the file after the problem name.

#### Individual

```
sh adapt-one.sh DIR_PATH/PYTHON_FILE_NAME.py
```

### Uploading

1. Rename and update config/credentials.yml.sample to
config/credentials.yml
2. Update the file accordingly
3. sh upload-category.sh FOLDER_PATH

The folder should contain the folders named after the problem

## Getting Programs (Optional)

The programs can either be manually written or scraped from an external source. 

### Scraping

scrape.py and parse.py must be in the same directory. 

#### Step 1
In scrape.py, edit pages variable to point to a dictionary of
links, where the key is the subtopic and the value is a list of URLs.

#### Step 2
To scrape, call scrape_links and pass in the PAGES variable and the
TOPIC as a string.
- Generates directories to path 'raw/TOPIC/SUBTOPIC' (parallel to
  scrape.py and parse.py) and creates
  an HTML file for raw scraped HTML from each link.

### Parsing

In parse.py, change TOPIC to the TOPIC used in scrape.py.

