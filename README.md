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
2. 执行命令:

```
# 部署和安装依赖
sh deploy.sh
cd /opt/deploy/rock4tools/rtsf-manager
# 启动
sh start.sh

# 返回正常，说明启动成功
curl http://127.0.0.1:5004/httpcase/tset
```




# 测试集列表

- 获取所有项目的测试集    
    
    ``` dev
    GET /httpcase/tset
    return 
    {
        "message": "Query all data  success in page: 1 size: 10.",
        "result": {
            "total": 1,
            "tsets": [
                {
                    "cases": [],
                    "pj_id": 1,
                    "pj_module_name": "试试",
                    "pj_name": "士大夫",
                    "tset_c_time": "2019-07-22 16:23:40",
                    "tset_id": 1,
                    "tset_name": "问问",
                    "tset_responsible": "",
                    "tset_tester": "",
                    "tset_u_time": "2019-07-22 16:23:40"
                }
            ]
        },
        "status": true
    }
    ```

- 新增测试集    
    
    ``` dev
    POST /httpcase/tset
    
    data {
        pj_name: pj_name,
        pj_module_name: pj_module_name, 
        tset_name: tset_name
    }
    ```
    
- 删除测试集
       
    ``` dev
    DELETE /httpcase/tset?tset_ids='1,2,3,4,5'
    ```
    
- 更新测试集
        
    ``` dev
    /httpcase/tset?tset_id=3
    {       
        tset_name: tset_name,
        tset_tester: tset_tester,
        desc: 'sdfsdf'
    }
    ```

# 测试集详情

- 获取指定测试集详情
        
    ``` dev
    GET /httpcase/tset?tset_id=xx
    return {
        "message": "Query all data  success in page: 1 size: 10.",
        "result": 
        {
            "total": 1,
            "tsets": [
                {
                    "cases": [],
                    "pj_id": 1,
                    "pj_module_name": "试试",
                    "pj_name": "士大夫",
                    "tset_c_time": "2019-07-22 16:23:40",
                    "tset_id": 1,
                    "tset_name": "问问",
                    "tset_responsible": "",
                    "tset_tester": "rock feng1",
                    "tset_u_time": "2019-07-22 16:23:40"
                }
            ]
        },
        "status": true
    }
    ```

- 在指定测试集中，新增测试用例
       
    ``` dev
    POST /httpcase/tset?tset_id=xx
    data {                   
        name: name,        
        call_api: call_api,
        call_suite: call_suite,
        url: url,
        method: method,
        glob_var: glob_var,
        glob_regx: glob_regx,
        pre_command: pre_command,
        headers: headers,
        body: body,
        files: files,
        post_command: post_command,
        verify: verify,             
    }
    name 必填
    必填其一: call_api  or  call_suite  or 手动填请求(url和method必填)
    ```
    
- 在指定测试集中，删除测试用例

    ``` dev
    DELETE /httpcase/tset?tcase_ids='1,2,3,4,5'
    ```    

- 在指定测试集中，更新测试用例
    
    ``` dev
    PUT /httpcase/tset?tcase_id=32342  
    data 同 POST的数据
    {                   
        name: name,        
        call_api: call_api
    }
    ```


# API
前端：编辑和新增，表单都会带数据的问题
- 获取指定项目的API
        
    ``` dev
    GET /httpcase/api?pj_id=xx
    return {
        "message": "Query all data  success.",
        "result": {
            "apis": [
                {
                    "api_def": "sdsdf",
                    "body": "{}",
                    "files": "{}",
                    "glob_regx": "{}",
                    "glob_var": "{}",
                    "headers": "{}",
                    "id": 1,
                    "method": "GET",
                    "post_command": "[]",
                    "pre_command": "[]",
                    "url": "http://www.baidu.com",
                    "verify": "[]"
                }
            ],
            "pj_module_name": "试试",
            "pj_name": "士大夫",
            "tset_name": "xxx",
            "tset_responsible": "xxx",
            "tset_tester": "xxx"
        },
        "status": true
    }
    ```
    
- 新增指定项目的API
        
    ``` dev
    POST /httpcase/api?pj_id=xx
    data {
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
    },
    api_def, url, method 必填
    ```

- 删除指定项目的API
        
    ``` dev
    DELETE /httpcase/api?tapi_id=xx
    ```

- 更新指定项目的API
    
    ``` dev
    PUT /httpcase/api?tapi_id=xx
    data 同 POST
    ```


# SUITE
- 获取项目中的suite
       
    ``` dev
    GET /httpcase/suite?pj_id=xx
    return {
        "message": "Query all data  success.",
        "result": {
            "pj_module_name": "试试",
            "pj_name": "士大夫",
            "suites": [
                {
                    "cases": [
                        {
                            "api": "sdsdf",
                            "name": "EFEFEFE"
                        }
                    ],
                    "id": 1,
                    "suite_def": "sssss"
                }
            ],
            "tset_name": "xxx",
            "tset_responsible": "xxx",
            "tset_tester": "xxx"
        },
        "status": true
    }
    ```

- 新增项目中的suite
    ``` mock
    POST /casesuites/list
    data {
        suite_def: "get_xxx()"
    }
    ```
    
    ``` dev
    POST /httpcase/suite?pj_id=xx
    data {
        suite_def: "get_xxx()",
        cases: [{"api":"sdsdf", "name":"asdf"}]
    }
    必填: suite_def 、 cases
    cases 可以是 空的list, 里边的值的格式是: {"api":"xxx", "name":"xxx"}
    ```
    
    
- 删除项目中的suite
    
    ``` dev
    DELETE /httpcase/suite?tsuite_id=xx
    ```

- 更新项目中的suite
    
    ``` dev
    PUT /httpcase/suite?tsuite_id=xx
    {
        suite_def: "get_xxx()",
        cases: [
            {name: case1,api: "call_api_1"},
            {name: case2,api: "call_api_2"}
        ]
    }
    必填: cases
    更新的时候，cases 不可以是空的list, 里边的值的格式是: {"api":"xxx", "name":"xxx"}
    ```
 

