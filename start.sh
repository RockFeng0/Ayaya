#!/bin/bash
# 项目主目录
BASE_DIR=/opt/deploy/rock4tools/rtsf-manager
cd ${BASE_DIR}

# 自动创建日志日志，防止目录不存在时报错
if [ ! -d "rman/logs" ]
then
    mkdir -p rman/logs
fi

# 清除原来的pyc文件
find ${BASE_DIR} -type f -name *.pyc|xargs rm -f


# 运行.bashrc文件，初始化个人设置的一些环境变量, 如:
#   redis的变量配置
#   export REDIS_HOST=127.0.0.1
#   export REDIS_PORT=6379
#   export REDIS_PASS=58cstest@abc

source ~/.bashrc

# 选择对应的虚拟环境
workon py3rtsfpj

# 启动异步任务
# celery -A rman.tasks worker &

# 启动python web容器gunicorn
# -b 表示 gunicorn 开发的访问地址 
# -w 表示开启多少个线程
gunicorn -w 1 -b 0.0.0.0:5004 -t 120 --threads 8 rman.app:APP >> rman.log 1>&1 2>&1  &

