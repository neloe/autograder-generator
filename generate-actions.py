import sys
import glob
import os

import json

WORKFLOW_YML='''    name: GitHub Classroom Workflow

    on: [push]

    jobs:
      build:
        name: Autograding
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - uses: actions/setup-java@v1
            with:
              java-version: '11'
          - uses: education/autograding@v1'''

def parse_tests(fname):
    classname = ''
    testnames = []
    with open(fname, 'r') as f:
        content = [x.strip() for x in f.readlines() if x.strip()!='']
    for i,l in enumerate(content):
        if 'class' in l and 'public' in l:
            classname = l.split()[2]
        if 'public' in l and 'void' in l and '@Test' in content[i-1]:
            testnames.append(l.split()[2][:-2])
    return classname,testnames

def action_dict(cname, tname):
    return {'name': '{}::{}'.format(cname, tname), 'run':'gradle clean test --tests *{}.{}'.format(cname,tname), 'timeout':10}

def discover_tests(projdir):
    return glob.glob(os.path.join(projdir,'src','test','**','*.java'), recursive=True)

def build_actions_list(projdir):
    files = discover_tests(projdir)
    actions = []
    for f in files:
        cname, tnames = parse_tests(f)
        actions.extend([action_dict(cname, tname) for tname in tnames])
    return actions

def distribute_points(actions, points):
    base = int(points * 100 / len(actions))
    plist = [base * .01] * len(actions)
    remainder = int(points * 100) - (base * len(actions))
    for i in range(remainder):
        plist[i] += .01
    for a,p in zip(actions, plist):
        a['points'] = 1 #round(p, 2)
    return {1}#set([round(p, 2) for p in plist])


#actions = build_actions_list(sys.argv[1])
#distribute_points(actions, float(sys.argv[2]))

import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb

class TestGen(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.actions = []
        self.proj_dir = ''

        self.proj_btn = tk.Button(self, text='Project path', command = self.get_proj_path)
        self.proj_btn.pack()

        self.ptsvar = tk.StringVar()
        self.ptsvar.set("0")

        self.ptsvar.trace_add('write', self.update_stats)
        
        ptsframe = tk.Frame(self)
        tk.Label(ptsframe, text='Total Points:').pack(side=tk.LEFT)
        tk.Entry(ptsframe, textvariable=self.ptsvar).pack(side=tk.LEFT)
        ptsframe.pack()

        self.go_btn = tk.Button(self, text='Generate test files', command=self.write_files)
        self.go_btn.pack()
        self.go_btn['state']=tk.DISABLED

        self.ntestsvar = tk.IntVar()
        self.ptspervar = tk.StringVar()
        dataframe = tk.Frame(self)
        tk.Label(dataframe, text='Number of tests:').pack(side=tk.LEFT)
        tk.Label(dataframe, textvar = self.ntestsvar).pack(side=tk.LEFT)
        tk.Label(dataframe, text='Points per test:').pack(side=tk.LEFT)
        tk.Label(dataframe, textvar=self.ptspervar).pack(side=tk.LEFT)

        dataframe.pack()

        self.pack()


    def get_proj_path(self):
        self.proj_dir=tkfd.askdirectory(mustexist=True)
        self.proj_btn['text'] = self.proj_dir
        self.actions = build_actions_list(self.proj_dir)
        self.update_stats()

    def update_stats(self, *args):
        self.ntestsvar.set(len(self.actions))
        if len(self.actions) > 0:
            pts = 0
            try:
                pts = float(self.ptsvar.get())
            except ValueError:
                pass
            self.ptspervar.set(','.join(map(str,distribute_points(self.actions, pts))))
            self.go_btn['state']=tk.NORMAL
        else:
            self.go_btn['state']=tk.DISABLED
            self.ptspervar.set('')

    def write_files(self):
        config_dir = os.path.join(self.proj_dir, '.github')
        workflows_dir = os.path.join(config_dir, 'workflows')
        classroom_dir= os.path.join(config_dir, 'classroom')

        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
        if not os.path.isdir(workflows_dir):
            os.mkdir(workflows_dir)
        if not os.path.isdir(classroom_dir):
            os.mkdir(classroom_dir)
        with open(os.path.join(workflows_dir, 'classroom.yml'), 'w') as f:
            f.write(WORKFLOW_YML)
        with open(os.path.join(classroom_dir, 'autograding.json'), 'w') as f:
            json.dump({'tests':self.actions}, f, indent=4)

        self.actions.clear()
        self.ptsvar.set('0')
        self.update_stats()
        tkmb.showinfo(message='Files written to {}'.format(config_dir)) 


if __name__ == "__main__":
    root = tk.Tk()
    app = TestGen(root)
    app.mainloop()
