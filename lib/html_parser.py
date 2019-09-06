import pdb
import os
import subprocess
import sys

import bs4
from markdownify import markdownify as md

class HtmlProcessor():
    
    def __init__(self, language):
        self.language = language
        self.done = False
        self.history = []

    def filterAny(self, ele):
        if not ele: return
        self.history.append(ele)
        if issubclass(type(ele), bs4.element.NavigableString): return # Includes bs4.element.Comment
        filters = [self.practiceLinkDiv, self.responsiveTabsWrapper, self.script, self.preHasSolution]
        
        for f in filters:
            if self.done or f(ele):
                ele.decompose()
                break

    def checkIfDone(self, ele):
        if self.done: return
        if not issubclass(type(ele), bs4.element.NavigableString): 
            self.done = 'References:' in ele.text
            if self.done: ele.decompose()

    def tryModifyLink(self, ele):
        """
        If is a link to main website, replace with span tag
        """
        if ele.name == 'a':
            href = ele.attrs['href']
            if not href: return
            if 'click here' in ele.text:
                ele.decompose()
            elif 'geeksforgeeks.org' in href:
                ele.name = 'span'
                del ele.attrs['href']

    def preHasSolution(self, ele):
        if ele.name != 'pre': return False
        class_names = ele.get('class')
        if not class_names: return
        class_names_str = ' '.join(ele.attrs['class'])
        if 'brush:' in class_names_str:
            if "brush: %s" % language not in class_names_str:
                return True
        return False

    def practiceLinkDiv(self, ele):
        """
        Specific element that should be ignored
        """
        return ele.get('id') == "practiceLinkDiv"

    def responsiveTabsWrapper(self, ele):
        """
        Wrapper for solution code
        """
        class_names = ele.get('class')
        if not class_names: return
        return 'responsive-tabs-wrapper' in class_names or 'responsive-tabs' in class_names

    def script(self, ele):
        return ele.name == "script"

class HtmlParser():
    
    def __init__(self, file_path, language):
        with open(file_path) as f:
            self.soup = bs4.BeautifulSoup(f, 'html.parser')

        self.file_path = path

        # Set problem name
        self.file_name = os.path.basename(path)
        self.with_problem_name(self.file_name.replace('.html', ''))
        
        # Set assignment name
        parent_path = os.path.dirname(path)
        self.with_assignment_name(os.path.basename(parent_path))

        # Set course name
        self.with_course_name(os.path.basename(os.path.dirname(parent_path))) 
        
        # Set default output path to current directory
        self.with_output_path('/tmp/kodethon-problems')
            
        self.language = language
        self.processor = HtmlProcessor(language)

    def language_to_extension(self, language):
        return {
            'python' : 'py',
            'java' : 'java',
            'c' : 'c'
        }[language]

    def language_variations(self, language):
        return {
            'python' : ['python', 'python3'],
            'java' : ['java'],
            'c' : ['c']
        }[language]

    def with_output_path(self, output_path):
        self.output_path = output_path
        return self

    def with_course_name(self, course_name):
        self.course_name = course_name
        return self

    def with_assignment_name(self, assignment_name):
        self.assignment_name = assignment_name
        return self

    def with_problem_name(self, problem_name):
        self.problem_name = problem_name
        return self

    def format_pre(self, ele):
        return unicode(ele).replace("\r", "").replace("\n", "  \n    ").replace("\\\\", "\\")

    def find_description(self):
        ele = self.soup.find("div", class_="entry-content")
        if not ele: return
        self.traverseElement(ele)

        return self.format_pre(ele)

    def traverseElement(self, root):
        for ele in root.children:
            self.processor.checkIfDone(ele)
            self.processor.filterAny(ele)
            self.processor.tryModifyLink(ele)
            if type(ele) is bs4.element.Tag:
                self.traverseElement(ele)

    def find_solution(self):
        text = ''
        for i in self.soup.findAll('pre'):
            if 'class' not in i.attrs: # Check if tag object contains class attribute
                continue
            
            variations = self.language_variations(self.language)
            language_found = False
            for variation in variations:
                language_found = ("%s;" % variation) in i['class']
                if language_found:
                    break
            if not language_found: continue # Check if class attribute has language string

            text += i.string.encode("utf-8")
        return text

    def write_description(self, description):
        """
        Writes 2 files, description.html and description.md in self.problem_folder_path
        """
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path):
            self.create_problem_folder()
        
        html_file_path = os.path.join(folder_path, "description.html")
        o = open(html_file_path, "w")
        o.write(description.encode("utf-8"))
        o.close()

        o = open(os.path.join(folder_path, "description.md"), "w")
        md = subprocess.check_output(['node', 'html_2_md.js', html_file_path])
        o.write(md)
        o.close()

    def write_solution(self, solution):
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path):
            self.create_problem_folder()
            
        extension = self.language_to_extension(self.language)
        o = open(os.path.join(folder_path, self.problem_name + '.' + extension), 'w')
        o.write(solution.encode("utf-8"))
        o.close()

    def create_problem_folder(self):
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path): # If folder for problem doesn't already exist
            os.makedirs(folder_path) # creates parent directories if necessary

    def problem_folder_path(self):
        return os.path.join(self.output_path, self.course_name, self.assignment_name, self.problem_name)

if __name__ == "__main__":
    path = sys.argv[1]
    language = 'python'
    #path = '/home/fuzzy/test/raw/algorithm-analysis/greedy-algorithms/greedy-algorithms-set-1-activity-selection-problem.html'
    parser = HtmlParser(path, language)

    solution =  parser.find_solution()
    if not solution: sys.exit(1)

    description = parser.find_description()
    if not description: sys.exit(1)
    
    parser.write_solution(solution)
    parser.write_description(description)
