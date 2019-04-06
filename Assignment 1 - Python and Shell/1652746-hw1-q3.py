#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
from dateutil.parser import parse
sys.stdout = open('1652746-hw1-q3.log', 'a')

f = open('1652746-hw1-q2.log', 'r')
line = f.readlines()

# 行数
cnt = len(line)
print(cnt)

# 第一行和最后一行输出结果的时间戳之间的时间差
start_time = parse(line[0].split(' ')[1])
end_time = parse(line[cnt - 1].split(' ')[1])
print((end_time - start_time).seconds)

# 5分钟内系统负载总体平均值
sum = 0
for i in range(0, cnt):
    sum = sum + float(line[i].split(',')[3])
print(round(sum / cnt, 4))

# 质数行内容、质数行的字符总数
sum_char = 0
for i in range(2, 100):

    for j in range(2, i):
        if(i % j == 0):
            break
    else:
        print(line[i - 1])
        sum_char = sum_char + len(line[i - 1])
print(sum_char)
