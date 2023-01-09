from os.path import join, dirname, splitext
from shutil import move
from datetime import datetime, timezone

def savefile(file, path):
    filename = str(abs(hash(file.filename))) + splitext(file.filename)[-1]
    tmppath = join(dirname(__file__), "tmp", filename)
    file.save(tmppath)
    move(tmppath, join(dirname(__file__), "static", path))

def timestampToString(timestamp):
    value = datetime.fromtimestamp(timestamp, timezone.utc)
    return value.strftime('%d %b, %Y')

def validateFields(fields):
    for f in fields:
        if(f == None or (type(f) == str and len(f) == 0)):
            return False
    return True

class History:
    buff : list
    max_size : int 

    def __init__(self, max_size=2):
        self.buff = list()
        self.max_size = max_size

    def push(self, curr : str):
        self.buff.append(curr)
        if len(self.buff) > self.max_size:
            self.buff.pop(0)
    
    def get(self, index : int):
        if(index < 0):
            index = abs(index)
        if(index > self.max_size):
            return None
        try:
            return self.buff[::-1][index]
        except:
            return None