"""
# Copyright 2015 Asteroide
# This software is distributed under the terms and conditions of the 'Apache-2.0'
# license which can be found in the file 'LICENSE' in this package distribution
# or at 'http://www.apache.org/licenses/LICENSE-2.0'.
"""

# TODO: copy the files to the destination directory
# TODO: clean the code
# TODO: add an option for "Delete image from source"
# TODO: add a micro database for image already scanned
# TODO: add additional tags in images (eg: Children, Phone, ...)


import sys
import os
import time
import exifread
import glob
import shutil
from PIL import Image
from optparse import OptionParser
import logging
from tkinter import PhotoImage
import tkinter as tk

PORT = 8080
logger = logging.getLogger('img_backup')
SIZE = (256, 256)
TMP_DIR = "/tmp/ib"

try:
    os.mkdir(TMP_DIR)
except OSError:
    pass

class Application(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.root = master
        self.pack()
        self.__create_widgets()
        self.__img_db = None
        self.__dirnames = list()
        self.__current_dirname = ""
        self.__current_tk_image = []

    def __end_configuration(self):
        self.root.destroy()
        return self.__img_db

    def get_images(self):
        return self.__img_db

    def set_next_image_to_frame(self, event=None):
        previous_text = self.entry_set.get()
        if self.__current_tk_image:
            self.__img_db[self.__current_dirname]['dir'] = previous_text
            # Delete tk images
            self.canvas.delete(tk.ALL)
        self.__current_tk_image = []
        try:
            self.__current_dirname = self.__dirnames.pop()
        except IndexError:
            return self.__end_configuration()
        img_list = self.__img_db[self.__current_dirname]["thumbs"]
        self.entry_set.delete(0, len(previous_text))
        self.entry_set.insert(0, self.__current_dirname)
        border = 10
        cpt = 0
        for image in img_list:
            imgobj = PhotoImage(file=image)
            _x = imgobj.width()/2 + imgobj.width()*(cpt % 2) + border
            _y = imgobj.height()/2 + imgobj.height()*int(cpt/2) + border
            cpt += 1
            print(cpt, _x, _y)
            self.canvas.create_image(_x, _y, image=imgobj)
            self.__current_tk_image.append(imgobj)
        self.entry_set.focus_set()

    def set_img_db(self, img_db):
        self.__img_db = img_db
        self.__dirnames = list(self.__img_db.keys())
        self.__dirnames.sort(reverse=True)
        self.set_next_image_to_frame()

    def __create_widgets(self):
        self.frame_top = tk.Frame(self)

        self.entry_set = tk.Entry(self.frame_top)
        self.entry_set["textvariable"] = "Set the name..."
        self.entry_set.bind('<Key-Return>', self.set_next_image_to_frame)
        self.entry_set.pack(side="left")

        self.button_set = tk.Button(self.frame_top)
        self.button_set["text"] = "Next..."
        self.button_set["command"] = self.set_next_image_to_frame
        self.button_set.pack(side="left")

        self.frame_top.pack(fill='both', expand='yes')

        self.frame_body = tk.Frame(self, width=80, height=80, bg='#808000')

        self.canvas = tk.Canvas(self.frame_body, width=2*SIZE[0]+20, height=400)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.scrollbar = tk.Scrollbar(self.frame_body, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.frame_body.pack(fill='both', expand='yes')

        # self.button_set.pack(side="top")
        # self.QUIT = tk.Button(self, text="QUIT", fg="red",
        #                       command=self.root.destroy)
        # self.QUIT.pack(side="bottom")


def create_thumbnail(infile, directory, size=SIZE):

    outname = None
    try:
        im = Image.open(infile)
        im.thumbnail(size)
        outname = os.path.join(directory, os.path.basename(infile))
        outname = outname.replace(".JPG", ".jpg")
        outname = outname.replace(".jpg", ".ppm")
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

def set_up_db(options, args):
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
                img_db[dirname]["thumbs"].append(create_thumbnail(photo, TMP_DIR))
                sys.stdout.write("/-\\|"[cpt%4]+"    "+str(cpt)+"   \r")
                sys.stdout.flush()
    return img_db

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
                      help="Delete image from source", default=False)
    return parser.parse_args()


if __name__ == "__main__":
    options, args = load_args()
    img_db = set_up_db(options, args)

    if options.configurator:
        root = tk.Tk()
        app = Application(master=root)
        app.set_img_db(img_db)

        app.mainloop()

        img_db = app.get_images()

    max = 0
    cpt = 0
    for dirname in img_db:
        max += len(img_db[dirname]['list'])
    for dirname in img_db:
        _output_dir = os.path.join(options.destination, img_db[dirname]['dir'])

        for img in img_db[dirname]['list']:
            if os.path.isfile(os.path.join(_output_dir, os.path.basename(img))):
                continue
            if not options.dryrun:
                sys.stdout.write("{:.2%} - {} -> {}   \r".format(cpt/max, img, _output_dir))
            else:
                print("\rCopy {} -> {}      ".format(img, _output_dir))
            if not options.dryrun:
                os.makedirs(_output_dir, exist_ok=True)
            if not options.dryrun:
                shutil.copy(img, _output_dir)
            cpt += 1

    if not options.dryrun:
        sys.stdout.write("{:.2%}   \n".format(1.))
