from bs4 import BeautifulSoup
import re
import urllib.request
import os
import argparse
import json
from hashlib import sha1
import mimetypes
from queue import Queue
from threading import Thread

# Author: Evan Simkowitz

WORKER_THREADS = 40

q = Queue()  

# Worker thread - retrieve from Queue and process data for downloading

def worker():
    while True:
        resData = q.get()
        if resData is None:
            break
        link = resData[0]
        Type = resData[1]
        DIR = resData[2]
        try:
            req = urllib.request.Request(link)
            req.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36")
            res = urllib.request.urlopen(req)
            raw_img = res.read()
            filename = str(sha1(link.encode()).hexdigest()) + "." + Type
            if len(Type) != 0 and res.info().get("Content-Type") != "text/html":
                #print res.info().get("Content-Type")
                #print mimetypes.guess_type(filename)
                f = open(os.path.join(DIR, filename), 'wb')
                f.write(raw_img)
                f.close()
        except Exception as e:
            print("could not load : " + link)
            print(e)
        q.task_done()

def get_soup(url, header):
    return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url, headers=header)), 'html.parser')

# you can change the query for the image  here
parser = argparse.ArgumentParser(
    description="Let's grab some pictures from Google")
parser.add_argument('query', metavar='S', type=str,
                    help='the desired search query')
args = parser.parse_args()
query = args.query
query = query.split()
query = '+'.join(query)
url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"
#add the directory for your image here
DIR = "Pictures"
header = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
          }
soup = get_soup(url, header)

if not os.path.exists(DIR):
            os.mkdir(DIR)
DIR = os.path.join(DIR, query.split()[0])

if not os.path.exists(DIR):
            os.mkdir(DIR)

# Create Worker Threads
for i in range(WORKER_THREADS):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

for a in soup.find_all("div", {"class": "rg_meta"}):
    link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
    q.put([link, Type, DIR])

# block until all tasks are done
q.join()
