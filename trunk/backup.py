#!/usr/bin/env python
"""
script to backup data from a flickr account to local disc.

backs up images and metadata in the filesystem and additionally stores
the metadata in a sqlite database for easier access.

we back up the data from flickr using the following directory layout:

base_dir
|-- photos
|   `-- <id>
|       |-- Large.jpg
|       |-- Medium.jpg
|       |-- Original.jpg
|       |-- Small.jpg
|       |-- Square.jpg
|       |-- Thumbnail.jpg
|       `-- md.xml
...
`-- sets
    |-- <id>
    |   `-- md.xml
...

"""
import sys
import urllib
import time
import re
from optparse import OptionParser
from xml.etree import ElementTree as et
from ConfigParser import SafeConfigParser

# third party modules:
import flickr
import path

# import the db schema
from lib.db import METADATA, get_session, Photo, Set, Tag, Note
from lib.util import existing_dir, write_tree, create_element


def backup(cfg, options):
    """
    backup all photos to disk
    """
    myself = flickr.User(cfg.get('flickr', 'user_id'))

    photo_ids = []
    set_ids = []

    base_dir = existing_dir(cfg.get('system', 'base_dir'))

    print "retrieving data from flickr ..."

    #
    # since backups may take a long time, and hence run a chance of being incomplete,
    # we try to reverse the backup order every once in a while.
    #
    sets = myself.getPhotosets()
    if int(round(time.time())%2): sets = reversed(sets)

    for set in sets:
        if options.set_id and options.set_id != set.id: continue

        if options.verbose: print "set =>", set.title, set.id

        set_dir = existing_dir(base_dir.joinpath('sets', str(set.id)))

        set_md_set = et.Element('set', {'id': set.id})
        for attr in ['title', 'description']:
            set_md_set.append(create_element(attr, None, getattr(set, attr)))

        for id, photo in set.getPhotos():
            if not options.sets_only:
                photo_dir = existing_dir(base_dir.joinpath('photos', str(photo.id)))

                if options.verbose: print "photo =>", photo.title, photo.id
                
                md = et.fromstring(getPhotoInfo(id))
                if md.get('stat') != 'ok': raise ValueError('status of flickr request not ok')

                photo_element = md.find('photo')
                if photo_element is None: raise ValueError('no photo element found')
                
                #
                # we enrich the photo metadata from flickr with data about the available
                # image sizes.
                #
                sizes_element = et.Element('sizes')

                for size in ['Square', 'Thumbnail', 'Small', 'Medium', 'Large', 'Original']:
                    target = photo_dir.joinpath('%s.jpg' % size)
                    try:
                        source = photo.getURL(size=size, urlType='source')
                        #
                        # note: we only retrieve the image if it doesn't exist!
                        # this may not be what you want, if you happen to edit images
                        # on flickr.
                        #
                        if not target.exists():
                            try:
                                urllib.urlretrieve(source, target)
                                if options.verbose: print "retrieved %s, size %s" % (photo.id, size)
                            except:
                                print "failed to retrieve %s, size %s" % (photo.id, size)
                    except flickr.FlickrError:
                        print "failed to determine image url for %s, size %s" % (photo.id, size)

                    if target.exists():
                        sizes_element.append(et.Element('size', dict(name=size, url=source)))

                photo_element.append(sizes_element)                
                p = write_tree(md, photo_dir.joinpath('md.xml')) 
                if options.verbose: print p, "written"
                if photo.id not in photo_ids: photo_ids.append(photo.id)

            set_md_set.append(et.Element('photo', {'ref': photo.id}))

        set_md_root = et.Element('rsp', {'stat':'ok'})
        set_md_root.append(set_md_set)

        p = write_tree(set_md_root, set_dir.joinpath('md.xml'))
        if options.verbose: print p, "written"
        set_ids.append(set.id)

    print "... finished: backed up %s photos in %s sets.\n" % (len(photo_ids), len(set_ids))


def getPhotoInfo(id):
    url = '%s%s/?api_key=%s&method=%s&%s'% \
          (flickr.HOST, flickr.API, flickr.API_KEY, 'flickr.photos.getInfo', 
           urllib.urlencode(dict(photo_id=id, email=flickr.email, password=flickr.password)))
    return urllib.urlopen(url).read()


def recreate_db(cfg, options):
    print "recreating db ..."

    base_dir = path.path(cfg.get('system', 'base_dir'))
    sqlite_db = path.path(cfg.get('system', 'sqlite_db'))
    sqlite_db.copy(sqlite_db+'.bak')

    session = get_session(sqlite_db.abspath())
    
    METADATA.drop_all()
    session.flush()
    METADATA.create_all()
    session.flush()

    photos = {}
    tags = {}

    for rsc_class in [Photo, Set]:
        rsc_type = rsc_class.__name__.lower()
        rscsDir = base_dir.joinpath(rsc_type+'s')

        for rsc in rscsDir.listdir():
            rscMd = rscsDir.joinpath(rsc, 'md.xml')
            if not rscMd.exists():
                if re.match('[0-9]+$', rsc): raise ValueError('no md for %s %s' % (rsc_type, rsc))
            else:
                try:
                    element = et.parse(rscMd).find(rsc_type)
                except:
                    print rscMd
                    raise

                new = rsc_class()
                new.id = element.get('id')
                new.title = element.find('title').text
                
                desc = element.find('description')
                if desc is not None:
                    new.description = desc.text

                if rsc_type == 'photo':
                    photos[element.get('id')] = new

                    location = element.find('location')
                    if location is not None:
                        new.latitude = float(location.get('latitude'))
                        new.longitude = float(location.get('longitude'))
                    
                    session.save(new)
                    session.flush()

                    for t in element.findall('.//tag'):
                        if t.attrib['raw'] not in tags:
                            tag = Tag()
                            tag.raw = t.attrib['raw']
                            tag.name = t.text
                            session.save(tag)
                            session.flush()
                            tags[t.attrib['raw']] = tag
                        else:
                            tag = tags[t.attrib['raw']]
                            
                        new.tags.append(tag)

                    for n in element.findall('.//note'):
                        note = Note()
                        note.photo_id = new.id
                        note.text = n.text
                        note.author = n.attrib['authorname']
                        #
                        # note: we multiply the pixel-values to work with the medium sized images.
                        #
                        note.left = 2*int(n.attrib['x'])
                        note.top = 2*int(n.attrib['y'])
                        note.width = 2*int(n.attrib['w'])
                        note.height = 2*int(n.attrib['h'])

                        session.save(note)
                        session.flush()

                elif rsc_type == 'set':
                    session.save(new)
                    session.flush()

                    for p in element.findall('photo'): 
                        new.photos.append(photos[p.attrib['ref']])

    session.flush()
    print "... finished: %s photos in %s sets" % (len(session.query(Photo).select()),
                                                  len(session.query(Set).select()))
                

if __name__ == "__main__":
    usage = """usage: %prog [options] [PHOTO_ID]"""
    parser = OptionParser(usage=usage)    
    parser.add_option("-V", "--verbose", action="store_true", default=False)
    parser.add_option("", "--cfg", default='myflickr.cfg')
    parser.add_option("", "--sets-only", action="store_true", default=False)
    parser.add_option("", "--set-id", default=None)
    parser.add_option("", "--db-only", action="store_true", default=False, 
                      help='only recreate the sqlite db from the flickr metadata')

    (options, args) = parser.parse_args()

    cfg = SafeConfigParser()
    try:
        cfg.read(options.cfg)
    except:
        parser.error("failed to read config file")
        sys.exit(0)

    #
    # set the credentials for the flickr api client:
    #
    flickr.API_KEY = cfg.get('flickr', 'api_key')
    flickr.email = cfg.get('flickr', 'email')
    flickr.password = cfg.get('flickr', 'password')

    if args:
        print getPhotoInfo(args[0])
        sys.exit(0)

    if not options.db_only:
        backup(cfg, options)

    recreate_db(cfg, options)
    sys.exit(0)
