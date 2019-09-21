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

        filters = [self.script, self.external_references, self.responsiveTabsWrapper]
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
    
    def external_references(self, ele):
        if ele.name == 'p':
            return 'have discussed' in ele.text

    def practiceLinkDiv(self, ele):
        """
        Specific element that should be ignored
        """
        if not self.done:
            self.done = ele.get('id') == "practiceLinkDiv"

            if not self.done and ele.name == 'a':
                self.done = 'https://practice.geeksforgeeks.org' in ele.attrs['href']

        return self.done

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
            
