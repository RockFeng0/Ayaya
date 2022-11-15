! python3
# -*- encoding: utf-8 -*-


from flask_restful import Resource
from flask import request,jsonify,json
import jsonschema
from  rman.app.models.ut_rman_interface_config import InterfaceModel
from  rman.app.models.ut_rman_httpcase import HttpCaseModel
from rman.app.models.ut_rman_project import ProjectModel
from rman.app.models.ut_rman_module import ModuleModel
from datetime import datetime
import logging
from flask_restful.reqparse import RequestParser
from rman.app import db
from rman.app.common.utils.other.alchemy import AlchemyJsonEncoder,has_module

class InterfaceConfigsView(Resource):
    def __init__(self):
        self.parser = RequestParser()

    #添加接口
    def post(self):
        dataForm = request.get_json(force = True)
        try:
            schema = {
                'type': 'object',
                'required': ['interface_name','url','request_type','project_name','module_name','project_id'],
                'properties': {
                    'interface_name': {'type': 'string', 'minLength': 1},
                    'url': {'type': 'string', 'minLength': 1},
                    'request_type': {'type': 'integer', 'minLength': 1},
                    'params': {'type': 'array'},
                    'headers': {'type': 'array'},
                    'project_name': {'type': 'string', 'minLength': 1},
                    'module_name': {'type': 'string', 'minLength': 1},
                    'project_id':{'type':'integer'},
                    'update_person': {'type': 'string'}

                }
            }
            jsonschema.validate(dataForm,schema)
            #查询module_id
            module_id = has_module(dataForm.get('project_id'),dataForm.get('module_name'))
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
            insert_data = {
                'interface_name': dataForm['interface_name'],
                'url': dataForm['url'],
                'request_type': dataForm['request_type'],
                'params': json.dumps(dataForm['params']) if 'params' in dataForm else '[]',
                'headers': json.dumps(dataForm['headers']) if 'headers' in dataForm else '[]',
                'project_name':dataForm['project_name'],
                'project_id': dataForm['project_id'],
                'module_id': module_id,
                'update_person': dataForm['update_person'] if 'update_person' in dataForm else '',
                'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            interface_model = InterfaceModel()
            db.session.add(AlchemyJsonEncoder.to_alchemy(interface_model, insert_data))
            db.session.commit()
        except Exception as e:
            logging.error('add interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"提交失败,{}".format(str(e))}

        return {"code":200, "msg":"接口添加成功"}
    #修改接口
    def put(self):
        dataForm = request.get_json(force=True)
        print("hello")
        try:
            if 'id' not in dataForm.keys():
                return {'code': 4101, 'msg': u"id must be used "}
            if 'params' in dataForm.keys():
                dataForm['params'] = json.dumps(dataForm['params'])
            if 'headers' in dataForm.keys():
                dataForm['headers'] = json.dumps(dataForm['headers'])
            if 'module_name' in dataForm.keys():
                # 查询module_id
                module_id = has_module(dataForm.get('project_id'),dataForm.get('module_name'))
                if len(module_id) == 0:
                    # 构造module数据库数据
                    testmodule_data = {
                        'name': dataForm['module_name'],
                        'project_id': dataForm['project_id']
                    }
                    test_module_model = ModuleModel()
                    db.session.add(AlchemyJsonEncoder.to_alchemy(test_module_model, testmodule_data))
                    db.session.commit()
                    module_id = test_module_model.id
                else:
                    module_id = module_id[0][0]
                dataForm['module_id'] = module_id
                dataForm.pop('module_name')

           #根据id找到interface表中url，通过url匹配到使用了该接口的用例
            _interface = db.session.query(InterfaceModel).filter_by(id=dataForm['id']).first()
            is_change = False
            check_item = ('headers', 'request_type')
            case_update = {}
            for item in check_item:
                if item in dataForm.keys() and _interface and getattr(_interface, item) != dataForm[item]:
                    is_change = True
                    case_update[item]=dataForm[item]
            if is_change:
                db.session.query(HttpCaseModel).filter_by(url=_interface.url, is_delete=0).\
                    update(AlchemyJsonEncoder.to_alchemy_json(HttpCaseModel, case_update))
                db.session.flush()
            db.session.query(InterfaceModel).filter_by(id=dataForm['id']).update(AlchemyJsonEncoder.to_alchemy_json(InterfaceModel, dataForm))
            db.session.commit()
        except Exception as e:
            logging.error('update interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"接口更新失败,{}".format(str(e))}
        return {"code": 200, "msg": "接口更新成功"}
    #获取接口配置列表
    def get(self):
        page = request.args.get('page', 1, type=int)
        num = request.args.get('num', 10, type=int)
        department_id = request.args.get('department_id', type=int)
        interface_name = request.args.get('interface_name','', type=str)
        if department_id<=0:
            return {'code': 402,'msg':'部门ID未传入'}
        try:
            #is_delete=0状态的数据，对查询结构以id进行升序排列,并进行分页
            project_id_list = db.session.query(ProjectModel.id).filter(ProjectModel.is_delete == 0,ProjectModel.department_id == department_id).all()
            to_list = []
            for i in project_id_list:
                to_list = to_list + list(i)
            project_id_list = to_list
            interface_dict = []
            query_field = (InterfaceModel.url,InterfaceModel.interface_name,InterfaceModel.request_type,InterfaceModel.params
                           ,InterfaceModel.headers,InterfaceModel.project_name,InterfaceModel.project_id,InterfaceModel.update_person,InterfaceModel.id,
                           InterfaceModel.update_time,InterfaceModel.update_person,InterfaceModel.create_time,InterfaceModel.is_delete)
            if interface_name:
                base_condition = db.session.query(*query_field,ModuleModel.name.label("module_name")).\
                    join(ModuleModel, ModuleModel.id==InterfaceModel.module_id).filter(InterfaceModel.is_delete == 0,InterfaceModel.project_id.in_(project_id_list),InterfaceModel.interface_name.like('%{keyword}%'.format(keyword=interface_name))).order_by(InterfaceModel.id.desc())
                interfacedata = base_condition.paginate(page = page, per_page = num).items
                if interfacedata:
                    interface_dict = AlchemyJsonEncoder.query_to_dict(interfacedata)
            else:
                base_condition = db.session.query(*query_field,ModuleModel.name.label("module_name")).\
                    join(ModuleModel, ModuleModel.id==InterfaceModel.module_id).filter(InterfaceModel.is_delete == 0,InterfaceModel.project_id.in_(project_id_list)).order_by(InterfaceModel.id.desc())
                interfacedata = base_condition.paginate(page = page, per_page = num).items
                if interfacedata:
                    interface_dict = AlchemyJsonEncoder.query_to_dict(interfacedata)
        except Exception as e:
            logging.error('get interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取接口列表失败,{}".format(str(e))}
        return {'code': 200, 'page':page,'num':num,'total':base_condition.count(),'data':interface_dict}
    #删除接口配置
    def delete(self):
        parser = RequestParser()
        parser.add_argument(
            'id',
            type=int,
            required=True,
            help="id must be used",
        )
        try:
            delete_id = parser.parse_args()['id']
            update_data = {'is_delete':1}
            if len(db.session.query(InterfaceModel).filter_by(id=delete_id).all()) == 0:
                return {'code': 402, 'msg': u"不存在ID为{}的数据".format(delete_id)}
            else:
                db.session.query(InterfaceModel).filter_by(id=delete_id).update(update_data)
                db.session.commit()
        except Exception as e:
            logging.error('get interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取失败,{}".format(str(e))}
        return {"code": 200, "msg": "接口删除成功"}

class InterfaceConfigsViewList(Resource):
    #获取接口配置
    def get(self, id):
        try:
            interfacedata = db.session.query(InterfaceModel).filter(InterfaceModel.id == id, InterfaceModel.is_delete == 0).all()
            if len(interfacedata) == 0:
                interface_data = []
            else:
                interface_data = AlchemyJsonEncoder.query_to_dict(interfacedata)
                interface_data[0]['params'] = json.loads(interface_data[0]['params'])
                interface_data[0]['headers'] = json.loads(interface_data[0]['headers'])
                module_data = db.session.query(ModuleModel).filter(ModuleModel.id == interface_data[0]['module_id']).first()
                interface_data[0]['module_name'] = module_data.name
                interface_data[0].pop("module_id")

        except Exception as e:
            logging.error('get interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取失败,{}".format(str(e))}
        return {"code": 200, "data": interface_data}
class InterfaceConfigsForAddCase(Resource):
    def get(self):
        all_interfacedata =[]
        department_id = request.args.get('department_id', 0,type=int)
        search_key = request.args.get('search_key','', type=str)
        if department_id <= 0:
            return {'code': 402, 'msg': '部门ID未传入'}
        try:
            #is_delete=0状态的数据，对查询结构以id进行升序排列,
            project_id_list = db.session.query(ProjectModel.id).filter(ProjectModel.is_delete == 0,ProjectModel.department_id == department_id).all()
            to_list = []
            for i in project_id_list:
                to_list = to_list + list(i)
            project_id_list = to_list
            if search_key:
                print(search_key)
                query_field = (
                InterfaceModel.url, InterfaceModel.interface_name, InterfaceModel.request_type, InterfaceModel.params
                , InterfaceModel.headers, InterfaceModel.project_name, InterfaceModel.project_id,
                InterfaceModel.update_person, InterfaceModel.id,
                InterfaceModel.update_time, InterfaceModel.update_person, InterfaceModel.create_time,
                InterfaceModel.is_delete)
                # all_interfacedata =  db.session.query(InterfaceModel).filter(InterfaceModel.is_delete == 0,InterfaceModel.project_id.in_(project_id_list),InterfaceModel.interface_name.like('%{keyword}%'.format(keyword= search_key))).all()
                all_interfacedata = db.session.query(*query_field,ModuleModel.name.label("module_name")).outerjoin(InterfaceModel,InterfaceModel.module_id == ModuleModel.id).filter(InterfaceModel.is_delete == 0,ModuleModel.is_delete == 0,InterfaceModel.project_id.in_(project_id_list),InterfaceModel.interface_name.like('%{keyword}%'.format(keyword= search_key))).all()
                # print(all_interfacedata)
                if all_interfacedata:
                    all_interfacedata = AlchemyJsonEncoder.query_to_dict(all_interfacedata)
                    for index in range(len(all_interfacedata)):
                        all_interfacedata[index]['params'] = json.loads(all_interfacedata[index]['params'])
                        all_interfacedata[index]['headers'] = json.loads(all_interfacedata[index]['headers'])
        except Exception as e:
            logging.error('get interface error:{}'.format(str(e)))
            db.session.rollback()
            return {'code': 401, 'msg': u"获取失败,{}".format(str(e))}
        return {'code': 200,'data':all_interfacedata}

