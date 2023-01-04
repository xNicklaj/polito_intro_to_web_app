from os.path import join, dirname, splitext
from shutil import move
from datetime import datetime

def savefile(file, path):
    filename = str(abs(hash(file.filename))) + splitext(file.filename)[-1]
    tmppath = join(dirname(__file__), "tmp", filename)
    file.save(tmppath)
    move(tmppath, join(dirname(__file__), "static", path))

def timestampToString(timestamp):
    value = datetime.fromtimestamp(timestamp)
    return value.strftime('%d %b, %Y')