#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
from tempfile import mkdtemp, mktemp
from ConfigParser import SafeConfigParser

try:
    #
    # we prefer the xslt processor of 4suite xml, because it handles python objects
    # as parameters.
    #
    from Ft.Xml import InputSource
    from Ft.Xml.Xslt import Processor
    from Ft.Xml import Domlette
    XSLT_PROVIDER = 'Ft'
    from xml.etree import ElementTree as et
except ImportError:
    try:
        #
        # as fallback, we can use the lxml xslt processor ...
        #
        from lxml import etree as et
        XSLT_PROVIDER = 'lxml'
    except ImportError:
        #
        # ... or even xsltproc via system call
        #
        from xml.etree import ElementTree as et
        XSLT_PROVIDER = 'xsltproc'

from lib import path
from lib.db import *
from lib import util
from lib.util import existing_dir, create_element, write_tree, ascii, file_uri

src_dir = path.path(util.__file__).splitpath()[0].splitpath()[0]


def xslt(src, sty, out, params, debug=False):
    """
    abstracts the interface to the xslt processor

    @param src: path to input document or C{None}
    @param sty: path to xsl transform
    @param out: output path
    @param params: a dictionary of stylesheet parameter
    """
    if debug:
        print src
        print sty
        print out
        print params

    if XSLT_PROVIDER == 'lxml':
        if src is None:
            src = et.fromstring('<r/>')
        else:
            src = et.parse(str(src))
        sty = et.XSLT(et.parse(str(sty)))
        for param in params: 
            # we need to quote input parameters manually:
            params[param] = "'%s'" % params[param].replace("'", '"')            
        res = str(sty(src, **params))
    elif XSLT_PROVIDER == 'Ft':
        def input(path): 
            if path is None:
                return InputSource.DefaultFactory.fromString('<r/>', 'http://example.com/')
            return InputSource.DefaultFactory.fromUri(file_uri(path))
        proc = Processor.Processor()
        proc.appendStylesheet(input(sty))
        if params is None: params = {}
        src = Domlette.NonvalidatingReader.parse(input(src))
        res = proc.runNode(src, src.baseURI, topLevelParams=params)
    else:
        # let's try our luck with xsltproc
        tmp = None
        if src is None:
            tmp = mktemp('.xml')
            f = file(tmp, 'w')
            f.write('<?xml version="1.0"?>\n<r/>')
            f.close()
            src = tmp

        quoted_params = []
        for param, value in params.items():
            if "'" in value and '"' in value:
                raise ValueError("stringparam contains both quote and double-quotes !")
            if isinstance(value, unicode):
                value = value.encode('utf8')
            if '"' in value:
                value = value.replace('"', r'\"')
            quoted_params.append((param, '"%s"' % value))
        quoted_params = ["--stringparam %s %s" % p for p in quoted_params]

        cmd = "xsltproc %s %s %s" % (' '.join(quoted_params), sty, src)
        if debug:
            print "running:", cmd
        res = os.popen(cmd).read()
        if tmp: os.remove(tmp)

    f = file(out, 'w')
    f.write(res)
    f.close()


class VirtualSet(object):
    def __init__(self, id, title, description=None, photos=None):
        self.id = id
        self.title = title
        self.description = description
        if photos is None: photos = []
        self.photos = photos

    def md(self):
        d = et.Element('rsp', {'stat': 'ok'})        
        set_e = et.Element('set', {'id': self.id})
        for attr in ['title', 'description']:
            set_e.append(create_element(attr, None, getattr(self, attr), et))
        for photo in self.photos:
            set_e.append(et.Element('photo', dict(ref=photo.id)))
        d.append(set_e)
        return d


def locations(set):
    """
    create an et.Element holding the information to create a map overlay
    with markers for photos in a set.
    """
    d = et.Element('set')
    for photo in set.photos:
        if photo.longitude is not None and photo.latitude is not None:
            attrs = dict(latitude="%s" % photo.latitude, 
                         longitude="%s" % photo.longitude, 
                         thumbnail='../../photos/%s/Thumbnail.jpg' % photo.id, 
                         locality='',
                         title=photo.title)
            d.append(et.Element('location', attrs))
    return d


def gallery(cfg, options):
    """
    create a gallery from sets

    the first step is selecting the sets, the second is copying the photos and
    creating the html pages from the photo metadata.
    """
    if options.debug:
        print "XSLT provider:", XSLT_PROVIDER

    base_dir = existing_dir(cfg.get('system', 'base_dir'))

    def _xslt(src, sty, out, params): 
        sty = src_dir.joinpath('xslt', options.theme, sty)
        if not sty.exists():
            sty = src_dir.joinpath('xslt', 'default', sty)
            print "missing transform %s for theme %s, falling back to default" % (sty, options.theme)
        xslt(src, sty, out, params, options.debug)
        if options.debug: print out, 'written'
        return

    if options.output: 
        target_dir = existing_dir(options.output)
    else:
        target_dir = base_dir

    sqlite_db = path.path(cfg.get('system', 'sqlite_db'))
    if not sqlite_db.exists():
        print """The database file %s does not exist.
You may have to run the backup script to create it.""" % sqlite_db
        sys.exit(256)
    session = get_session(sqlite_db.abspath())

    sets = []
    selection = ''

    if options.tags:
        print "selecting sets by tag"
        selection = "set tagged with %s" % options.tags

        operator = all
        tags = options.tags
        if ',' in tags:
            operator = any
            tags = filter(None, [t.strip() for t in tags.split(',')])
        elif '+' in tags:
            tags = filter(None, [t.strip() for t in tags.split('+')])
        else:
            tags = [tags]

        tags = [t.replace(':','') for t in tags]

        if options.verbose:
            print tags, operator

        related = []

        for p in session.query(Photo).select():
            p_tags = [t.name for t in p.tags]

            if operator([t in p_tags for t in tags]):
                for s in p.sets:
                    if s not in sets: 
                        sets.append(s)

                for t in p.tags:
                    if t.name not in related:
                        related.append(t.name)
        #
        # as a service for narrowing down a selection, we print out related tags
        #
        print "related tags:", related
    elif options.sets:
        print "selecting sets by title"
        selection = "sets where title contains %s" % options.sets
        query = options.sets.replace('%', '')
        for s in session.query(Set).select(Set.c.title.like('%'+query+'%')):
            sets.append(s)        
    else:
        #
        # create pages for all sets and for all tags
        #
        selection = 'all sets'
        for tag in session.query(Tag).select():
            related = {}
            s = VirtualSet('v_tag_%s' % ascii(tag.name), 'Photos tagged with "%s"' % tag.raw)
            for p in session.query(Photo).select():
                if tag in p.tags:
                    s.photos.append(p)
                    for t in p.tags:
                        if t != tag:
                            if t.name not in related:
                                related[t.name] = (t, 1)
                            else:
                                related[t.name] = (t, related[t.name][1]+1)
            s.related_tags = related
            sets.append(s)
        
        for s in session.query(Set).select():
            sets.append(s)

    sets = [s for s in sets if not s.title.startswith('favorites ')]

    #
    # write the selection of sets to a file to make it available for the xslt processing:
    #
    d = et.Element('sets', {'selection': selection, 'user_id': cfg.get('flickr', 'user_id')})
    for s in sets:
        d.append(create_element('set', dict(id=s.id), s.title, et))
    tmp_sets = mktemp('.xml')
    write_tree(d, tmp_sets, implementation=et)
    xsl_params = dict(sets=file_uri(tmp_sets), 
                      lang=options.lang,
                      user_name=cfg.get('flickr', 'user_name'))
    if options.metadata:
        xsl_params['metadata_file'] = str(path.path(options.metadata).abspath())


    #
    # now copy the data:
    #
    for rscs in ['sets', 'photos', 'js', 'css', 'images']:
        existing_dir(target_dir.joinpath(rscs))
   
    for s in sets:
        if options.verbose:
            print s.title

        for photo in s.photos:
            photo_dir = target_dir.joinpath('photos', photo.id)
            if not photo_dir.exists():
                path.path(base_dir.joinpath('photos', photo.id)).copytree(photo_dir)

            _xslt(base_dir.joinpath(photo.md()), 'photo.xsl', photo_dir.joinpath('index.html'), xsl_params)

        set_dir = existing_dir(target_dir.joinpath('sets', s.id))

        xsl_params['map'] = str([p for p in s.photos if p.latitude] != [])
        xsl_params['base_uri'] = file_uri(base_dir)
        _xslt(base_dir.joinpath(s.md()),  'set.xsl',  set_dir.joinpath('index.html'), xsl_params)

        #
        # we have to provide a file locations.xml, too
        #
        write_tree(locations(s), target_dir.joinpath('sets', s.id, 'locations.xml'), implementation=et)

    _xslt(None, 'index.xsl', target_dir.joinpath('index.html'), xsl_params)
    os.remove(tmp_sets)
  
    #
    # copy the static resources:
    #
    if not target_dir.joinpath('images').exists():
        src_dir.joinpath('images').copytree(target_dir.joinpath('images'))
    else:
        for f in filter(lambda p: p.isfile(), src_dir.joinpath('images').listdir()):
            f.copy(target_dir.joinpath('images', f.splitpath()[1]))

    for f in ['style.css', 'lightbox.css', 'photonotes.css']:
        p = src_dir.joinpath('css', options.theme, f)
        if p.exists():
            p.copy(target_dir.joinpath('css', f))
        else:
            src_dir.joinpath('css', f).copy(target_dir.joinpath('css', f))

    for f in ['effects.js', 'lightbox.js', 'map.js', 'photonotes.js', 'prototype.js', 'scriptaculous.js']:
        src_dir.joinpath('js', f).copy(target_dir.joinpath('js', f))


if __name__ == "__main__":
    usage = """usage: %prog [options]"""
    parser = OptionParser(usage=usage)    
    parser.add_option("-V", "--verbose", action="store_true", default=False)
    parser.add_option("", "--debug", action="store_true", default=False)
    parser.add_option("-o", "--output", default=None)
    parser.add_option("", "--cfg", default='myflickr.cfg')
    parser.add_option("", "--metadata", default=None)
    parser.add_option("", "--tags", default=None)
    parser.add_option("", "--sets", default=None)
    parser.add_option("", "--theme", default='default')
    parser.add_option("", "--lang", default='en')

    (options, args) = parser.parse_args()

    cfg = SafeConfigParser()
    try:
        cfg.read(options.cfg)
    except:
        parser.error("failed to read config file")
        sys.exit(0)

    if not src_dir.joinpath('css', options.theme, 'style.css').exists():
        parser.error("missing theme configuration")
        sys.exit(0)        

    if options.metadata and not path.path(options.metadata).exists():
        parser.error("can't find metadata file")
        sys.exit(0)        

    gallery(cfg, options)
    sys.exit(0)
