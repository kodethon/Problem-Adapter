import bs4 
import pdb
import urllib2
import os

from google.cloud import storage

class HtmlProcessor():
    
    def __init__(self, language):
        self.language = language
        self.done = False
        self.history = []

        client = storage.Client()
        self.bucket_name = 'kodethon'
        self.bucket = client.get_bucket(self.bucket_name)
        self.bucket_folder_name = 'a6eb56f80be8a120436d6f1c9b8d87ca'
        self.bucket_host = 'https://storage.googleapis.com'

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
            if "brush: %s" % self.language not in class_names_str:
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

    def try_process_image(self, ele):
        if not ele.name == 'img': return False
        src = ele.get('src') 
        contents = urllib2.urlopen(src).read()
        path = os.path.join(self.bucket_folder_name, os.path.basename(src))
        blob = self.bucket.blob(path)
        blob.upload_from_string(contents)
        url = os.path.join(self.bucket_host, self.bucket_name, path)
        ele['src'] = url
        return True
            
