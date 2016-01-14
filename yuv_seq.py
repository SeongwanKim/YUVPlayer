import numpy as np
import matplotlib.pyplot as plt
import cv2

class YUV_frame:
    """ YUV frame 한장 """
    def __init__(self, w, h, d):
        self.width = w
        self.height = h
        self.bitdepth = d
    def read_frame(self, fp):
        size = self.width * self.height
        step = 1 if self.bitdepth == 8 else 2
        Y = fp.read(size * step)
        U = fp.read(size * step//4)
        V = fp.read(size * step//4)
        if len(Y) == 0:
            return 0
        if self.bitdepth == 8:
            Y = np.fromstring(Y, dtype='uint8').astype('uint16')
            U = np.fromstring(U, dtype='uint8').astype('uint16')
            V = np.fromstring(V, dtype='uint8').astype('uint16')
        else:
            Y = np.fromstring(Y, dtype='uint16')
            U = np.fromstring(U, dtype='uint16')
            V = np.fromstring(V, dtype='uint16')
        self.Y = np.reshape(Y,(self.height, self.width))
        self.U = np.reshape(U,(self.height//2, self.width//2))
        self.V = np.reshape(V,(self.height//2, self.width//2))
        return len(Y)

    def GetImg(self, channel, width, height):
        import scipy.ndimage
        div = 2**(self.bitdepth-8)
        ret = np.zeros((height, width, 3), 'uint8')+128
        ratio = min(width/self.width, height/self.height)
        dst_width = ratio * self.width
        dst_height = ratio * self.height
        dst_x = (width - dst_width) // 2
        dst_y = (height - dst_height) // 2
        dst_width += dst_x
        dst_height += dst_y

        if channel == 'Y':
            ret[dst_y:dst_height,dst_x:dst_width,0] = cv2.resize((self.Y // div), (0,0), fx=ratio, fy=ratio)
        elif channel == 'U':
            ret[dst_y:dst_height,dst_x:dst_width,0] = cv2.resize((self.U // div), (0,0), fx=ratio*2, fy=ratio*2)
        elif channel == 'V':
            ret[dst_y:dst_height,dst_x:dst_width,0] = cv2.resize((self.V // div), (0,0), fx=ratio*2, fy=ratio*2)
        else:
            ret[dst_y:dst_height,dst_x:dst_width,0] = cv2.resize((self.Y // div), (0,0), fx=ratio, fy=ratio)
            ret[dst_y:dst_height,dst_x:dst_width,1] = cv2.resize((self.U // div), (0,0), fx=ratio*2, fy=ratio*2)
            ret[dst_y:dst_height,dst_x:dst_width,2] = cv2.resize((self.V // div), (0,0), fx=ratio*2, fy=ratio*2)

        ret = cv2.cvtColor(ret,cv2.COLOR_YUV2BGR)
        return ret

class YUV_sequence:
    """ YUV sequences """
    def __init__(self):
        self.width = 0
        self.height = 0
        self.fps = 24

    def createDB(self):
        import sqlite3
        #DB 가 없으면 생성
        con = sqlite3.connect('fileopenlog.db')
        csr = con.cursor()
        print ('Create Table')
        tables = 'FileName TEXT NOT NULL, '
        tables += 'WIDHT INT NOT NULL, '
        tables += 'HEIGHT INT NOT NULL, '
        tables += 'framerate INT NOT NULL, '
        tables += 'bit_depth INT'
        query = "CREATE TABLE {0}({1});".format('filenames',tables)
        csr.execute(query)
        con.commit()
        print(query)

    def insertDB(self, filename, width, height, fps, bitdepth):
        import sqlite3
        con = sqlite3.connect('fileopenlog.db')
        csr = con.cursor()
        try:
            csr.execute("SELECT * from {0} where FileName='{1}';".format('filenames', filename))
            con.commit()
            re = csr.fetchall()
        except sqlite3.OperationalError:
            self.createDB()
            re = 0
        if re:
            # update
            query = "UPDATE filenames SET WIDTH={1}, HEIGHT={2},framerate={3},bit_depth={4} WHERE FileName={0};".format(filename,width,height,fps,bitdepth)
        else:
            query_data = {
            'FileName'        : filename,
            'WIDTH'            : width,
            'HEIGHT'        : height,
            'framerate'        : fps,
            'bit_depth'        : bitdepth,
            }
            # insert
            query = "INSERT INTO {0} ({1}) VALUES {2};".format('filenames', ', '.join(query_data.keys()), tuple(query_data.values()))
        csr.execute(query)
        con.commit()
        con.close()

    def get_seq_params(self, filename):
        import re
        # if known format ([a-zA-Z0-9]+)_[width]x[height]_[framerate]_[bitdepth]_[a-zA-Z].yuv
        pattern ='([a-zA-Z0-9]+)_(\d+)[x](\d+)_(\d{2})(_10bit)?'
        m = re.search(pattern, filename)
        if m:
            [seq, w, h, f, d] =m.groups()
            w = int(w)
            h = int(h)
            f = int(f)
            d = 10 if d == '_10bit' else 8
            return [w,h,f,d]
        else: # query database
            #TODO: completete it
            import sqlite3
            conn = sqlite3.connect('fileopenlog.db')
        return [1920, 1080,24,8]

    def open_file(self, filename, width, height, fps, bpp = 8):
        #read file
        self.data = []
        cnt = 0
        with open(filename, 'rb') as f:
            while True:
                t = YUV_frame(width, height, bpp)
                ret_len = t.read_frame(f)
                if ret_len == 0:
                    break
                self.data.append(t)
        return len(self.data)
    def getFrame(self, FrameNum):
        return self.data[FrameNum]
