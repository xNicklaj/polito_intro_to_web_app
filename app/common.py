from os.path import join, dirname, splitext, exists
from os import mkdir
from shutil import move
from datetime import datetime, timezone

# Upload file to app/tmp directory, then move it to the final directory based on its format.
def savefile(file, path):
    filename = str(abs(hash(file.filename))) + splitext(file.filename)[-1]
    if not exists(join(dirname(__file__), "tmp")):
        mkdir(join(dirname(__file__)))
    tmppath = join(dirname(__file__), "tmp", filename)
    file.save(tmppath)
    move(tmppath, join(dirname(__file__), "static", path))

# Convert a unix utc timestamp to string of type "6 Jan, 2006"
def timestampToString(timestamp):
    value = datetime.fromtimestamp(timestamp, timezone.utc)
    return value.strftime('%d %b, %Y')

# Make sure that all keys in the fields list are non-zero strings if they are present.
def validateFields(fields):
    for f in fields:
        if(f == None or (type(f) == str and len(f) == 0)):
            return False
    return True

# This class defines a history object used to save recent interactions between the client and the server, allowing to redirect to previously visited pages.
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
    
    # Gets the element of the list associated with the absolute offset to the current element. Therefore, get(-1) is the same as get(1).
    def get(self, index : int):
        if(index < 0):
            index = abs(index)
        if(index > self.max_size):
            return None
        try:
            return self.buff[::-1][index]
        except:
            return None