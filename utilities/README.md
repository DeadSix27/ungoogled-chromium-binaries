# Utilities

Multiple utilities to help maintain the download pages of multiple authors.

The two main utilities you should worry about are:

`add_release_to_database.py` and `site_generator.py`

___

### `add_release_to_database.py` Usage Help

This utlity adds new releases to the JSON Database.

To add a new release call it like:

`add_release_to_database.py {version} {author} {platform} {platformVersion} {arch} {filename {...}}`

Where
* `version` is the Chromium version number (e.g 55.0.2883.87-1)
* `author` is the GitHub Username of the binary builder (e.g Eloston)
* `platform` is one of:
  * `macos`
  * `windows`
  * `linux_static`
  * `debian`
  * `ubuntu`
* `platformVersion` is one of:
	* `ubuntu1610`
	* `ubuntu1604`
	* `windows` 
	* `linux_static`
	* `debian90`
	* `macos`
* `arch` is either `i386` or `amd64`
* `filename {...}` is the list of files (e.g multiple .deb files or a single .zip, etc)

___

### `site_generator.py` Usage Help

To generate the HTML pages call it like:

`site_generator.py`

Basically all you have to do is run it, it will create index.html and archive pages(tbd) automatically in the CURRENT WORKING DIR.
This way you can review the index.html before you overwrite them.
