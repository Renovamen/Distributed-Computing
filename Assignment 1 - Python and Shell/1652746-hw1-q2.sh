#! /bin/bash
log="./1652746-hw1-q2.log"
exec 2>>$log

for i in `seq 100` 
do
	uptime >>$log
	sleep 10
done
