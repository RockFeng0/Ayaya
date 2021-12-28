#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.rm_task.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.rm_task.views,  v1.0 2019年12月5日
    FROM:   2019年12月5日
********************************************************************
======================================================================

Provide a function for the automation test

'''


import datetime,os, json, io
from flask import request, jsonify,send_file, make_response, url_for
from flask.views import MethodView
from redis.exceptions import ConnectionError

from rman.app.routes.api_0_0.rm_task import rm_task
from rman.app.routes.api_0_0.rm_task.models import Rmtask, db

from rman.app.routes.api_0_0.tasks.run_case.r_gen import gen_http_project
from rman.app.routes.api_0_0.tasks.run_case.r_http import test_http_case

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_rmtask_query():
    return db.session.query(Rmtask)

class RmtaskView(MethodView):
    
    def get(self):
        # GET /rm_task/case?page=1&size=10
        param = request.values
        _query = get_rmtask_query()
        
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))
        conditions = {i: param.get(i) for i in ('case', 'tid') if param.get(i)}     
        base_condition = _query.filter_by(**conditions).order_by(Rmtask.create_time.desc())
        
        total = base_condition.count()    
        pagination = base_condition.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "tasks":[]}
        result["tasks"] = [{"id":task.id,
                           "case": task.case,
                           "desc":task.desc,
                           "tid":task.tid,
                           "status":task.status,
                           "report_path":task.report_path,
                           "report_url":task.report_url,                           
                           "c_time": task.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                           "u_time": task.update_time.strftime("%Y-%m-%d %H:%M:%S")
                           } for task in pagination.items]
        return jsonify(get_result(result, message = "get all tasks success in page: {0} size: {1}.".format(page, size)))
    
    def post(self):
        # POST /rm_task/case    
        param = request.json if request.data else request.form.to_dict()        
        _query = get_rmtask_query()    
        now = datetime.datetime.now()
        
        cases = param.get("cases")
        if not param.get("cases"):
            return jsonify(get_result("", status = False, message = "Parameter ['cases'] should not be null"))
        
        try:
            if isinstance(cases, str):
                cases = json.loads(cases)
        except:
            pass
        
        if not isinstance(cases, list):
            return jsonify(get_result("", status = False, message = "Parameter 'cases' need a list type."))
            
        for case in cases:
            if not isinstance(case, dict):
                return jsonify(get_result("", status = False, message = "Parameter 'cases' need a content a dict type."))
            
        
        try:                 
            status = True
            
            for case in cases:         
                name = case.get("name")
                desc = case.get("desc")
            
                task = Rmtask(case = name, 
                              desc = desc, 
                              tid = "",
                              status = 0,
                              report_url = "",  
                              report_path = "", 
                              create_time = now,
                              update_time = now)
                db.session.add(task)
            message = "add task success."
            db.session.flush()
            db.session.commit()
            
        except Exception as e:
            message = str(e)
            status = False       
         
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /rm_task/case?task_id=32342
        
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        
        _query = get_rmtask_query() 
        now = datetime.datetime.now()        
         
        task = _query.filter_by(id = param.get("task_id")).first()
          
        if task:                  
            for i in ["case", "desc"]:
                _ = setattr(task, i, j_param.get(i)) if j_param.get(i) else ""
            task.update_time = now
            status = True
            message = "update rmtask success."
            db.session.flush()
            db.session.commit()
        else:
            status = False
            message = "do not have the task with task_id({})".format(param.get("task_id"))
        return jsonify(get_result("", status = status,message = message))
    
    def delete(self):
        # DELETE /rm_task/case?task_id=32342
        param = request.values
        _query = get_rmtask_query() 
          
        task = _query.filter_by(id = param.get("task_id")).first()
           
        if task:
            db.session.delete(task)
            db.session.commit()
            status = True
            message = "delete task success."        
        else:
            status = False
            message = "do not have the task with task_id({})".format(param.get("task_id"))
        return jsonify(get_result("", status = status,message = message))
   
    
    
@rm_task.route('/run', methods=['GET'])
def http_test():
    # GET /rm_task/run?task_ids=1,2,3,4,5
    param = request.values
    _query = get_rmtask_query() 
    
    task_ids = param.get("task_ids","")
    if not task_ids:
        return jsonify(get_result("", status = False,message = "Missing parameter 'task_ids'."))
    
    tasks = []
    task_ids = task_ids.split(',')    
    for _id in task_ids:
        task = _query.filter_by(id = _id).first()
        if not task:
            return jsonify(get_result("", status = False,message = "Do not have the task with task_id({})".format(_id)))        
        tasks.append(task)
    
    for task in tasks:
        f1 = gen_http_project(task.case)
        if os.path.isfile(f1):
            try:
                async_task = getattr(test_http_case, "apply_async")(args = (f1,))
            except ConnectionError:
                # Redis server not connected                
                task.status = 5
            else:            
                task.tid = async_task.id
                task.report_path = ""
                task.report_url = ""
                task.status = 1
        else:
            # 0-未执行, 1-执行中, 2-执行成功, 3-执行失败, 4-无效脚本 , 5-redis服务异常
            task.status = 4
        task.update_time = datetime.datetime.now()
        
    db.session.flush()
    db.session.commit() 
    return jsonify(get_result("", status = True,message = "Task added successfully."))          

@rm_task.route('/status')
def http_test_status():
    # GET /rm_task/status?task_ids=1,2,3,4,5
    param = request.values
    _query = get_rmtask_query() 
    
    task = _query.filter_by(id = param.get("task_id")).first()
    task_ids = param.get("task_ids","")
    if not task_ids:
        return jsonify(get_result("", status = False,message = "Missing parameter 'task_ids'."))
    
    tasks = []
    task_ids = task_ids.split(',')    
    for _id in task_ids:
        task = _query.filter_by(id = _id).first()
        if not task:
            return jsonify(get_result("", status = False,message = "Do not have the task with task_id({})".format(_id)))        
        tasks.append(task)
        
    results = {}
    for task in tasks:
        if task.status != 1:
            continue
                
        async_task = getattr(test_http_case, "AsyncResult")(task.tid)
        #     async_task = test_http_case.AsyncResult(task_id)
        results[task.id] = {"state":async_task.state}
        
        if async_task.state == 'PENDING':
            results[task.id]["message"] = "wait for the job finish." 
            task.status = 1
            task.report_url = ""
        elif async_task.state == 'FAILURE':
            results[task.id]["message"] = "something went wrong in the background job: " +  str(async_task.info)
            task.status = 3
            task.report_url = ""
        else:
            results[task.id]["message"] = "job finished."
            task.report_path = async_task.info.get("report")            
            task.status = 2 
            task.report_url = url_for("rm_task.get_test_report", task_id = task.id, _external=True)
            
    db.session.flush()
    db.session.commit()     
    return jsonify(get_result(results, status = True, message="Task status query successful.")) 

@rm_task.route('/report', methods = ["GET"])
def get_test_report():
    # GET /rm_task/report?task_id=32342
    param = request.values
    _query = get_rmtask_query() 
    
    task = _query.filter_by(id = param.get("task_id")).first()
    
    if task and os.path.isfile(task.report_path):
        return send_file(task.report_path)
    else:
        return "404"

@rm_task.route('/caselogs/<log>')
def get_log(log):
    # GET /rm_task/caselogs/xxx.log?task_id=32342
    param = request.values
    _query = get_rmtask_query() 
    
    task = _query.filter_by(id = param.get("task_id")).first()
    
    if task and os.path.isfile(task.report_path): 
        report_abs_path = os.path.dirname(task.report_path)   
        lg = os.path.join(report_abs_path, 'caselogs/%s' %log)
        resp = make_response(io.open(lg, 'r', encoding='utf-8').read())
        resp.headers["Content-type"]="text/plain;charset=UTF-8"
        return resp
    else:
        return "404"
    

_rmtask_view_manager = RmtaskView.as_view('rmtask_view_manager')
rm_task.add_url_rule('/case', view_func=_rmtask_view_manager)
