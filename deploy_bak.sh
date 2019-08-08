#!/bin/bash

# 安装包名称
APP_PAGKAGE_NAME=rtsf-manager.tgz

# 项目主目录
BASE_DIR=/opt/deploy/rtsf-manager

# 打包
tar -zcf ${APP_PAGKAGE_NAME} ./*

# 判断程序目录是否存在
if [[ ! -d ${BASE_DIR} ]]
then
  mkdir -p ${BASE_DIR}
fi

# 删除原目录下的代码
if [[ -d ${BASE_DIR} ]]
then
  rm -rf ${BASE_DIR}/*
fi

# 分发新包
mv ${APP_PAGKAGE_NAME} ${BASE_DIR}

# 解压新安装包
cd ${BASE_DIR} && tar -zxf ${APP_PAGKAGE_NAME} && rm -f ${APP_PAGKAGE_NAME}

# 自动创建日志日志，防止目录不存在时报错
if [ ! -d "rtsf-manager/logs" ]
then
    mkdir -p rtsf-manager/logs
fi

# 选择对应的虚拟环境
source ~/.bashrc
workon py3rtsfpj

# 安装依赖
pip install -r requirements/requirements.txt > /dev/null 1>&1
