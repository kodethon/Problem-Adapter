import pdb
import os
import subprocess
import sys
import urllib2
import bs4
import shutil
import datetime
import json
from markdownify import markdownify as md

class HtmlProcessor():
    
    def __init__(self, language):
        self.language = language
        self.done = False
        self.history = []

    def check_if_done(self, ele):
        if not ele: return False
        if self.done: return False

        if not self.is_tag(ele): return False

        filters = [self.practiceLinkDiv, self.references_ele]
        for f in filters:
            if f(ele):
                return True
        return False

    def filter(self, ele):
        if not ele: return False
        if self.done: return False
        if not self.is_tag(ele): return False

        filters = [self.script, self.preHasSolution, self.responsiveTabsWrapper]
        for f in filters:
            if f(ele):
                self.remove_element(ele)
                return True
        return False

    def is_tag(self, ele):
        # Includes bs4.element.Comment
        return not issubclass(type(ele), bs4.element.NavigableString) and type(ele) == bs4.element.Tag

    def remove_element(self, ele):
        if self.is_tag(ele):
            ele.decompose()
        else:   
            try:
                ele.replace_with('')
            except Exception as e:
                # May already have been removed due .decompose being called on parent
                pass

    def references_ele(self, ele):
        if not self.done:
            self.done = 'References:' in ele.text
        return self.done

    def try_modify_link(self, ele):
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
        if not class_names: return False
        class_names_str = ' '.join(ele.attrs['class'])
        if 'brush:' in class_names_str:
            if "brush: %s" % language not in class_names_str:
                self.removeSolutionTitle()
                return True
        return False

    def removeSolutionTitle(self):
        """
        A solution is generally accompanied by a title that references it.
        It should have phrases such as, The following..., Following..., Below..., Shown...
        """
        cur = len(self.history) - 1
        title_words = ['Following', 'Below']
        follow_up_words = ['following', 'below']
        while cur >= 0: 
            ele = self.history[cur]
            if type(ele) != bs4.element.NavigableString:
                cur -= 1
                continue
            
            toks = ele.strip().split(' ')
            if len(toks) == 1: 
                cur -= 1
                continue
 
            capital_letters_count = 0
            has_period = False
            has_colon = False
            has_title_word = False

            i = 0
            for tok in toks:
                if len(tok) == 0: continue
                if i == 0:
                    has_title_word = tok in title_words

                if i == 1 and not has_title_word:
                    has_title_word = tok in follow_up_words

                if tok == '.':
                    has_period = True 
                elif tok[-1] == ':':
                    has_colon = True
                elif tok[0].isupper():
                    capital_letters_count += 1

                i += 1
            
            if capital_letters_count > 1 or not has_period or has_title_word:
                ele.replace_with('')
            
            # This is a title, stop here
            if capital_letters_count > 1: break


    def practiceLinkDiv(self, ele):
        """
        Specific element that should be ignored
        """
        if not self.done:
            self.done = ele.get('id') == "practiceLinkDiv"
        return ele.get('id') == "practiceLinkDiv"

    def responsiveTabsWrapper(self, ele):
        """
        Wrapper for solution code
        """
        if not ele: return False
        class_names = ele.get('class')
        if not class_names: return False
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

    def update_file(self):
        # Searach for file URL
        ele = self.soup.find("meta", {'property': 'og:url'})
        url = ele.attrs['content']
        contents = urllib2.urlopen(url).read()
        
        # Move current copy to a backup version
        current_time = str(datetime.datetime.now())
        current_time = '-'.join(current_time.split(' '))
        backup_folder = os.path.join(os.path.dirname(self.file_path), 'backup')
        if not os.path.exists(backup_folder):
            os.mkdir(backup_folder)
        new_path = os.path.join(backup_folder, "%s.%s" % (self.file_name, current_time))
        shutil.move(self.file_path, new_path)
            
        # Create new copy of the file
        fp = open(self.file_path, 'w')
        fp.write(contents)
        fp.close()

    def get_metadata(self):
        metadata = {}
        ele = self.soup.find("span", {'id': 'rating_box'})
        if not ele:
            print 'Could not find rating.'
            return
        difficulty = float(ele.text.strip())
        metadata['difficulty'] = difficulty

        ele = self.soup.find("meta", {'property': 'og:url'})
        url = ele.attrs['content']
        ele = self.soup.find('a', {'href': url})
        title = ele.text
        if '|' in title:
            title = title.split('|')[0].strip()
        metadata['title'] = title.strip()
        
        variations = self.language_variations(self.language)
        for variation in variations:
            ele = self.soup.find('pre', {'class': "%s;" % variation})
            if not ele:
                continue
            else:
                metadata['language'] = variation
                break
        return metadata
        
    def write_metadata(self, metadata):
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path):
            self.create_problem_folder()
        
        json_file_path = os.path.join(folder_path, "metadata.json")
        o = open(json_file_path, "w")
        o.write(json.dumps(metadata).encode("utf-8"))
        o.close()

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
        elements = []
        self.traverse_element(ele, elements)

        for root in elements:
            self.processor.remove_element(root) 

        return self.format_pre(ele)

    def traverse_element(self, root, elements):
        self.processor.history.append(root)
        self.processor.check_if_done(root)
        filtered = self.processor.filter(root)
        if not filtered: self.processor.try_modify_link(root)

        if self.processor.done:
            elements.append(root) 

        if type(root) is bs4.element.Tag:
            for ele in root.children:
                self.traverse_element(ele, elements)

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
    if os.path.isdir(path):
        print "%s is a directory." % path
        sys.exit(1)

    language = 'python'
    parser = HtmlParser(path, language)

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
