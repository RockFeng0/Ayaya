# 安装包名称
APP_PAGKAGE_NAME=rtsf-manager.zip
BASE_DIR=/opt/deploy/rock4tools

# 判断程序目录是否存在
if [[ ! -d ${BASE_DIR} ]]
then
  mkdir -p ${BASE_DIR}
fi

# 删除原目录下的代码
if [[ -d ${BASE_DIR}/rtsf-manager ]]
then
  rm -rf ${BASE_DIR}/rtsf-manager
fi

# 解压程序包
cd ${BASE_DIR}
unzip -o ${APP_PAGKAGE_NAME} -d ${BASE_DIR}

# 选择对应的虚拟环境
source ~/.bashrc
workon py3rtsfpj

# 安装依赖, 可能镜像源要自己去捣鼓一下
cd rtsf-manager
pip install -r requirements.txt > /dev/null 1>&1
