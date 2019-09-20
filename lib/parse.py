import sys
import os

from parse.html_parser import HtmlParser
from parse.html_processor import HtmlProcessor

if __name__ == "__main__":
    path = sys.argv[1]
    if os.path.isdir(path):
        print "%s is a directory." % path
        sys.exit(1)
    
    language = 'python'
    processor = HtmlProcessor(language)
    parser = HtmlParser(path, processor)
    
    #parser.update_file()
    metadata = parser.get_metadata()

    solution =  parser.find_solution()
    if not solution: 
        print 'Could not find solution.' 
        sys.exit(1)

    description = parser.find_description()
    if not description: 
        print 'Could not find description.'
        sys.exit(1)

    parser.write_metadata(metadata)
    parser.write_solution(solution)
    parser.write_description(description)
