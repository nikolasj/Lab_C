#!/usr/bin/env python
# Script to clone all the github repos that a user is watching

import subprocess
# test message
print("Start!")
print("----------------------------------")

subprocess.call('git pull --no-edit https://github.com/nikolasj/Lab_C.git feature', shell=True)
subprocess.call('touch test.txt', shell=True)
subprocess.call('git diff >> test.txt', shell=True)

print("----------------------------------")
print("Finish!")



# subprocess.call('echo "start"', shell=True)
# subprocess.call('mkdir /home/cm/test_git/', shell=True)
# subprocess.call('cd /home/cm/test_git/; echo "one" | git clone https://github.com/nikolasj/Lab_C.git; echo "two"', shell=True)
# subprocess.call('git clone https://github.com/nikolasj/Lab_C.git', shell=True)
# subprocess.call('echo "finish"', shell=True)