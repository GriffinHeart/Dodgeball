from datetime import datetime
import pytz

class googletimeconv(object):
    def __init__(self, timestr):
        self.timestr = timestr
        self.timezone = pytz.timezone('Asia/Tokyo')

    def convert(self):
        foo1 = self.timestr.split('+')[0]
        foo2 = datetime.strptime(foo1, '%Y-%m-%dT%H:%M:%S')
        return foo2