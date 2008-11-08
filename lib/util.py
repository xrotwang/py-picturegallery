from xml.etree import ElementTree as et

import path

def existing_dir(p):
    if not isinstance(p, path.path):
        p = path.path(p)
    if not p.exists():
        p.makedirs()
    return p

def create_element(tag, attrs=None, text=None, implementation=None):
    if implementation is None: implementation = et
    if attrs is None:
        attrs = {}
    e = implementation.Element(tag, attrs)
    if text is not None:
        e.text = text
    return e

def write_tree(tree, path, implementation=None):
    if implementation is None: implementation = et    
    if not hasattr(tree, 'write'):
        # we assume an element was passed as tree
        tree = implementation.ElementTree(tree)
    tree.write(path, 'utf-8')
    return path

def ascii(ustring):
    return ustring.encode('ascii', 'replace').replace('?', '_')

def file_uri(p): 
    if isinstance(p, str):
        p = path.path(p)
    return "file://%s" % p.abspath()

