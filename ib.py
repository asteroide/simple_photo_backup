import sys
import http.server
import socketserver
import os
import threading
import time
import exifread
import glob
import shutil
from PIL import Image
from optparse import OptionParser
import logging

PORT = 8080
logger = logging.getLogger('img_backup')
SIZE = (256, 256)
TMP_DIR = "/tmp/ib"

try:
    os.mkdir(TMP_DIR)
except OSError:
    pass


class AsyncWebServer(threading.Thread):

    template = """
<html>
    <head><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        {img_list}
        <hr>
        <form action="/">
            <input type="button" value="quit">
            <input type="text" value="name">

        </form>
    </body>
</html>
        """

    def __init__(self, *args, **kwargs):
        super(AsyncWebServer, self).__init__()
        self.img_db = dict()
        self.img_list = list()
        self.title = ""
        self.Handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("", PORT), self.Handler)
        os.chdir(TMP_DIR)

    def stop(self):
        logger.info("quitting server")
        self.httpd.shutdown()
        # self._stop.set()
        return self.img_db

    def run(self):
        print("serving at port", PORT)
        self.httpd.serve_forever()

    def create_thumbnail(self, infile, directory, size=SIZE):

        outname = None
        try:
            im = Image.open(infile)
            im.thumbnail(size)
            outname = os.path.join(directory, os.path.basename(infile))
            outname = outname.replace(".JPG", ".jpg")
            # outname = outname.replace(".jpg", ".ppm")
            im.save(outname)
            logger.info("Create thumbnail {}".format(outname))
        except IOError:
            logger.warning("cannot create thumbnail for {}".format(infile))
        return outname

    def get_date_time(self, fn):
        f = open(fn, 'rb')
        try:
            tags = exifread.process_file(f, details=False)
            _time = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
            return time.strftime("%Y/%m-%d", _time)
        except KeyError:
            # print("Error with {}".format(fn))
            pass

    def load_dir(self, directories):
        for filename in directories:
            if os.path.isdir(filename):
                glob_dir = glob.glob(os.path.join(filename, "*"))
                max = len(glob_dir)
                cpt = 0
                for _filename in glob_dir:
                    dirname = self.get_date_time(_filename)
                    cpt += 1
                    yield _filename, dirname, max, cpt

    def main(self, options, args):
        directories = args
        out_directory = options.destination
        self.img_db = {}
        for directory in args:
            for photo, dirname, max, cpt in self.load_dir(directories):
                if photo and dirname:
                    if dirname not in self.img_db:
                        self.img_db[dirname] = {}
                        self.img_db[dirname]["list"] = []
                        self.img_db[dirname]["thumbs"] = []
                        self.img_db[dirname]["dir"] = dirname
                    self.img_db[dirname]["list"].append(photo)
                    _outdir = os.path.join(out_directory, dirname)
                    if os.path.isfile(os.path.join(_outdir, os.path.basename(photo))):
                        continue
                    self.img_db[dirname]["thumbs"].append(self.create_thumbnail(photo, TMP_DIR))
        # if options.configurator:
        #     self.load_filenames(self.img_db)
        #     # create_multiple_thumbnails(img_db)

def load_args():
    parser = OptionParser()
    parser.add_option("-o", "--output-destination", dest="destination",
                      help="copy files to DIR", metavar="DIR", default="/tmp/ib")
    parser.add_option("-d", "--dry-run", dest="dryrun", action="store_true",
                      help="Execute the script but don't copy the files", default=False)
    parser.add_option("-c", "--configure", dest="configurator", action="store_true",
                      help="Create thumbnail and configure name of directories", default=False)
    parser.add_option("-f", "--force", dest="force", action="store_true",
                      help="Force analysis of all image (even if already processed)", default=False)
    parser.add_option("--delete", dest="delete", action="store_true",
                      help="Delete image from source", default=False) # TODO
    return parser.parse_args()



if __name__ == "__main__":
    web_server = AsyncWebServer()
    options, args = load_args()
    web_server.main(options, args)
    web_server.start()

    time.sleep(5)
    img_db = web_server.stop()

    print(img_db)

    for dirname in img_db:
        print(img_db[dirname])

    # for photo, dirname, max, cpt in self.load_dir(directories):
    #     if photo and dirname:
    #         _outdir = os.path.join(out_directory, dirname)
    #         if os.path.isfile(os.path.join(_outdir, os.path.basename(photo))):
    #             continue
    #         if not options.dryrun:
    #             sys.stdout.write("{:.2%} - {} -> {}   \r".format(cpt/max, photo, _outdir))
    #         else:
    #             print("\rCopy {} -> {}      ".format(photo, _outdir))
    #         if not options.dryrun:
    #             os.makedirs(_outdir, exist_ok=True)
    #         if not options.dryrun:
    #             shutil.copy(photo, _outdir)
    # if not options.dryrun:
    #     sys.stdout.write("{:.2%}   \n".format(1.))




