import shutil
import os
import timeit

from optparse import OptionParser

from ConfigWorker import generate_root_config
from RSyncWorker import walk_root_directory, walker
from CheckExists import exists
from ParallelWorker import walk

parser = OptionParser()
parser.add_option('-m', '--mirror', dest='url', help='define mirror, otherwise default used')
parser.add_option('-p', '--pxedir', dest='pxedir', help='define pxecfg.d, otherwise default used')
(options, args) = parser.parse_args()

url = vars(options).get('url')
pxedir = vars(options).get('pxedir')

url = 'rsync://mirror.yandex.ru/' if url is None else url
pxedir = 'pxelinux.cfg' if pxedir is None else pxedir

if (url[-1] != '/'):
    url += '/'

#get main tree (usually doesn't work correcly with recursive rsync)
directories = walk_root_directory(walker(url))
if os.path.isdir(pxedir):
    #remove old directory (protect from overwrite)
    shutil.rmtree(pxedir)

#creating main pxe directory where files stored
os.mkdir(pxedir)

pxedir_location = os.path.join(os.getcwd(), pxedir)
#check availability via http or ftp
urlForConfig = exists(url, directories)

if urlForConfig:
    begin = timeit.default_timer()
    #start parallel worker here
    walk(directories, url, urlForConfig, pxedir)
    #generate final config
    generate_root_config(pxedir)
    end = timeit.default_timer() - begin
    print('Mirror walked in %f. Results are in %s' % (end, pxedir_location))
else:
    print("Something went wrong. Walker shattered some glass")
