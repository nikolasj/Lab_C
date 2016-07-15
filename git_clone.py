#!/usr/bin/env python
# Script to clone all the github repos that a user is watching

import subprocess

# test message

def main():
    print("Start!")
    # subprocess.call('git pull --no-edit https://github.com/nikolasj/Lab_C.git feature', shell=True)
    # subprocess.call('git diff feature^', shell=True)

if  __name__ ==  "__main__" :
   # print("Введите ветку:")
   # branch = input()
    main()

# subprocess.call('echo "start"', shell=True)
# subprocess.call('mkdir /home/cm/test_git/', shell=True)
# subprocess.call('cd /home/cm/test_git/; echo "one" | git clone https://github.com/nikolasj/Lab_C.git; echo "two"', shell=True)
# subprocess.call('git clone https://github.com/nikolasj/Lab_C.git', shell=True)
# subprocess.call('echo "finish"', shell=True)