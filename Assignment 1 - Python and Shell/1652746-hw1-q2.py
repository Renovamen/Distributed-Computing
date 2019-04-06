import os
import sys
import time

sys.stdout = open('1652746-hw1-q2.log', 'a')

for i in range(1, 100):

    p = os.popen('uptime')
    x = p.read()
    print(x)
    time.sleep(10)
