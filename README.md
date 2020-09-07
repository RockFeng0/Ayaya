gitlab & github
# rtsf自动化系列框架管理平台
- 基于python，采用技术栈flask+vue.js,进行前后端分离
- 具体包括一些flask的扩展,如flask_login,flask_sqlalchemy,flask_migrate等,
- 也包括一些vue的扩展，如axios,element-ui等

# rtsf-manager
主要是后端的实现，提供业务逻辑的接口

# 其他备忘
- (test_pj) C:\d_disk\auto\git\rtsf-manager\rman>set flask_app=manager
- (test_pj) C:\d_disk\auto\git\rtsf-manager\rman>flask db init -d migrations_testing



# rtsf-manager 后台安装和部署

1. 下载rtsf-manager.zip包和deploy.sh, 放在同一目录下

> 因为还没发布，临时部署, 所以 APP_ENV = 'testing' ， 不需要修改; 如果有异步任务，还要修改下celeryconfig.py文件

2. 执行命令:

```
# 部署和安装依赖
sh deploy.sh
cd /opt/deploy/rock4tools/rtsf-manager

# 注意 windows redis 和 celery 只有这个版本适用, 而且最好使用python2.7安装
# pip install redis==2.10.6
# pip install celery==3.1.25 

# 启动
sh start.sh

# 返回正常，说明启动成功
curl http://127.0.0.1:5004/httpcase/tset
```
3. 异步任务， 测试环境

```
- celery消费
(test_pj) C:\d_disk\auto\git\rtsf-manager>celery -A rman.manager worker --loglevel info -c 1

- redis服务
C:\f_disk\BaiduNetdiskDownload\redis-64.3.0.503>redis-server.exe redis.windows.conf


注意:
celery
# -A选项是应用中的celer对象，作为 Task(生产者)
# worker 作为Workers(消费者)

redis,作为Brokers，指任务队列本身
# redis.windows.conf设置了redis连接密码：  requirepass 123456
# 下载 redis windows命令行工具，执行命令，启动redis服务器

```
   

# API

1. 测试集列表 
    
```
# 获取所有项目的测试集  
GET /httpcase/tset?page=1&size=10

# 新增测试集   
POST /httpcase/tset
params:
    pj_name: 某某项目
    pj_module_name: 某某模块
    tset_name:  某某测试
    
# 更新测试集
PUT /httpcase/tset?tset_id=3
params:
    tset_name: 某某项目
    tset_tester: 某某模块
    desc:  某某测试
    
# 删除测试集
DELETE /httpcase/tset?tset_ids='1,2,3,4,5'
    
```


2. 测试集详情

```
# 获取指定测试集详情
GET /httpcase/tset?tset_id=xx

# 在指定测试集中，新增测试用例
POST /httpcase/tset?tset_id=xx
params:
    name: "",        
    call_api: "",
    call_suite: "",
    url: "",
    method: "",
    glob_var: {},
    glob_regx: {},
    pre_command: [],
    headers: {},
    body: {},
    files: {},
    post_command: [],
    verify: []

  name 必填; 必填其一: call_api  or  call_suite  or 手动填请求(url和method必填)
      
    
# 在指定测试集中，更新测试用例
PUT /httpcase/tset?tcase_id=32342  
params:
    name: name,        
    call_api: call_api
    
# 在指定测试集中，删除测试用例
DELETE /httpcase/tset?tcase_ids='1,2,3,4,5'
    
```

3. 测试组件(API)

```
# 获取指定项目的API
GET /httpcase/api?pj_id=xx

# 新增指定项目的API
POST /httpcase/api?pj_id=xx
params:
    api_def: "get_xxx()",
    url: http://www.baidu.com,
    method: methods,
    glob_var: {
        username: sdf,
        password: sdf,
    },
    glob_regx: {
        id_card: sdf,
        regx: /[a-z][A-Z]/,
    },
    pre_command: [],        
    headers: {},
    body: {},
    files: {
        file1: 'c:/test1.txt',
        file2: 'c:/test2.txt',
    },
    post_command: [],
    verify: [],

  api_def 必填
      
    
# 更新指定项目的API
PUT /httpcase/api?tapi_id=xx  
params:
    同 POST
    
# 删除指定项目的API
DELETE /httpcase/api?tapi_id=xx
    
```

4. 测试套件(SUITE)

```
# 获取项目中的suite
GET /httpcase/suite?pj_id=xx

# 新增项目中的suite
POST /httpcase/suite?pj_id=xx
params:
    suite_def: "get_xxx()",
    cases: [{"api":"sdsdf", "name":"asdf"}]
  
  必填: suite_def 、 cases
 cases 可以是 空的list, 里边的值的格式是: {"api":"xxx", "name":"xxx"}
    
# 更新项目中的suite
PUT /httpcase/suite?tsuite_id=xx
params:
    suite_def: "get_xxx()",
    cases: [
        {name: case1,api: "call_api_1"},
        {name: case2,api: "call_api_2"}
    ]
    
# 删除项目中的suite
DELETE /httpcase/suite?tsuite_id=xx
    
```

 
5. 执行异步任务-- 目前仅支持 http(s)自动化测试用例的脚本任务

```
# 分页获取任务
GET http://127.0.0.1:5000/rm_task/case?page=1&size=10

# 添加任务
POST http://127.0.0.1:5000/rm_task/case
params:
    cases: [{"name":"百度一哈", "desc":"百度哇"}, {"name":"百度二哈", "desc":"百度二哇"}]

# 更新任务
PUT http://127.0.0.1:5000/rm_task/case?task_id=1
params:
    case: xxx(必填)
    desc: xxx 
    
# 删除任务
DELEETE http://127.0.0.1:5000/rm_task/case?task_id=1

# 执行单个任务
GET http://127.0.0.1:5000/rm_task/run?task_ids=1
# 执行批量任务
GET http://127.0.0.1:5000/rm_task/run?task_ids=1,2,3,4

# 获取单个任务状态
GET http://127.0.0.1:5000/rm_task/status?task_ids=1
# 获取批量任务状态
GET http://127.0.0.1:5000/rm_task/status?task_ids=1,2,3,4

# 查看任务执行报告
GET http://127.0.0.1:5000/rm_task/report?task_id=1
    
```
