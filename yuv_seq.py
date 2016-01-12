import numpy as np
import matplotlib.pyplot as plt

class YUV_frame:
    """ YUV frame 한장 """
    def __init__(self, w,h,d):
        self.width = w
        self.height = h
        self.bitdepth = d
    def read_frame(self, fp):
        Y = fp.read(w*h*step)
        U = fp.read(w*h*step//4)
        V = fp.read(w*h*step//4)
        if self.bitdepth == 8:
            Y = np.fromstring(Y, dtype='uint8').astype('uint64')
            U = np.fromstring(U, dtype='uint8').astype('uint64')
            V = np.fromstring(V, dtype='uint8').astype('uint64')
        else:
            Y = np.fromstring(Y, dtype='uint16').astype('uint64')
            U = np.fromstring(U, dtype='uint16').astype('uint64')
            V = np.fromstring(V, dtype='uint16').astype('uint64')
        self.Y = np.reshape(Y,(self.height,self.width))
        self.U = np.reshape(U,(self.height,self.width))
        self.V = np.reshape(V,(self.height,self.width))

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
            self.createDB('filenames')
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
            query = "INSERT INTO {0} ({1}) VALUES {2};".format(DB_name, ', '.join(query_data.keys()), tuple(query_data.values()))
        csr.execute(query)
        con.commit()
        con.close()

    def get_seq_params(filename):
        # if known format ([a-zA-Z0-9]+)_[width]x[height]_[framerate]_[bitdepth]_[a-zA-Z].yuv
        pattern ='([a-zA-Z0-9]+)_(\d+)[x](\d+)_(\d{2})(_10bit)?'
        m = re.search(pattern, filename)
        if m:
            [seq, w, h, f, d] =m.groups()
            w = int(w)
            h = int(h)
            f = int(f)
            d = 10 if d == '_10bit' else 8
            return [seq,w,h,f,d]
        else: # query database
            import sqlite3
            conn = sqlite3.connect('fileopenlog.db')
        step = 1 if d == 8 else 2

    def open_file(filename, width, height, fps, bpp = 8):
        #read file
        self.data = []
        with open(obj, 'rb') as f:
            while True:
                t = YUV_frame(width, height, bpp)
                t.read()
                self.data.append(t)
    def getFrame(FrameNum):
        return self.data[FrameNum]
