from flask_restful import Resource
from flask import request,jsonify,json
import jsonschema,json
import logging
from rman.app import db
from datetime import datetime
from rman.app.models.ut_rman_testset import TestSetModel
from rman.app.models.ut_rman_httpcase import HttpCaseModel
from rman.app.models.ut_rman_testcase import TestCaseModel
from rman.app.models.ut_rman_project import ProjectModel
from rman.app.models.ut_rman_module import ModuleModel
from rman.app.common.utils.other.alchemy import AlchemyJsonEncoder, has_module
from flask_restful.reqparse import RequestParser

class TestCaseConfigView(Resource):
    #添加用例
    def post(self):
        dataForm = request.get_json(force=True)
        try:
            schema = {
                'type': 'object',
                'required':['project_id','project_name','case_name','case_interface','module_name','url','request_type'],
                'properties': {
                    'project_id': {'type': 'integer', 'minLength': 1},
                    'project_name': {'type': 'string', 'minLength': 1},
                    'case_name': {'type': 'string', 'minLength': 1},
                    'case_interface': {'type': 'string', 'minLength': 1},
                    'module_name': {'type': 'string', 'minLength': 1},
                    'url': {'type': 'string', 'minLength': 1},
                    'request_type': {'type': 'integer', 'minLength': 1},
                    'params': {'type': 'object'},
                    'headers': {'type': 'array'},
                    'assert': {'type': 'array'},
                    'local_var': {'type': 'array'},
                    'desc': {'type': 'string'},
                    'update_person': {'type': 'string'}
                }
            }
            jsonschema.validate(dataForm, schema)
            #准备插入httpcase表数据
            #apply_case中存放的是set_id,case_name,params传入结构{‘input’：{}，‘select’:{'key_name':'set_id/case_name/var_local'}}
            #从params中的select构造apply_case,select中参数的value值的格式是以/分割的字符串
            apply_case = []
            body = []
            print(dataForm['params']['select'])
            if dataForm['params']['select']:
                # post_command = {}
                for value in dataForm['params']['select']:
                    value_dict = value['value'].split('/')
                    apply_case.append({'key_name':value['key'],'case_id':value_dict[0],'case_name':value_dict[1],'var_local_name':value_dict[2],'var_local':value_dict[3],'desc':value['desc']})
                    body.append({'key':value['key'],'value':'$'+value_dict[2],'desc':''})
            body = dataForm['params']['input']+body
            if dataForm['local_var']:
                for index in range(len(dataForm['local_var'])):
                    dataForm['local_var'][index]['type'] = 'json'
                    dataForm['local_var'][index]['index'] = 0
            test_httpcase_data = {
                'pre_command': json.dumps(apply_case),
                'url': dataForm['url'],
                'method': dataForm['request_type'],
                'headers': json.dumps(dataForm['headers']) if 'headers' in dataForm else '[]',
                'body': json.dumps(body) if body else '[]',
                'verify': json.dumps(dataForm['assert']) if 'assert' in dataForm else '[]',
                'post_command': json.dumps(dataForm['local_var']) if 'local_var' in dataForm else '[]',
                'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            #构造testcase表中数据，如果modole_name已经在module中存在，则不插入module直接将已有的module_id插入testcase
            module = has_module(dataForm['project_id'], dataForm['module_name'])
            if len(module)==0:
                #构造module数据库数据
                testmodule_data = {
                    'name': dataForm['module_name'],
                    'project_id': dataForm['project_id'],
                    'desc': dataForm['desc'] if 'desc' in dataForm else '',
                    'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                test_module_model = ModuleModel()
                db.session.add(AlchemyJsonEncoder.to_alchemy(test_module_model, testmodule_data))
                db.session.flush()
                module_id = test_module_model.id
            else:
                module_id = module[0][0]

            test_httpcase_model = HttpCaseModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(test_httpcase_model, test_httpcase_data))
            db.session.flush()
            httpcase_id = test_httpcase_model.id
            testcase_data = {
                'name': dataForm['case_name'],
                'interface_name': dataForm['case_interface'],
                'case_type': 1001,
                'case_id': httpcase_id,
                'module_id': module_id,
                # 'test_set_id': set_id,
                'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            testcase_model = TestCaseModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(testcase_model, testcase_data))
            db.session.commit()
        except Exception as e:
            logging.error('add case error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"用例提交失败,{}".format(str(e))}
        return {"code": 200, "msg": "用例添加成功"}
    #获取用例列表
    def get(self):
        page = request.args.get('page', 1, type=int)
        num = request.args.get('num', 10, type=int)
        department_id = request.args.get('department_id', type=int)
        case_name = request.args.get('case_name','', type=str)
        case_list = []
        if department_id<=0:
            return {'code': 402,'msg':'部门ID未传入'}
        try:
            project_id_list = db.session.query(ProjectModel.id).filter(ProjectModel.is_delete == 0,ProjectModel.department_id == department_id).all()
            to_list = []
            for i in project_id_list:
                to_list = to_list + list(i)
            project_id_list = to_list
            if case_name:
                base_condition = db.session.query(ProjectModel.name ,ProjectModel.id,ModuleModel.name,TestCaseModel.name,TestCaseModel.case_id,TestCaseModel.id, TestCaseModel.update_time).outerjoin(ProjectModel,ModuleModel.project_id==ProjectModel.id).join(TestCaseModel,TestCaseModel.module_id == ModuleModel.id).filter(TestCaseModel.is_delete==0,ModuleModel.is_delete==0,ModuleModel.project_id.in_(project_id_list),TestCaseModel.name.like('%{keyword}%'.format(keyword=case_name))).order_by(TestCaseModel.update_time.desc())
                base_data = base_condition.paginate(page=page, per_page=num).items

            else:
                base_condition = db.session.query(ProjectModel.name,ProjectModel.id, ModuleModel.name, TestCaseModel.name,TestCaseModel.case_id, TestCaseModel.id, TestCaseModel.update_time).outerjoin(ProjectModel,ModuleModel.project_id == ProjectModel.id).join(TestCaseModel, TestCaseModel.module_id == ModuleModel.id).filter(TestCaseModel.is_delete == 0,ModuleModel.is_delete == 0,ModuleModel.project_id.in_(project_id_list)).order_by(TestCaseModel.update_time.desc())
                base_data = base_condition.paginate(page=page, per_page=num).items
            if base_data:
                key_list = ('project_name','project_id', 'module_name', 'case_name', 'case_id', 'testcase_id','update_time')
                case_list = [dict(zip(key_list, case)) for case in base_data]
                for index in range(len(case_list)):
                    case_list[index]['responsible'] = ''
                    case_list[index]['update_time'] = case_list[index]['update_time'].strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logging.error('get case list error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取用例列表失败,{}".format(str(e))}
        return {'code': 200, 'page': page, 'num':num,'total':base_condition.count(), 'data': case_list}
    #编辑用例
    def put(self):
        #修改时间，12/24 将set_id改成case_id
        dataForm = request.get_json(force=True)
        try:
            if dataForm:
                if 'case_id' not in dataForm.keys():
                    return {'code': 4101, 'msg': u"case_id must be used "}
                apply_case = []
                body = []
                if dataForm['params']['select']:
                    # post_command = {}
                    #将依赖数据和填写body合并
                    for value in dataForm['params']['select']:
                        value_dict = value['value'].split('/')
                        apply_case.append(
                            {'key_name': value['key'], 'case_id': value_dict[0], 'case_name': value_dict[1],
                             'var_local_name': value_dict[2], 'var_local': value_dict[3], 'desc': value['desc']})
                        body.append({'key': value['key'], 'value': '$' + value_dict[2], 'desc': value['desc']})

                body = dataForm['params']['input'] + body
                if dataForm['local_var']:
                    for index in range(len(dataForm['local_var'])):
                        dataForm['local_var'][index]['type'] = 'json'
                        dataForm['local_var'][index]['index'] = 0
                dataForm['params'] = body
                dataForm['apply_case'] = apply_case
                # 入参字段和数据库字段不一致，做个映射
                input_relation_output = {
                    'case_name': 'TestCaseModel.name',
                    'project_id': 'TestCaseModel.project_id',
                    # 'project_name': 'TestSetModel.name',
                    'apply_case': 'HttpCaseModel.pre_command',
                    'case_interface': 'TestCaseModel.interface_name',
                    'request_type': 'HttpCaseModel.method',
                    'headers': 'HttpCaseModel.headers',
                    'params': 'HttpCaseModel.body',
                    'url':'HttpCaseModel.url',
                    'assert': 'HttpCaseModel.verify',
                    'local_var': 'HttpCaseModel.post_command',
                    # 'post_command':'HttpCaseModel.post_command',
                    'desc': 'TestCaseModel.desc',
                }
                # 判断是否传入了module_name
                if 'module_name' in dataForm.keys():
                    module_id = has_module(dataForm.get('project_id'), dataForm.get('module_name'))
                    if len(module_id)==0:
                    # 构造module数据库数据
                        testmodule_data = {
                            'name': dataForm['module_name'],
                            'project_id': dataForm['project_id']
                        }
                        test_module_model = ModuleModel()
                        db.session.add(AlchemyJsonEncoder.to_alchemy(test_module_model, testmodule_data))
                        db.session.flush()
                        module_id = test_module_model.id
                    else:
                        module_id = module_id[0][0]
                    dataForm['module_id'] = module_id
                    input_relation_output['module_id'] = 'TestCaseModel.module_id'
                case_id = int(dataForm['case_id'])
                insert_dict = {}
                for key in dataForm.keys():
                    if key in input_relation_output.keys():
                        update_table = input_relation_output[key].split('.')[0]
                        update_column = input_relation_output[key].split('.')[1]
                        if update_column in ['body','verify','post_command','headers']:
                            update_value = json.dumps(dataForm[key])
                        else:
                            update_value = dataForm[key]
                        if update_table in insert_dict.keys():
                            insert_dict[update_table][update_column] = update_value
                        else:
                            insert_dict[update_table] = {update_column:update_value}
                        insert_dict[update_table]['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for key in insert_dict.keys():
                    if key == 'HttpCaseModel':
                        db.session.query(HttpCaseModel).filter_by(id=case_id).update(AlchemyJsonEncoder.to_alchemy_json(HttpCaseModel, insert_dict[key]))
                    if key == 'TestCaseModel':
                        db.session.query(TestCaseModel).filter_by(case_id=case_id).update(AlchemyJsonEncoder.to_alchemy_json(TestCaseModel, insert_dict[key]))
                db.session.commit()
        except Exception as e:
            logging.error('update case error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取失败,{}".format(str(e))}
        return {"code": 200, "msg": "成功"}
    #删除用例
    def delete(self):
        #删除用例，入参case_id
        parser = RequestParser()
        parser.add_argument(
            'case_id',
            type=int,
            required=True,
            help="case_id must be used",
        )
        try:
            case_id = parser.parse_args()['case_id']
            update_data = {'is_delete': 1}
            #获取测试集数据
            testcase_data = db.session.query(TestCaseModel).filter_by(case_id = case_id).all()
            if len(testcase_data) == 0:
                return {'code': 402, 'msg': u"不存在用例id为{}的数据".format(case_id)}
            else:
                # 更新ut_rman_testcase表中的is_delete状态为删除状态1
                db.session.query(TestCaseModel).filter_by(case_id=case_id).update(update_data)
                #更新ut_rman_httpcase表中的is_delete状态为删除状态1
                db.session.query(HttpCaseModel).filter_by(id=case_id).update(update_data)
                db.session.commit()
        except Exception as e:
            logging.error('delete case error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"用例删除失败,{}".format(str(e))}
        return {"code": 200, "msg": "用例删除成功"}
class TestCaseConfigViewList(Resource):
    #查看用例接口,点击依赖接口跳转的页面也是通过这个页面
    #输入case_id
    def get(self,id):
        case_data = {
            'case_id':0,
            'testcase_id':0,
            'httpcase_id':0,
            'project_name':'',#项目名称
            'project_id':0,#项目id
            'case_name':'',#用例名称
            'module_name':'',
            # 'apply_case':[],#依赖用例
            'case_interface':'',#用例接口名称
            'url':'',
            'request_type':0,
            'params':[],
            'headers':[],
            'assert':[],
            'local_var':[],
            'desc':''
        }
        try:
            #通过case_id获取相关数据信息
            testcase_data = db.session.query(ProjectModel.name, ProjectModel.id, ModuleModel.name, TestCaseModel.name,TestCaseModel.interface_name, TestCaseModel.id, TestCaseModel.desc).outerjoin(ProjectModel,ModuleModel.project_id == ProjectModel.id).join(TestCaseModel, TestCaseModel.module_id == ModuleModel.id).filter(TestCaseModel.is_delete == 0,ModuleModel.is_delete == 0,TestCaseModel.case_id == id).all()
            if testcase_data:
                key_list = ('project_name', 'project_id', 'module_name', 'case_name', 'interface_name','testcase_id','desc')
                testcase_list = [dict(zip(key_list, case)) for case in testcase_data][0]
                httpcase_data = AlchemyJsonEncoder.query_to_dict(db.session.query(HttpCaseModel).filter(HttpCaseModel.id == id,HttpCaseModel.is_delete == 0).all())[0]
                parmas = {'input': [], 'select': []}
                body = json.loads(httpcase_data['body'])
                if body:
                    for value in body:
                        if isinstance(value['value'], str) and '$' not in value['value']:
                            parmas['input'].append(value)
                        # else:
                        #     parmas['select'].append(value)
                apply_case = json.loads(httpcase_data['pre_command'])
                if apply_case:
                    for ac in apply_case:
                        parmas['select'].append({'key': ac['key_name'],'value': str(ac['case_id']) + '/' + ac['case_name'] + '/' + ac['var_local_name'] + '/' + ac['var_local'], 'desc': ac['desc']})
                case_data['case_id'] = id
                case_data['testcase_id'] = testcase_list['testcase_id']
                case_data['httpcase_id'] = id
                case_data['project_name'] = testcase_list['project_name']
                case_data['project_id'] = testcase_list['project_id']
                case_data['case_name'] = testcase_list['case_name']
                case_data['module_name'] = testcase_list['module_name']
                case_data['case_interface'] = testcase_list['interface_name']
                case_data['url'] = httpcase_data['url']
                case_data['request_type'] = httpcase_data['method']
                case_data['params'] = parmas if parmas else []
                case_data['headers'] = json.loads(httpcase_data['headers']) if httpcase_data['headers'] else []
                case_data['assert'] = json.loads(httpcase_data['verify']) if httpcase_data['verify'] else []
                case_data['local_var'] = json.loads(httpcase_data['post_command']) if httpcase_data['post_command'] else []
                case_data['desc'] = testcase_list['desc']
        except Exception as e:
            logging.error('get interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取失败,{}".format(str(e))}
        return {'code': 200, 'data': case_data}
    #复制用例
    def post(self):
        #入参被复制的用例的set_id,和产生的新用例的case_name
        #根据set_id查到testcase,httpcase的相关数据，插入到对应的表中
        dataForm = request.get_json(force=True)
        try:
            schema = {
                'type': 'object',
                'required':['set_id','case_name'],
                'properties': {
                    'set_id': {'type': 'integer', 'minLength': 1},
                    'case_name': {'type': 'string', 'minLength': 1}

                }
            }
            jsonschema.validate(dataForm, schema)
            case_name = dataForm['case_name']
            set_id = dataForm['set_id']
            has_case_name = db.session.query(TestSetModel).filter(TestSetModel.name == case_name,TestSetModel.is_delete == 0).all()
            if len(has_case_name) > 0 :
                return {'code': 401, 'msg': u"用例名称已存在"}
            set_data = AlchemyJsonEncoder.query_to_dict(db.session.query(TestSetModel).filter(TestSetModel.id == set_id,TestSetModel.is_delete == 0).all())[0]
            test_set_data = {
                'name': case_name,
                'responsible': '-',  # 目前没有登录信息都先给默认值
                'tester': '-',
                'project_id': set_data['project_id'],
                'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'desc': set_data['desc']
            }
            testcase_data = AlchemyJsonEncoder.query_to_dict(db.session.query(TestCaseModel).filter(TestCaseModel.test_set_id == set_id,TestCaseModel.is_delete == 0).all())[0]
            case_id = testcase_data['case_id']
            test_httpcase_data = AlchemyJsonEncoder.query_to_dict(db.session.query(HttpCaseModel).filter(HttpCaseModel.id == case_id,HttpCaseModel.is_delete == 0).all())[0]
            test_httpcase_data['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            test_httpcase_data.pop('id')
            test_httpcase_data.pop('update_time')
            test_set_model = TestSetModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(test_set_model, test_set_data))
            test_httpcase_model = HttpCaseModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(test_httpcase_model, test_httpcase_data))
            db.session.flush()
            set_id = test_set_model.id
            httpcase_id = test_httpcase_model.id
            testcase_data = {
                'name': testcase_data['name'],
                'case_id': httpcase_id,
                'test_set_id': set_id,
                'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            testcase_model = TestCaseModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(testcase_model, testcase_data))
            db.session.commit()
        except Exception as e:
            logging.error('add case error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"复制用例失败,{}".format(str(e))}

        return {"code": 200, "msg": "复制用例成功"}
class TestCaseCopyView(Resource):
    def post(self):
        #入参被复制的用例的case_id,和产生的新用例的case_name
        #根据set_id查到testcase,httpcase的相关数据，插入到对应的表中
        dataForm = request.get_json(force=True)
        try:
            schema = {
                'type': 'object',
                'required':['case_id','case_name'],
                'properties': {
                    'case_id': {'type': 'integer', 'minLength': 1},
                    'case_name': {'type': 'string', 'minLength': 1}

                }
            }
            jsonschema.validate(dataForm, schema)
            case_name = dataForm['case_name']
            case_id = dataForm['case_id']
            #判断用例名称是否已存在
            has_case_name = db.session.query(TestCaseModel).filter(TestCaseModel.name == case_name,TestCaseModel.is_delete == 0).all()
            if len(has_case_name) > 0 :
                return {'code': 401, 'msg': u"用例名称已存在"}
            #准备httpcase表数据
            test_httpcase_data = AlchemyJsonEncoder.query_to_dict(db.session.query(HttpCaseModel).filter(HttpCaseModel.id == case_id,HttpCaseModel.is_delete == 0).all())[0]
            test_httpcase_data['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            test_httpcase_data.pop('id')
            test_httpcase_data.pop('update_time')
            test_httpcase_model = HttpCaseModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(test_httpcase_model, test_httpcase_data))
            db.session.flush()
            #准备testcase表数据
            httpcase_id = test_httpcase_model.id
            testcase_data = AlchemyJsonEncoder.query_to_dict(db.session.query(TestCaseModel).filter(TestCaseModel.case_id == case_id,TestCaseModel.is_delete == 0).all())[0]
            testcase_data['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            testcase_data.pop('id')
            testcase_data.pop('update_time')
            testcase_data['case_id'] = httpcase_id
            testcase_data['name'] = case_name
            testcase_model = TestCaseModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(testcase_model, testcase_data))
            db.session.commit()
        except Exception as e:
            logging.error('add case error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"复制用例失败,{}".format(str(e))}

        return {"code": 200, "msg": "复制用例成功"}
    def get(self):
        #添加用例页面添加依赖用例请求报文接口
        case_list = []
        department_id = request.args.get('department_id', type=int)
        try:
            #获取部门所对应的项目id
            project_id_list = db.session.query(ProjectModel.id).filter(ProjectModel.is_delete == 0,ProjectModel.department_id == department_id).all()
            to_list = []
            for i in project_id_list:
                to_list = to_list + list(i)
            project_id_list = to_list
            httpcase_data = db.session.query(HttpCaseModel.id,HttpCaseModel.post_command).filter(HttpCaseModel.post_command!='[]',HttpCaseModel.is_delete == 0).all()
            if httpcase_data:
                key_list = ('id', 'post_command')
                httpcase_lists = [dict(zip(key_list, case)) for case in httpcase_data]
                for index in httpcase_lists:
                    case_id = index['id']
                    testcase_data = db.session.query(TestCaseModel.name).outerjoin(ModuleModel,TestCaseModel.module_id == ModuleModel.id).filter(ModuleModel.is_delete==0,ModuleModel.project_id.in_(project_id_list),TestCaseModel.is_delete==0,TestCaseModel.case_id==case_id).all()
                    if testcase_data:
                        case_data = {
                            'case_name': testcase_data[0][0],  # 用例名称
                            'case_id': case_id,
                            'post_command': json.loads(index['post_command'])

                        }
                        case_list.append(case_data)
        except Exception as e:
            logging.error('get case list error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取用例全局变量,{}".format(str(e))}
        return {'code': 200, 'data': case_list}
class TestCaseFlowView(Resource):
    #通过case_id查询某个用例的用例流
    #返回格式eg:
    #{case_id:{'base_info':****,'parent':[2,3,4]},2:{'base_info':*****,'parent':[5,6]}}
    def get(self):
        id = request.args.get('id', type=int)
        id_list = []
        id_list.append(id)
        case_tree = {}
        try:
            while id_list:
                case_id = id_list[0]
                id_list.pop(0)
                httpcase_data = db.session.query(HttpCaseModel.pre_command).filter(HttpCaseModel.id == case_id,HttpCaseModel.is_delete == 0).all()
                pre_command = []
                if httpcase_data:
                    pre_command = httpcase_data[0][0]
                if pre_command:
                    parent_id = []
                    pre_command = json.loads(pre_command)
                    for var in pre_command:
                        parent_id.append(int(var['case_id']))
                    case_tree[case_id] = parent_id
                    id_list += parent_id
            data_tree = AlchemyJsonEncoder.getparents(id,case_tree)
        except Exception as e:
            logging.error('case flow error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"查询用例流失败,{}".format(str(e))}
        return {"code": 200, "data": data_tree}
class TestCaseDebugView(Resource):
    #添加用例页面，调试按钮对应的接口
    def post(self):
        dataForm = request.get_json(force=True)
        try:
            schema = {
                'type': 'object',
                'required': ['url', 'request_type', 'params'],
                'properties': {
                    'url': {'type': 'string', 'minLength': 1},
                    'request_type': {'type': 'integer', 'minLength': 1},
                    'params': {'type': 'object'},
                    'headers': {'type': 'array'}
                }
            }
            #'pattern':u'(https|http){0,1}://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+}'
            jsonschema.validate(dataForm, schema)
            case_flow = dataForm
            case_flow['parent'] = []
            if dataForm['params']['select']:
                select = dataForm['params']['select']
                for index in select:
                    select_list = index['value'].split('/')
                    select_case_id = select_list[0]
                    set_flow = AlchemyJsonEncoder.getparents(select_case_id)
                    case_flow['parent'].append(set_flow)
            data = AlchemyJsonEncoder.case_flow_request(case_flow)
        except Exception as e:
            logging.error('case debug error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"调试用例失败,{}".format(str(e))}
        return {'code':200,'msg':'调试成功','data':data}
class TestTaskSearchCase(Resource):
    def get(self):
        #添加任务页面-添加用例选择用例
        #逻辑：根据输入的关键字进行模糊查询返回结果
        #输入：sug_key
        #输出：包括sug_key的用例列表
        search_key = request.args.get('search_key', '',type=str)
        department_id = request.args.get('department_id', 0, type=int)
        if department_id <= 0:
            return {'code': 402, 'msg': '部门ID未传入'}
        search_case_lists = []
        try:
            project_id_list = db.session.query(ProjectModel.id).filter(ProjectModel.is_delete == 0,ProjectModel.department_id == department_id).all()
            to_list = []
            for i in project_id_list:
                to_list = to_list + list(i)
            project_id_list = to_list
            if search_key:
                search_case_lists = db.session.query(TestCaseModel.id,TestCaseModel.name,TestCaseModel.case_id).outerjoin(ModuleModel,TestCaseModel.module_id==ModuleModel.id).filter(TestCaseModel.is_delete == 0,ModuleModel.is_delete == 0, ModuleModel.project_id.in_(project_id_list),TestCaseModel.name.like('%{keyword}%'.format(keyword= search_key))).order_by(TestCaseModel.update_time.desc()).all()
                if search_case_lists:
                    key_list = ('id', 'name','case_id')
                    search_case_lists = [dict(zip(key_list, case)) for case in search_case_lists]
        except Exception as e:
            logging.error('case debug error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"调试用例失败,{}".format(str(e))}
        return {'code': 200, 'msg': '用例获取成功', 'data': search_case_lists}




