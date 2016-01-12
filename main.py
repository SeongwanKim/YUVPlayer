"""GUI for YUV player using tkinter"""
from tkinter import *
from yuv_seq import YUV_sequence, YUV_frame

class MainDiag(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("YUV Player")
        self.pack(fill = BOTH, expand=1)

        menubar = Menu(self.parent)
        self.parent.config(menu = menubar)

        filemenu = Menu(menubar)
        filemenu.add_command(label="Open", command=self.onOpen)
        menubar.add_cascade(label="File", menu=filemenu)

        self.txt = Text(self)
        self.txt.pack(fill = BOTH, expand=1)

    def onOpen(self):
        ftypes = [('YUV files', '*.yuv'), ('All files', '*')]
        fl = filedialog.askopenfilename(filetypes=ftypes)
        if fl != '':
            text = self.readFile(fl)
            self.txt.insert(END, text)
    def readFile(self, filename):
        self.seq = YUV_sequence()
        [width, hieight, fps, depth] = self.seq.get_seq_params(filename)
        ret = self.seq.open_file(filename, width, height, fps, depth)

if __name__ == '__main__':
    root = Tk()
    diag = MainDiag(root)
    root.mainloop()
