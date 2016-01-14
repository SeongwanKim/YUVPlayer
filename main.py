"""GUI for YUV player using tkinter"""
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from yuv_seq import YUV_sequence, YUV_frame


class MainDiag(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, width=832, height=480)
        self.parent = parent
        self.initUI()
        self.data=0
        self.chn='A'
        self.play = False
        self.onOpen()

    def initUI(self):
        self.parent.title("YUV Player")
        self.pack(fill = BOTH, expand=1)

        menubar = Menu(self.parent)
        self.parent.config(menu = menubar)

        filemenu = Menu(menubar)
        filemenu.add_command(label="Open", command=self.onOpen)
        menubar.add_cascade(label="File", menu=filemenu)

        self.bind("<Configure>", self.on_resize)
        self.parent.bind("<Left>", self.prev1)
        self.parent.bind("<Right>", self.next1)
        self.parent.bind("<Shift-Left>", self.prev_sec)
        self.parent.bind("<Shift-Right>", self.next_sec)
        self.parent.bind("n", self.next_chn)
        self.parent.bind("<space>", self.play_pause)

    def onOpen(self):
        ftypes = [('YUV files', '*.yuv'), ('All files', '*')]
        fl = filedialog.askopenfilename(filetypes=ftypes)
        if fl != '':
            self.readFile(fl)

    def readFile(self, filename):
        self.seq = YUV_sequence()
        [width, height, fps, depth] = self.seq.get_seq_params(filename)
        print ([width, height, fps, depth])
        self.NumFrame = self.seq.open_file(filename, width, height, fps, depth)
        self.parent.geometry("{0}x{1}".format(width,height))
        self.showImage(0)

    def prev_sec(self, event):
        self.showImage((self.nf - self.seq.fps) % self.NumFrame)
    def next_sec(self, event):
        self.showImage((self.nf + self.seq.fps) % self.NumFrame)
    def prev1(self, event):
        self.showImage((self.nf - 1) % self.NumFrame)
    def next1(self, event=0):
        self.showImage((self.nf + 1) % self.NumFrame)

    def next_chn(self, event):
        chn = {'A':'Y', 'Y':'U','U':'V','V':'A'}
        self.chn = chn[self.chn]
        self.showImage(self.nf)

    def play_pause(self, event):
        self.play = not self.play
        if self.play:
            self.parent.title("YUV Player <PLAY>")
        else:
            self.parent.title("YUV Player <PAUSE>")
        self.showImage()

    def showImage(self, FrameNum = -1):
        import time
        se = time.time()
        if FrameNum >= 0:
            self.nf = FrameNum
            self.data = self.seq.getFrame(FrameNum)
        elif not self.data:
            return
        load = Image.fromarray(self.data.GetImg(self.chn, self.winfo_width(), self.winfo_height()))
        render = ImageTk.PhotoImage(load)
        # labels can be text or images
        img = Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)
        if self.play:
            cur = time.time()
            rem = round((1./self.seq.fps - (cur-se)) * 1000)
            if rem < 0:
                print("delayed ", rem)
                self.next1()
            else:
                self.after(rem, self.next1)

    def on_resize(self, event):
        self.showImage(-1)


if __name__ == '__main__':
    root = Tk()
    diag = MainDiag(root)
    root.mainloop()
