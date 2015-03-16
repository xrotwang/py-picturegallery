# Create offline browseable Galleries from flickr photos #

This package started out as a backup script I ran regularly to recover my photos stored on flickr.

```
./backup.py --cfg=/path/to/config
```
will crawl flickr for all sets and photos within sets in one account.

As a first extension, I created html pages to browse the backup.

Once the backup grew too big to fit on one cd, I had to come up with some scripts to create configurable portions of the backup. This is what this software does.

```
./gallery.py --cfg=/path/to/config --tags=skitour+karwendel --output=/tmp/skitour
```
will select all sets having at least one photo tagged with both "skitour" and "karwendel", copy the relevant photos to /tmp/skitour, and create pages to navigate the gallery.


## Requirements ##

The scripts require python >= 2.5, [sqlalchemy](http://sqlalchemy.org/) >= 0.4 and one of the following xslt processors (to create galleries from the backup):
  * [4Suite XML](http://4suite.org/index.xhtml)
  * [lxml](http://codespeak.net/lxml/)
  * xsltproc via system call

Note: The backup script does not require an xslt processor.

You need a [flickr api key](http://www.flickr.com/services/api/misc.api_keys.html) to use the flickr api client.


## Installation ##

Currently, you may only run the scripts from a svn checkout of the repository.


## Configuration ##

The configuration file should look as follows:
```
[system]
base_dir=/path/to/backup/dir
sqlite_db=/path/to/sqlite_db

[flickr]
user_name=
user_id=
api_key=
email=
password=
```


## Output ##

A screenshot of a page for a flickr set can be found [here](http://www.flickr.com/photos/xrotwang/3012540645/).


## Thanx ##

The following libraries come bundled with this package:
  * Jason Orendorff's path library,
  * James Clarke's flickr API client,
  * Thomas Fuchs' script.aculo.us,
  * Sam Stephenson's Prototype JavaScript framework,
  * Lokesh Dhakar's Lightbox v2.02,
  * Dusty Davidson's photonotes.