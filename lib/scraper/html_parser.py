from bs4 import BeautifulSoup
import pdb
import os

class HtmlParser():
    
    def __init__(self, file_path):
        with open(path) as f:
            self.soup = BeautifulSoup(f, 'html.parser')

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
        self.with_output_path('output')

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

    def find_description(self):
        text = ''
        for tag in self.soup.findAll("div", class_="entry-content"):
            pdb.set_trace()
            text += tag.contents
            text +="\n"
        return text

    def find_solution(self):
        text = ''
        for i in self.soup.findAll('pre'):
            if 'class' not in i.attrs: # Check if tag object contains class attribute
                continue

            if 'python;' not in i['class'] and 'python3;' not in i['class']: # Check if class attribute has python string
                continue
            text += i.string.encode("utf-8")
        return text

    def write_description(self, description):
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path):
            self.create_problem_folder()

        o = open(os.path.join(folder_path, "description.txt"), "w")
        o.write(description.encode("utf-8"))
        o.close()

    def write_solution(self, solution):
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path):
            self.create_problem_folder()

        o = open(os.path.join(folder_path, self.problem_name + '.py'), 'w')
        o.write(solution.encode("utf-8"))
        o.close()

    def create_problem_folder(self):
        folder_path = self.problem_folder_path()
        if not os.path.exists(folder_path): # If folder for problem doesn't already exist
            os.makedirs(folder_path) # creates parent directories if necessary

    def problem_folder_path(self):
        return os.path.join(self.output_path, self.course_name, self.assignment_name, self.problem_name)


path = '/home/fuzzy/python-problems/raw/algorithm-analysis/greedy-algorithms/greedy-algorithms-set-1-activity-selection-problem.html'
parser = HtmlParser(path)
description = parser.find_description()
solution =  parser.find_solution()
parser.write_solution(solution)
parser.write_description(description)

a = 1

