#!/bin/bash
PID=`/usr/sbin/lsof -i:5004|grep -v PID|awk '{print $2}'`

if [[ "x${PID}" == "x" ]]
then
  echo "没有找到运行的进程，不需要结束"
else
  echo "当前进程PID：${PID},结束当前进程"
  kill -9 ${PID}
fi