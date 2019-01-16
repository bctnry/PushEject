# PushEject.
# (c) sebastian lin. 2018

# usage:
#     python ./main.py [id-of-nhentai-gallery]
# the [id-of-nhentai-gallery] part is the id in the address.
# e.g. the one doujin that you should never read has the id 177013, so if you
# really want to read that you can use `python ./main.py 177013` to download
# it. THE ID 177013 WAS MEANT TO BE AN EXAMPLE *ONLY*. DON'T READ THAT DOUJIN.
# tested under archlinux. does not guarantee to work under windows.

import http.client
import re
import html.parser
import os
import shutil
import sys

CONNECTION = None
RESULT_DIR = './result/'

# regexps.
REGEX_IMG = re.compile('<img src="(.*?)".*>')
REGEX_FILE_NAME = re.compile('.*/(.*)$')
REGEX_GALLERY_NAME_BIG = re.compile('<h1>(.*)</h1>')
REGEX_NUM_PAGES = re.compile('<div>([0-9]*) pages</div>')

# this is just to escape some of the special characters because currently
# pusheject will choke on some tags. specifically Fate tags (Fate/stay
# night, Fate/Grand Order, etc.), for they have slashes.
def directory_name_escape(dir_name):
    return dir_name.replace('/', ' ')


def download_file(result_dir, url):
    global CONNECTION, RESULT_DIR, REGEX_FILE_NAME
    with open("%s/%s" % (result_dir, REGEX_FILE_NAME.findall(url)[0]), mode='wb') as opened:
        CONNECTION.request('GET', url)
        try:
            opened.write(CONNECTION.getresponse().read())
        except:
            print('WRITE FAILED.')

def get_pic_addr(gallery_pic_str):
    return REGEX_IMG.findall(gallery_pic_str)[1]

def get_gallery_info(gallery_id):
    global CONNECTION, REGEX_GALLERY_NAME_BIG, REGEX_NUM_PAGES
    CONNECTION.request('GET', '/g/%s/' % gallery_id)
    resp = CONNECTION.getresponse()
    if resp.getcode() == 200:
        resp_str = resp.read().decode()
        return {
            'name': REGEX_GALLERY_NAME_BIG.findall(resp_str)[0],
            'num_pages': int(REGEX_NUM_PAGES.findall(resp_str)[0])
        }
    else:
        print('Gallery info retriever reported error with code', resp.getcode(), flush=True)
        return None


def get_gallery(gallery_id):
    global CONNECTION, RESULT_DIR
    gallery_info = get_gallery_info(gallery_id)
    if not gallery_info:
        print('No gallery info. Download cancelled.')
        return
    print('Gallery info retrieved:')
    print('Name:\t\t%s\n#Pages:\t\t%s' % (gallery_info['name'], gallery_info['num_pages']))
    gallery_dir = "%s%s" % (RESULT_DIR, gallery_id)
    gallery_result_dir = "%s%s/%s" % (RESULT_DIR, gallery_id, directory_name_escape(gallery_info['name']))
    print('Your file will be saved at %s.\nStart downloading...' % gallery_result_dir, flush=True)
    if os.path.exists(gallery_dir):
        shutil.rmtree(gallery_dir)
    os.mkdir(gallery_dir)
    os.mkdir(gallery_result_dir)
    for i in range(1, gallery_info['num_pages'] + 1):
        print('Downloading %s...' % i, flush=True)
        CONNECTION.request('GET', '/g/%s/%s/' % (gallery_id, i))
        resp = CONNECTION.getresponse()
        if resp.getcode() == 200:
            download_file(gallery_result_dir, get_pic_addr(resp.read().decode()))
        else:
            print('Failed to download %s. Leaving...' % i, flush=True)
            break
    print('Downloading finished.')

def initialization():
    global CONNECTION, RESULT_DIR
    # initialize the connection.
    CONNECTION = http.client.HTTPSConnection('nhentai.net')
    # prepare the directory.
    if not os.path.exists(RESULT_DIR):
        os.mkdir(RESULT_DIR)

def finalization():
    global CONNECTION
    CONNECTION.close()
    del CONNECTION

def main():
    initialization()
    for x in sys.argv[1:]:
        get_gallery(x)
    finalization()

main()