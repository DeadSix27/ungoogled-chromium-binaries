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
_IGNORE_EXTENSION_LIST = ["changes","buildinfo"]
_ARCH_FRIENDLY_NAME = { "i386" : "32-Bit", "amd64" : "64-Bit" }
_INDEX_TEMPLATE = "index_template.html"


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
	<div class="link"><a href="{href_link}">{release_file_name}</a></div>
</div>
'''

# Main functions


def errorOut(msg):
	print(msg, file=sys.stderr)
	sys.exit(0)

def create_platform_name(p):
	platforms = { 
		"macos"        : ("fa-apple"   , "OS X"),
		"windows"      : ("fa-windows" , "Windows"),
		"linux_static" : ("fa-linux"   , "Linux static"),
		"debian"       : ("fa-linux"   , "Debian"), # tbd: replace with proper debian icon
		"ubuntu"       : ("fa-linux"   , "Ubuntu")  # tbd: replace with proper ubuntu icon
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
	with open(_DATABASE_FILE,"r") as fileobj:
		db = json.load(fileobj, object_pairs_hook=OrderedDict)
	return db

def generate_index(db): # Reads the database and builds an html page.
	site = ""
	for plat in db["latest_stable"]:
		platVerTemp = ""
		for platVer in db["latest_stable"][plat]:
			v = db["latest_stable"][plat][platVer]
			releaseConTemp = ""
			for au in db["releases"][v][plat]:
				archConTemp = ""
				for btnss in db["releases"][v][plat][au][platVer]:
					relListTemp = ""
					for rel in db["releases"][v][plat][au][platVer][btnss]["files"]:
						fi = db["releases"][v][plat][au][platVer][btnss]["files"][rel]
						if os.path.splitext(fi["url"])[1][1:] not in _IGNORE_EXTENSION_LIST:
							relListTemp += releaseTemplate.format(release_title=create_title_by_filename(rel),href_link=fi["url"],release_file_name=rel)
					archConTemp += archContainerTemplate.format(bitness=_ARCH_FRIENDLY_NAME[btnss],release_list=relListTemp)
					
				releaseConTemp += releaseContainerTemplate.format(author=au,arch_container_list=archConTemp)
			platVerTemp += platformVersionContainerTemplate.format(platform_version_header=create_platform_version(platVer),release_container_template=releaseConTemp)
		site += platFormContainerTemplate.format(platform_name=create_platform_name(plat),platform_version_container_template=platVerTemp)
	
	f = open("test.html","w")
	f.write(indexTemplate.replace("[[mainData]]",site))
	f.close()
		# for platVer in db["latest_stable"][plat]:
			# v = db["latest_stable"][plat][platVer]
			# htmlAuthorGroup = ""
			# for au in db["releases"][v][plat]:
				# platformVerList = ""
				# for platVer in db["releases"][v][plat][au]:
					# htmlReleaseList= ""
					# for arch in db["releases"][v][plat][au][platVer]:
						# for f in db["releases"][v][plat][au][platVer][arch]["files"]:
							# fi = db["releases"][v][plat][au][platVer][arch]["files"][f]
							
							# htmlReleaseList += releaseGroup.format(release_title=create_title_by_filename(f),hrefUrl=fi["url"],release_file_name=f)
					# htmlAuthorGroup += authorGroup.format(author=au,release_list=htmlReleaseList)
					# platformVerList += platformVerGroup.format(platform_version_header=create_platform_version(platVer),authorgroup_list=htmlAuthorGroup)
			# print(platformGroup.format(platform_header=create_platform_name(plat),platform_version_list=platformVerList))
if __name__ == "__main__":
	db = read_database()
	generate_index(db)
