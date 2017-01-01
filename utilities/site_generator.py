#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# ungoogled-chromium-binaries: Concerns prebuilt versions of ungoogled-chromium
# Copyright (C) 2016  ungoogled-software contributors
#
# This file is part of ungoogled-chromium-binaries.
#
# ungoogled-chromium-binaries is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ungoogled-chromium-binaries is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ungoogled-chromium-binaries.  If not, see <http://www.gnu.org/licenses/>.

'''
	Generates the website files
'''
# Imports

import os,os.path,pprint,json,sys,mimetypes
from collections import OrderedDict

# Settings
_DATABASE_FILE = "../config/release_list.json"
_LATEST_STABLE_FILE = "../config/latest_stable.json"
_IGNORE_EXTENSION_LIST = ["changes","buildinfo"]
_ARCH_FRIENDLY_NAME = { "i386" : "32-Bit", "amd64" : "64-Bit" }
_INDEX_TEMPLATE = "../config/page_templates/index_template.html"
_OUTPUT_FOLDER = "."


# Site template parts

indexTemplate = ""
with open(_INDEX_TEMPLATE, 'r') as inf:
    indexTemplate = inf.read()

platFormContainerTemplate = '''
<div class="platformContainer">
	<span class="platFormHeader">{platform_name}</span>
	{platform_version_container_template}
</div>
'''
platformVersionContainerTemplate = '''
<div class="platformVersionContainer">
	<div class="platformVersionHeader">{platform_version_header}</div>
	{release_container_template}
</div>
'''
releaseContainerTemplate = '''
<div class="releaseContainer">
	<div class="authorGroup">
		<div class="head">Built by <a href="https://github.com/{author}">{author}</a></div>
		{arch_container_list}
	</div>
</div>
'''
archContainerTemplate = '''
<div class="archContainer">
	<div class="archHeader">{bitness}</a></div>
	{release_list}
</div>
'''
releaseTemplate = '''
<div class="release">
	<div class="title"><span>{release_title}</span></div>
	<div class="link"><a href="{href_link}">{release_file_name} <i class="fa fa-download" aria-hidden="true"></i></a></div>
</div>
'''
#Archive template


# Main functions


def errorOut(msg):
	print(msg, file=sys.stderr)
	sys.exit(0)

def create_platform_name(p):
	platforms = { 
		"macos"        : ("fa-apple"   , "OS X"),
		"windows"      : ("fa-windows" , "Windows"),
		"linux_static" : ("fl-tux"     , "Linux static"),
		"debian"       : ("fl-debian"  , "Debian"), # tbd: replace with proper debian icon
		"ubuntu"       : ("fl-ubuntu"  , "Ubuntu")  # tbd: replace with proper ubuntu icon
	}
	if p in platforms:
		p = platforms[p]
	else:
		errorOut("Unknown Platform")
	return '<i class="fa {picon}" aria-hidden="true"></i> {pname}'.format(picon=p[0],pname=p[1])
	
def create_platform_version(p):
	platformVers = { 
		"ubuntu1610"   : "Yakkety (16.10)",
		"ubuntu1604"   : "Xenial (16.04)",
		"windows"      : "Windows 10/8.1/8/7",
		"linux_static" : "Linux static",
		"debian90"     : "9.0 (stretch)",
		"macos"        : "Mac OS X 10.9 or later"
	}
	if p in platformVers:
		p = platformVers[p]
	else:
		errorOut("Unknown Platform Version")
	return p

def create_title_by_filename(f):
	ext = os.path.splitext(f)[1][1:]
	platformVers = { 
		"deb"       : "Debian Package",
		"dmg"       : "OS X Package",
		"msi"       : "Windows Installer (msi)",
		"exe"       : "Windows Installer",
		"zip"       : "Archive (zip)",
		"7z"        : "Archive (7z)",
		"xz"        : "Archive (xz)"
	}
	if ext in platformVers:
		ext = platformVers[ext]
	else:
		errorOut("Unknown filetype: " + ext)
	return ext

def read_database():
	db = None
	ls = None
	with open(_LATEST_STABLE_FILE,"r") as lSfileobj:
		ls = json.load(lSfileobj, object_pairs_hook=OrderedDict)
	with open(_DATABASE_FILE,"r") as dBfileobj:
		db = json.load(dBfileobj, object_pairs_hook=OrderedDict)
		
		verDict = db["releases"]
		
		sortedVerDict = OrderedDict()
		sortedVerList = sorted(db["releases"].keys(),key= lambda s: list(map(int, s.replace("-",".").split('.'))),reverse=True)
		
		for ver in sortedVerList:
			sortedVerDict[ver] = verDict[ver]
		
		db["releases"] = sortedVerDict
		
		# dbRelasesSorted = OrderedDict(sorted(db["releases"].keys(),))
		# dbRelasesSorted = OrderedDict(sorted(db["releases"].keys(),key= lambda s: list(map(int, s.replace("-",".").split('.')))))
		
		# db["releases"] = dbRelasesSorted
		
		# print(next (iter (db["releases"].keys())))
		
		# vers = db["releases"]
		
		# vers = vers.fromkeys(sorted(vers.keys(),key= lambda s: list(map(int, s.replace("-",".").split('.')))))
		# db["releases"] = vers
		# print(next (iter (db["releases"].keys())))
	return (db,ls)

def generate_main_index(db,ls): # Reads the database and builds an html landing/index page, looks confusing, is quite simple.
	site = ""
	relCount=0
	for plat in ls["latest_stable"]:
		platVerTemp = ""
		for platVer in ls["latest_stable"][plat]:
			v = ls["latest_stable"][plat][platVer]
			releaseConTemp = ""
			for au in db["releases"][v][plat]:
				if platVer in db["releases"][v][plat][au]:
					archConTemp = ""
					for btnss in db["releases"][v][plat][au][platVer]:
						relCount+=1
						relListTemp = ""
						for rel in db["releases"][v][plat][au][platVer][btnss]["files"]:
							fi = db["releases"][v][plat][au][platVer][btnss]["files"][rel]
							if os.path.splitext(fi["url"])[1][1:] not in _IGNORE_EXTENSION_LIST:
																					#create_title_by_filename(rel)
								relListTemp += releaseTemplate.format(release_title=v,href_link=fi["url"],release_file_name=rel)
						archConTemp += archContainerTemplate.format(bitness=_ARCH_FRIENDLY_NAME[btnss],release_list=relListTemp)
					
					releaseConTemp += releaseContainerTemplate.format(author=au,arch_container_list=archConTemp)
			platVerTemp += platformVersionContainerTemplate.format(platform_version_header=create_platform_version(platVer),release_container_template=releaseConTemp)
		site += platFormContainerTemplate.format(platform_name=create_platform_name(plat),platform_version_container_template=platVerTemp)
	print("Scanned {0} releases..".format(relCount))
	f = open(os.path.join(_OUTPUT_FOLDER,"index.html"),"w")
	f.write(indexTemplate
		.replace("[[sub_title]]","Stable downloads")
		.replace("[[mainData]]",site)
		.replace("[[top_url_link]]","archive.html")
		.replace("[[top_url_text]]","Browse archived versions")
		)
	f.close()
	print("Built main index.html")
	
# "releases": {
	# "55.0.2883.75-1": {
		# "ubuntu": {
			# "9Morello": {
				# "ubuntu1610": {
					# "amd64": {
						# "files": {
						
# <table border=1>



  # <tr>
    # <th>{version}</th>
    # <th></th>
  # </tr>
  # <tr>
    # <th>{platform}</th>
    # <th></th> 
  # </tr>
  # </tr>
    # <tr>
    # <th>{author}</th>
    # <th></th> 
  # </tr>
  # </tr>
    # <tr>
    # <th>{platform_version}</th>
    # <th></th> 
  # </tr>
  # </tr>
    # <tr>
    # <th>{bitness}</th>
    # <th></th> 
  # </tr>
  # <tr>
    # <td></td>
    # <td>{file}</td> 
  # </tr>
  
  
  
# </table>

	
def generate_archive(db): # tbd 
	site = ""
	relCount = 0
	beginning=False
	for ver in db["releases"]:
		if not beginning:
			beginning=True
		else:
			site+='''<tr class="versionSeperator">
				<th colspan="2">&nbsp;</th>
			</tr><tr>
				<th colspan="2">&nbsp;</th>
			</tr>'''
		site += '''<tr>
			<th class="versionHeader" colspan="2">{version}</th>
		</tr>'''.format(version=ver)
		for plat in db["releases"][ver]:
			site += '''<tr>
				<th class="platformHeader">{platform}</th>
				<th></th> 
			</tr><tr><td colspan="2">&nbsp;</th></tr>'''.format(platform=create_platform_name(plat))
			for au in db["releases"][ver][plat]:
				site += '''<tr>
					<th>Builds by {author}</th>
					<th></th> 
				  </tr>'''.format(author=au)
				for platVer in db["releases"][ver][plat][au]:
					site += '''<tr>
							<th>{platform_version}</th>
							<th></th> 
						  </tr>'''.format(platform_version=create_platform_version(platVer))
					for btnss in db["releases"][ver][plat][au][platVer]:
						relCount += 1
						site += '''<tr>
								<th>{bitness}</th>
								<th></th> 
							</tr>'''.format(bitness=_ARCH_FRIENDLY_NAME[btnss])
						for rel in db["releases"][ver][plat][au][platVer][btnss]["files"]:
							fi = db["releases"][ver][plat][au][platVer][btnss]["files"][rel]
							site += '''<tr>
								<td></td>
								<td><i class="fa fa-download" aria-hidden="true"></i> <a href="{href_link}">{filename}</a></td> 
							</tr>'''.format(filename=rel,href_link=fi["url"])
			
	print("Scanned {0} releases..".format(relCount))
	f = open(os.path.join(_OUTPUT_FOLDER,"archive.html"),"w")
	f.write(indexTemplate
		.replace("[[sub_title]]","Archive")
		.replace("[[mainData]]",'<table class="archiveTable">'+site+'</table>')
		.replace("[[top_url_link]]","index.html")
		.replace("[[top_url_text]]","Browse stable versions")
		)
	f.close()
	print("Built archive.html")
if __name__ == "__main__":
	db,ls = read_database()
	generate_main_index(db,ls)
	generate_archive(db)
