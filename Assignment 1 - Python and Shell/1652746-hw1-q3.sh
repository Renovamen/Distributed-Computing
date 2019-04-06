#! /bin/bash
log="./1652746-hw1-q3.log"
exec 2>>$log

File=1652746-hw1-q2.log

# 行数
cat $File | wc -l >>$log

# 第一行和最后一行输出结果的时间戳之间的时间差
start_time=$(awk '(NR==1) {print $1}' $File)
end_time=$(awk 'END {print $1}' $File)
start_time_stamp=`date -d $start_time +%s`
end_time_stamp=`date -d $end_time +%s`
interval_time=$(($end_time_stamp - $start_time_stamp))
echo $interval_time >>$log

#5分钟内系统负载总体平均值
ave_load=$(awk -F ',' '{sum+= $4};END {print sum/100}' $File)
echo $ave_load >>$log

#质数行内容、质数行的字符总数.
for i in `seq 100`
do
    for((j=2;j<=i-1;j++))
    do
         [ $((i%j)) -eq 0 ] &&  break 
    done
         [ $j -eq $i ] && sed -n "$i"p $File >>$log && sum=$(expr $sum + $(sed -n "$i"p $File | wc -m))
done
echo $sum >>$log