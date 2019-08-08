#!/usr/bin/env bash
PID=`ps -ef|grep gunicorn|grep -v grep|grep rman.app:APP|sed -n '1p'|awk '{print $ 2}'`

if [[ "x${PID}" == "x" ]]
then
  echo '程序没有启动，忽略！'
else
  pstree -p ${PID}
fi