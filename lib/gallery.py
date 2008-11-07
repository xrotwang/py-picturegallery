#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
from tempfile import mkdtemp, mktemp
from ConfigParser import SafeConfigParser


from ePubTk.lib import fslib
from ePubTk.lib import xmllib
from ePubTk.lib.stringClasses import uString


from db import *
from config import BASE_DIR


SRC_DIR = fslib.Dir(BASE_DIR.join('lib'))

class VirtualSet(object):
    def __init__(self, id, title, description=None, photos=None):
        self.id = id
        self.title = title
        self.description = description
        if photos is None: photos = []
        self.photos = photos

    def md(self):
        d = xmllib.createDom('<rsp stat="ok"/>')
        setElement = xmllib.createElement(d, 'set', None, id=self.id)
        setElement.appendChild(xmllib.createElement(d, 'title', self.title))
        setElement.appendChild(xmllib.createElement(d, 'description', self.description))

        for photo in self.photos:
            setElement.appendChild(xmllib.createElement(d, 'photo', None, ref=photo.id))

        d.documentElement.appendChild(setElement)
        return d


def locations(set):
    d = xmllib.createDom('<set/>')
    for photo in set.photos:
        if photo.longitude is not None and photo.latitude is not None:
            attrs = dict(latitude=photo.latitude, 
                         longitude=photo.longitude, 
                         thumbnail='../../photos/%s/Thumbnail.jpg' % photo.id, 
                         locality='',
                         title=photo.title)
            d.documentElement.appendChild(xmllib.createElement(d, 'location', None, **attrs))
    return d


def gallery(cfg, options, set_spec=None):
    """
    copy photos, sets, virtual sets, ... to target_dir
    """
    if set_spec is None: set_spec = {}

    if options.output: 
        target_dir = fslib.Dir(options.output)
    else:
        target_dir = BASE_DIR

    if not target_dir.exists(): target_dir.mk()

    if options.tags:
        set_spec['tag'] = options.tags

    #photos = []
    sets = []

    if set_spec and 'tag' in set_spec:
        related = []
        #set = VirtualSet('v_tag_%s' % set_spec['tag'], 'Photos tagged with "%s"' % set_spec['tag'])
        for p in session.query(Photo).select():
            if set_spec['tag'] in [t.name for t in p.tags]:
                print p.id, p.title

                #if p not in photos: photos.append(p)

                for s in p.sets:
                    if s not in sets: sets.append(s)

                #set.photos.append(p)
                for t in p.tags:
                    if t.raw not in related:
                        related.append(t.raw)
        #sets.append(set)
        #print "related tags:", related
    if set_spec and 'geo' in set_spec:
        pass
    if set_spec and 'date' in set_spec:
        pass

    if set_spec is None:
        #
        # create pages for all sets and for all tags
        #
        for tag in session.query(Tag).select():
            related = {}
            set = VirtualSet('v_tag_%s' % uString(tag.name).ascii(), 'Photos tagged with "%s"' % tag.raw)
            for p in session.query(Photo).select():
                if tag in p.tags:
                    #print p.id, p.title
                    #if p not in photos: photos.append(p)
                    set.photos.append(p)
                    for t in p.tags:
                        if t != tag:
                            if t.name not in related:
                                related[t.name] = (t, 1)
                            else:
                                related[t.name] = (t, related[t.name][1]+1)
            set.related_tags = related
            sets.append(set)
            print related
        
        for set in session.query(Set).select():
            #for p in set.photos:
                #if p not in photos: photos.append(p)
            sets.append(set)

    #
    # write the selection of sets to a file to make it available for the xslt processing:
    #
    d = xmllib.createDom('<sets/>')
    for s in sets:
        d.documentElement.appendChild(xmllib.createElement(d, 'set', s.title, id=s.id))
    tmp = mktemp('.xml')
    xmllib.writeNode(d, outFile=tmp)
    
    xsl_params = dict(sets=fslib.File(tmp).uri(), lang=options.lang)

    #
    # now copy the photos:
    #
    source_dir = BASE_DIR

    target_dir = fslib.Dir(target_dir)
    if not target_dir.exists():
        target_dir.mk()

    for rscs in ['sets', 'photos', 'js', 'css', 'images']:
        rscs_dir = fslib.Dir(target_dir.join(rscs))
        if not rscs_dir.exists():
            rscs_dir.mk()
    
    for s in sets:
        for photo in s.photos:
            if not fslib.Dir(target_dir.join('photos', photo.id)).exists():
                photo.dir().copytree(target_dir.join('photos', photo.id))

            xmllib.xslt(photo.md(), 
                        fslib.Dir(SRC_DIR.join('xslt')).join('photo.xsl'), 
                        outFile=target_dir.join('photos', photo.id, 'index.html'),
                        params=xsl_params)

    for set in sets:
        if not fslib.Dir(target_dir.join('sets', set.id)).exists():
            fslib.Dir(target_dir.join('sets', set.id)).mk()

        if [p for p in set.photos if p.latitude]: map = True
        else: map = False

        xsl_params['map'] = map
        xmllib.xslt(set.md(), 
                    fslib.Dir(SRC_DIR.join('xslt')).join('set.xsl'), 
                    outFile=target_dir.join('sets', set.id, 'index.html'),
                    params=xsl_params)

        #
        # we have to provide a file locations.xml, too
        #
        if map:
            xmllib.writeNode(locations(set), 
                             outFile=target_dir.join('sets', set.id, 'locations.xml'))
   
    xsl_params['subtitle'] = str(set_spec)
    xmllib.xslt(xmllib.createDom('<r/>'), 
                fslib.Dir(SRC_DIR.join('xslt')).join('index.xsl'), 
                outFile=target_dir.join('index.html'),
                params=xsl_params)

    os.remove(tmp)
 
    #
    # copy the static resources:
    #
    for d in ['images', 'js', 'css']:
        fslib.Dir(SRC_DIR.join(d)).copyfiles(target_dir.join(d))    
    fslib.File(SRC_DIR.join('css', options.theme+'.css')).cp(target_dir.join('css', 'style.css'))

if __name__ == "__main__":
    usage = """usage: %prog [options]"""
    parser = OptionParser(usage=usage)    
    parser.add_option("-V", "--verbose", action="store_true", default=False)
    parser.add_option("-o", "--output", default=None)
    parser.add_option("", "--cfg", default='myflickr.cfg')
    parser.add_option("", "--tags", default=None)
    parser.add_option("", "--theme", default='default')
    parser.add_option("", "--lang", default='en')

    (options, args) = parser.parse_args()

    cfg = SafeConfigParser()
    try:
        cfg.read(options.cfg)
    except:
        parser.error("failed to read config file")
        sys.exit(0)

    gallery(cfg, options)
    sys.exit(0)
