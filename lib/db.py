"""
the database schema
"""
from uuid import uuid1
uuid = lambda: str(uuid1())

from sqlalchemy import *
import path


METADATA = MetaData()


photos_t = Table('photos', METADATA,
                 Column('id', String(), primary_key=True),
                 Column('title', Unicode()),
                 Column('description', Unicode(), nullable=True, default=None),
                 Column('longitude', Float(), nullable=True, default=None),
                 Column('latitude', Float(), nullable=True, default=None),
                 )

sets_t = Table('sets', METADATA,
               Column('id', String(), primary_key=True),
               Column('title', Unicode()),
               Column('description', Unicode(), nullable=True, default=None),
               )

tags_t = Table('tags', METADATA,
               Column('raw', Unicode(), primary_key=True),
               Column('name', Unicode()),
               )
photos_tags_t = Table('photos_tags', METADATA,
                      Column('photo_id', String(), ForeignKey('photos.id')),
                      Column('tag_raw', Unicode(), ForeignKey('tags.raw')),
                      )

photos_sets_t = Table('photo_set', METADATA,
                      Column('photo_id', String(), ForeignKey('photos.id')),
                      Column('set_id', String(), ForeignKey('sets.id')),
                      )

notes_t = Table('notes', METADATA,
                Column('id', String(36), default=uuid, primary_key=True),
                Column('photo_id', String(), ForeignKey('photos.id')),
                Column('text', Unicode()),
                Column('author', Unicode()),
                Column('left', Integer()),
                Column('top', Integer()),
                Column('width', Integer()),
                Column('height', Integer()),
                )

class Resource(object): pass
    def dir(self):
        return path.path(self.__class__.__name__.lower()+'s').joinpath(self.id)

    def md(self):
        return self.dir().joinpath('md.xml')

class Photo(Resource): pass
class Set(Resource): pass
class Tag(object): pass
class Note(object): pass

mapper(Set, sets_t)
mapper(Tag, tags_t)
mapper(Note, notes_t)

mapper(Photo, photos_t,
       properties={'notes': relation(Note, backref='photo'),
                   'sets': relation(Set, secondary=photos_sets_t, backref='photos'),
                   'tags': relation(Tag, secondary=photos_tags_t, backref='photos')})

def get_session(db_path):
    engine = create_engine('sqlite:///%s' % db_path)
    METADATA.bind = engine
    return create_session(bind_to=engine)
