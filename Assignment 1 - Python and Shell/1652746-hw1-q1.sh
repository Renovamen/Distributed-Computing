#!/bin/bash
log="./1652746-hw1-q1.log"
exec 2>>$log


sum=0

for i in `seq 100`
do
    for((j=2;j<=i-1;j++))
    do
         [ $((i%j)) -eq 0 ] &&  break      
    done
         [ $j -eq $i ] && sum=$(expr $sum + $i)
done

echo $sum>>$log