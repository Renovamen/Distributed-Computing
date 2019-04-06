#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.stdout = open('1652746-hw1-q1.log', 'a')

sum = 0

for i in range(2, 100):

    for j in range(2, i):
        if(i % j == 0):
            break
    else:
        sum += i

print(sum)
