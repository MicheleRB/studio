# from tkinter import *
#
# running = True  # Global flag
#
# def scanning():
#     if running:  # Only do this if the Stop button has not been clicked
#         print("hello")
#
#     # After 1 second, call scanning again (create a recursive loop)
#     root.after(1000, scanning)
#
# def start():
#     """Enable scanning by setting the global flag to True."""
#     global running
#     running = True
#
# def stop():
#     """Stop scanning by setting the global flag to False."""
#     global running
#     running = False
#
# root = Tk()
# root.title("Title")
# root.geometry("500x500")
#
# app = Frame(root)
# app.grid()
#
# start = Button(app, text="Start Scan", command=start)
# stop = Button(app, text="Stop", command=stop)
#
# start.grid()
# stop.grid()
#
# root.after(1000, scanning)  # After 1 second, call scanning
# root.mainloop()
#
#
#
#
#
# import threading
# import time
# import tkinter as tk
# from tkinter import messagebox
#
#
# def do_slow_stuff():
#     for i in range(1, 5):
#         print(i, '...')
#         time.sleep(1)
#     print('done!')
#
#
# def check_if_ready(thread):
#     print('check')
#     if thread.is_alive():
#         # not ready yet, run the check again soon
#         root.after(200, check_if_ready, thread)
#     else:
#         messagebox.showinfo("Ready", "I'm ready!")
#
#
# def start_doing_slow_stuff():
#     thread = threading.Thread(target=do_slow_stuff)
#     thread.start()
#     root.after(200, check_if_ready, thread)
#
#
# root = tk.Tk()
# tk.Button(root, text="Start", command=start_doing_slow_stuff).pack()
# root.mainloop()
#
#


import sys
from subprocess import Popen
from tkinter import Tk, StringVar
import tkinter as tk
#import ttk

START, STOP = "start", "stop"

# just some arbitrary command for demonstration
cmd = [sys.executable, '-c', """import sys, time
print("!")
sys.stdout.flush()
for i in range(30):
    sys.stdout.write("%d " % i)
    sys.stdout.flush()
    time.sleep(.05)
"""]


class App(object):
    def __init__(self, parent):
        self.process = None
        self.after = parent.after
        self.command = START
        self.button_text = None
        self.progressbar = None
        self.make_widgets(parent)

    def make_widgets(self, parent):
        parent = tk.Frame(width=500, height=300, bg="lightgrey")
        parent.pack()
        #self.progressbar = tk..Progressbar(parent, length=200,
       #                                   mode='indeterminate')
        #self.progressbar.pack()
        self.button_text = StringVar()
        self.button_text.set(self.command)
        self.button_color = StringVar()
        self.button_color.set('green')
        button = tk.Button(parent, textvariable=self.button_text,
                            command=self.toggle, bg=self.button_color)
        button.pack()
        button.focus()

    def toggle(self, event_unused=None):
        if self.command is START:
            try:
                self.start_process()
            except:
                #self.progressbar.stop()
                raise
            self.command = STOP
            self.button_text.set(self.command)
        else:
            assert self.command is STOP
            self.stop_process()

    def stop(self):
        #self.progressbar.stop()
        self.command = START
        self.button_text.set(self.command)

    def start_process(self):
        print(dir(self))
        self.process = Popen(cmd)

        def poller():
            if self.process is not None and self.process.poll() is None:
                # process is still running
                self.after(delay, poller)  # continue polling
            else:
                self.stop()
        delay = 100  # milliseconds
        self.after(delay, poller)

    def stop_process(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            # kill process in a couple of seconds if it is not terminated
            self.after(2000, kill_process, self.process)
        self.process = None


def kill_process(process):
    if process is not None and process.poll() is None:
        process.kill()
        process.wait()


if __name__ == "__main__":
    root = Tk()
    app = App(root)

    def shutdown():
        app.stop_process()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", shutdown)
    root.bind('<Return>', app.toggle)
    root.mainloop()