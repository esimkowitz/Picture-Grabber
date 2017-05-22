#import json
#import urllib2
import argparse
from googleapiclient.discovery import build
import pprint
import os
import subprocess
import mimetypes
from hashlib import sha1

parser = argparse.ArgumentParser(description="Let's grab some pictures from Google")
parser.add_argument('query', metavar='S', type=str,
                    help='the desired search query')
args = parser.parse_args()
api_key = "AIzaSyDgupdc84Z-Tt49vBJmb_2v7DVCFdKNuM0"
cse_id = "003218340875695042344:a0ju79bnocu"

service = build("customsearch", "v1", 
                developerKey=api_key)
destination_dir = "%s/%s"%(os.path.abspath(os.curdir), args.query)
if not os.path.isdir(destination_dir):
    os.mkdir(destination_dir)
itemsPerPage = 10
for i in range(100, 110, itemsPerPage):
    res = service.cse().list(
        q=args.query,
        cx=cse_id,
        searchType='image',
        imgType='photo',
        start=i
    ).execute()
    for item in res["items"]:
        if item["mime"] and item["mime"] != "image/":
            extensions = mimetypes.guess_all_extensions(item["mime"])
            if len(extensions) > 0:
                print item["link"]
                filepath = "%s/%s%s" % (destination_dir,
                                        sha1(item["link"]).hexdigest(), 
                                        extensions[0])
                print filepath
                #subprocess.call(["wget", item["link"], "-O", filepath])
    print res.get("queries").get("nextPage")[0]
    print service.cse().list(res.get("queries").get("nextPage")[0]).execute()
"""
for i in xrange(1, 200, 10):
    print i
    url = "https://www.googleapis.com/customsearch/v1?cx=%s&key=%s&q=%s&searchType=image&start=%i"%(cse_id, api_key, args.query, i)
    response = json.load(urllib2.urlopen(url))
"""
