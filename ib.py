
import os
import sys
import signal
import exifread
import glob
import time
import shutil
from PIL import Image
from optparse import OptionParser
import logging
from tkinter import PhotoImage
import tkinter as tk
import webbrowser

import cherrypy

# from cherrypy._cpserver import Server
# server = Server()
# server.socket_port = 8090
# server.subscribe()

import threading

config = {
    'global': {
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
        'server.thread_pool': 8,
        # interval in seconds at which the timeout monitor runs
        'engine.timeout_monitor.frequency': 1
    },
    '/': {
        # the number of seconds to allow responses to run
        'response.timeout': 2
    }
}


class AsyncWebServer(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(AsyncWebServer, self).__init__()
        # threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.img_db = dict()
        self.img_list = list()
        self.title = ""

    def stop(self):
        cherrypy.engine.stop()
        cherrypy.server.httpserver = None
        self._stop.set()

    def run(self):
        # self.web_server = WebServer()
        cherrypy.quickstart(self, '/', config)

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

    @cherrypy.expose
    def index(self):
        html_list = ""
        for img in self.img_list:
            html_list += """<img src="{}"> \n\t\t""".format(img)
        self.html = """<html>
    <body>
        {img_list}
    </body>
</html>
        """.format(img_list=html_list)
        return self.template.format(title=self.title, img_list=html_list)

    def load_filenames(self, img_db):
        self.img_db = dict(img_db)
        self.title = list(self.img_db.keys())[0]
        self.img_list = self.img_db[self.title]["thumbs"]


#
# class WebServer(object):
#     template = """
# <html>
#     <head><title>{title}</title></head>
#     <body>
#         <h1>{title}</h1>
#         {img_list}
#     </body>
# </html>
#         """
#
#     @cherrypy.expose
#     def index(self):
#         return "Hello World!"


# class WebReport:
#
#     def __init__(self, img_list):
#         html_list = ""
#         for img in img_list:
#             html_list += """<img src="{}"> \n\t\t""".format(img)
#         self.html = """<html>
#     <body>
#         {img_list}
#     </body>
# </html>
#         """.format(img_list=html_list)
#
#     def save(self, filename):
#         open(filename, "w").write(self.html)
#
#     def __str__(self):
#         return self.html


# class Application(tk.Frame):
#
#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.root = master
#         self.pack()
#         self.__create_widgets()
#
#     def add_image_to_frame(self, dirname, img_list):
#         self.hi_there["text"] = dirname
#         for image in img_list:
#             logger.info("Adding image in TK {}".format(image))
#             imgobj = PhotoImage(file=image)
#             label = tk.Label(self, image=imgobj, text=image)
#             label.img = imgobj
#             label.pack(side='bottom')
#         self.pack(side='bottom')
#
#     def __create_widgets(self):
#         self.hi_there = tk.Button(self)
#         self.hi_there["text"] = "Hello World\n(click me)"
#         # self.hi_there["command"] = self.say_hi
#         self.hi_there.pack(side="top")
#         self.QUIT = tk.Button(self, text="QUIT", fg="red",
#                               command=self.root.destroy)
#         self.QUIT.pack(side="bottom")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('img_backup')

SIZE = (256, 256)

def create_thumbnail(infile, directory, size=SIZE):

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

def get_date_time(fn):
    f = open(fn, 'rb')
    try:
        tags = exifread.process_file(f, details=False)
        _time = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
        return time.strftime("%Y/%m-%d", _time)
    except KeyError:
        # print("Error with {}".format(fn))
        pass

def load_dir(directories):
    for filename in directories:
        if os.path.isdir(filename):
            glob_dir = glob.glob(os.path.join(filename, "*"))
            max = len(glob_dir)
            cpt = 0
            for _filename in glob_dir:
                dirname = get_date_time(_filename)
                cpt += 1
                yield _filename, dirname, max, cpt

def create_multiple_thumbnails(img_db):
    keys = list(img_db.keys())
    keys.sort()
    for dirname in keys:
        img_list = list(img_db[dirname]["thumbs"])
        html_filename = os.path.join("/tmp", dirname.replace("/", "-")+".html")
        # WebReport(img_list).save(html_filename)
        # webbrowser.open(html_filename)
        name = input("Give the name of this directory [{}]: ".format(dirname))
        print(name)
        # root = tk.Tk()
        # app = Application(master=root)
        # app.add_image_to_frame(dirname, img_list)
        # app.mainloop()

def load_args():
    parser = OptionParser()
    parser.add_option("-o", "--output-destination", dest="destination",
                      help="copy files to DIR", metavar="DIR", default="/tmp")
    parser.add_option("-d", "--dry-run", dest="dryrun", action="store_true",
                      help="Execute the script but don't copy the files", default=False)
    parser.add_option("-c", "--configure", dest="configurator", action="store_true",
                      help="Create thumbnail and configure name of directories", default=False)
    parser.add_option("-f", "--force", dest="force", action="store_true",
                      help="Force analysis of all image (even if already processed)", default=False)
    parser.add_option("--delete", dest="delete", action="store_true",
                      help="Delete image from source", default=False) # TODO
    return parser.parse_args()

def main(options, args, web_server):
    directories = args
    out_directory = options.destination
    img_db = {}
    for directory in args:
        for photo, dirname, max, cpt in load_dir(directories):
            if photo and dirname:
                if dirname not in img_db:
                    img_db[dirname] = {}
                    img_db[dirname]["list"] = []
                    img_db[dirname]["thumbs"] = []
                    img_db[dirname]["dir"] = dirname
                img_db[dirname]["list"].append(photo)
                _outdir = os.path.join(out_directory, dirname)
                if os.path.isfile(os.path.join(_outdir, os.path.basename(photo))):
                    continue
                img_db[dirname]["thumbs"].append(create_thumbnail(photo, "/tmp"))
    if options.configurator:
        web_server.load_filenames(img_db)
        # create_multiple_thumbnails(img_db)
    for photo, dirname, max, cpt in load_dir(directories):
        if photo and dirname:
            _outdir = os.path.join(out_directory, dirname)
            if os.path.isfile(os.path.join(_outdir, os.path.basename(photo))):
                continue
            if not options.dryrun:
                sys.stdout.write("{:.2%} - {} -> {}   \r".format(cpt/max, photo, _outdir))
            else:
                print("\rCopy {} -> {}      ".format(photo, _outdir))
            if not options.dryrun:
                os.makedirs(_outdir, exist_ok=True)
            if not options.dryrun:
                shutil.copy(photo, _outdir)
    if not options.dryrun:
        sys.stdout.write("{:.2%}   \n".format(1.))

if __name__ == "__main__":
    options, args = load_args()
    web_server = AsyncWebServer()
    web_server.start()

    main(options, args, web_server)

    webbrowser.open_new("http://localhost:8080")
    # web_server.stop()
    # os.kill(os.getpid(), signal.SIGSTOP)
    web_server.join()
