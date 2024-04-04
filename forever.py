#!/usr/local/lib/python3.7from subprocess import Popenimport sys

filename = sys.argv[1]while True:
    print("\nStarting " + filename)
    p = Popen("python3 " + filename, shell=True)
    p.wait()
