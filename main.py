# PushEject.
# (c) sebastian lin. 2018

import http.client
import re
import html.parser
import os
import shutil

CONNECTION = None
RESULT_DIR = './result/'

# regexps.
REGEX_IMG = re.compile('<img src="(.*?)".*>')
REGEX_FILE_NAME = re.compile('.*/(.*)$')

def download_file(url):
    global CONNECTION, RESULT_DIR, REGEX_FILE_NAME
    with open(RESULT_DIR + REGEX_FILE_NAME.findall(url)[0], mode='wb') as opened:
        CONNECTION.request('GET', url)
        try:
            opened.write(CONNECTION.getresponse().read())
        except:
            print('WRITE FAILED.')

def get_pic_addr(gallery_pic_str):
    return REGEX_IMG.findall(gallery_pic_str)[1]

def get_gallery(gallery_id):
    global CONNECTION
    i = 1
    while True:
        print('Downloading %s...' % i, flush=True)
        CONNECTION.request('GET', '/g/%s/%s/' % (gallery_id, i))
        resp = CONNECTION.getresponse()
        if resp.getcode() == 200:
            download_file(get_pic_addr(resp.read().decode()))
            i += 1
        else:
            print('Failed to download %s. Leaving...' % i, flush=True)
            break

def initialization():
    global CONNECTION, RESULT_DIR
    # initialize the connection.
    CONNECTION = http.client.HTTPSConnection('nhentai.net')
    # prepare the directory.
    if os.path.exists(RESULT_DIR):
        shutil.rmtree(RESULT_DIR)
    os.mkdir(RESULT_DIR)

def finalization():
    global CONNECTION
    CONNECTION.close()
    del CONNECTION

def main():
    initialization()
    get_gallery(0)
    finalization()

main()