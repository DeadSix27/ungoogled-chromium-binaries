#!/usr/bin/env python3

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


# Imports
import json,sys,hashlib,zlib,pprint,os.path
from shutil import copyfile
# Settings

_DATABASE_FILE = "../config/release_list.json"
_HASH_ALGS = ["md5", "sha1", "sha256", "crc32"]

# Main functions

def print_usage_info():
	print("Usage: add_release_to_database.py {version} {author} {platform} {platformVersion} {amd64|i386} {filename {...}} ", file=sys.stderr)
	print("Example: add_release_to_database.py 55.0.2883.95-1 FooBar windows windows amd64 test.zip test2.zip", file=sys.stderr)

def create_download_link(a,v,f): # author, version, filename
	#return "https://github.com/Eloston/ungoogled-chromium/releases/download/{version}/{filename}".format(version=v,filename=f)
	return "https://github.com/{author}/ungoogled-chromium-binaries/releases/download/{version}/{filename}".format(author=a,version=v,filename=f)
	

def main(args):
	if len(args)<=0:
		print_usage_info()
		return 0
	if args[0] == "--help" or args[0] == "-h" or args[0] == "help" or len(args)<6:
		print_usage_info()
		return 0
	db = None
	print("Saving backup to {0}".format(_DATABASE_FILE+".back"))
	copyfile(_DATABASE_FILE, _DATABASE_FILE+".back")
	with open(_DATABASE_FILE) as jsonFile:
		db = json.load(jsonFile)
		
		version = args[0] #chromium version string e.g 55.0.2883.95-1
		author = args[1] # builder GitHub username e.g Eloston
		platform = args[2] # e.g windows or macos
		platform_version = args[3] # e.g ubuntu1604 (for windows, just use "windows") for a list see create_platform_version in site_generator.py
		arch = args[4] # e.g amd64 or i386
		filenames = args[5:] # list of files single or multiple depending on platform.
		
		# layout
		#	"releases": { 
		#		"(version)": { 55.0.2883.95-1
		#			"(platform)": { ubuntu
		#				"9Morello": { Eloston
		#					"ubuntu1610": { ubuntu1604
		#						"amd64": { amd64
		#							"files": { files }

		if version not in db["releases"]:
			db["releases"][version] = {}
		if platform not in db["releases"][version]:
			db["releases"][version][platform] = {}
		if author not in db["releases"][version][platform]:
			db["releases"][version][platform][author] = {}
		if platform_version not in db["releases"][version][platform][author]:
			db["releases"][version][platform][author][platform_version] = {}
		if arch not in db["releases"][version][platform][author][platform_version]:
			db["releases"][version][platform][author][platform_version][arch] = {}
			
		fileList = {}
		if "files" in db["releases"][version][platform][author][platform_version][arch]:
			fileList = db["releases"][version][platform][author][platform_version][arch]["files"]
		elif "files" not in db["releases"][version][platform][author][platform_version][arch]:
			db["releases"][version][platform][author][platform_version][arch]["files"] = {}
		
		
		for file in filenames:
			fbasename = os.path.basename(file)
			if fbasename not in fileList:
				with open(file,"rb") as fileobj:
					fileList[fbasename] = { "url" : create_download_link(author,version,fbasename) }
					for algorithm in _HASH_ALGS:
						if algorithm == "crc32":
							prev = 0
							for eachLine in fileobj:
								prev = zlib.crc32(eachLine, prev)
							fileList[fbasename][algorithm] = "%X"%(prev & 0xFFFFFFFF)
						else:
							hasher = hashlib.new(algorithm)
							hasher.update(fileobj.read())
							fileList[fbasename][algorithm] = hasher.hexdigest()
							fileobj.seek(0)
			else:
				#Skipping file, already in db. in the future we could probably compare hashes,
				#but since this is a dev tool, we assume the dev only uploads new files
				#and doesnt want to replace old ones with new ones that have different hashes if so,
				#use the probably not yet existing, delete_release.py tool or manually edit the json...
				pass
		db["releases"][version][platform][author][platform_version][arch]["files"] = fileList
	
	print("Saved to {f}".format(f=_DATABASE_FILE))
	with open(_DATABASE_FILE, 'w') as outfile:
		json.dump(db, outfile)

if __name__ == "__main__":
	exit(main(sys.argv[1:]))
