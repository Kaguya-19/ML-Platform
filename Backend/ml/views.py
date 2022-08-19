from array import array
import threading
from tkinter.filedialog import test
from turtle import Turtle

from django.shortcuts import render
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.paginator import  Paginator
import datetime
from django.utils import timezone
# Create your views here.
from .models import Model_info,Test_info,Service_info
from .filters import ModelFilter

def model_add_singlemodel(name,description,model_type,file):
    model = Model_info.objects.create(name=name,description=description,model_type=model_type,file=file)
    return model

import os
from .ml import get_model_info

BASE_URL='http://127.0.0.1:8080'

def model_api(request):
    if request.method == 'POST':
        return model_add(request)
    elif request.method == 'GET':
        return model_all(request)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)


def model_add(request,add_mode = 'single'):
    res = dict()
    willContinue = True
    if request.method != 'POST':
        res = {"errmsg":"上传模型失败"}
        willContinue = False
    else:
        try:
            name = request.POST.get('name')
            description = request.POST.get('description','')
            model_type = request.POST.get('model_type')
            if add_mode == 'single':
                model = model_add_singlemodel(name,description,model_type,file = request.FILES['file'])
                info = get_model_info(model.file.path, model.model_type)
                if "stderr" in info:
                    res = {"errmsg":"模型不合法"}
                    os.remove(model.file.path)
                    model.delete()
                    willContinue = False
                else:
                    try:
                        model.input=info['input']
                        model.output=info['output']
                        model.algorithm=info['algorithm']
                        model.engine=info['engine']
                        model.save()
                    except:
                        res = {"errmsg":"模型不合法"}
                        os.remove(model.file.path)
                        model.delete()
                        willContinue = False
            # else:
            #     # 解压zip/rar的模型文件并保存至model
            #     current_work_dir = os.path.dirname (__file__)
            #     tmp_models_dir = current_work_dir + '/tmpTest'
            #     if not os.path.exists(tmp_models_dir):
            #         os.makedirs(dir)
            #     src_file = request.FILES['file']
            #     file_type = '.zip'
            #     if file_type == '.zip':
            #         # 需要安装zip包：pip install zipp
            #         zip_file = zipfile.ZipFile(src_file)
            #         for names in zip_file.namelist():
            #             zip_file.extract(names, tmp_models_dir)
            #         zip_file.close()
            #     elif file_type == '.rar':
            #         # 需要安装rar包：pip install rarfile
            #         rar = rarfile.RarFile(src_file)
            #         os.chdir(tmp_models_dir)
            #         rar.extractall()
            #         rar.close()
            #     # TODO 多线程     
            #     files=os.listdir(tmp_models_dir)
            #     for i in files:
            #         file_path=os.path.join(tmp_models_dir+i)
            #         f = open(file_path)
            #         file = f.read()
            #         f.close()
            #         model_add_singlemodel(file)
            #     pass
        except:
            res = {"errmsg":"上传模型失败"}
            willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def model_all(request):
    try:
        pageNo = int(request.GET.get('pageNo',1))
        pageSize = int(request.GET.get('pageSize',10))
        text = request.GET.get('name','')
        model_type = request.GET.get('model_type','')
        
        if model_type != '':
            models = Model_info.objects.filter(model_type=model_type).order_by('id').values('name','model_type','id')
            print(models)
        else:
            models = Model_info.objects.order_by('id').values('name','model_type','id')
        if text != '':
            models = ModelFilter({"name":text}, queryset=models).qs
        
        paginator = Paginator(models, pageSize)
        context = {'result':{'data':list(paginator.page(pageNo)),
                             'pageSize':pageSize,
                             'pageNo':pageNo,
                             'totalCount':models.count(),
                             'totalPage':paginator.num_pages
                             }}
        return JsonResponse(context)
    except:
        return JsonResponse({"errmsg":"获取信息失败"},status=400)

def model_info_api(request, model_id):
    if request.method == 'DELETE':
        return model_delete(request, model_id)
    elif request.method == 'GET':
        return model_info(request, model_id)
    elif request.method == 'PUT':
        return model_change(request, model_id)
    elif request.method == 'POST':
        return test_add(request, model_id)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def model_info(request, model_id):
    res = dict()
    willContinue = True
    try:
        model = Model_info.objects.get(id=model_id)
        res = model_to_dict(model)
        res['file']=BASE_URL+res['file'].url
        res['addTime'] = model.addTime.strftime("%Y-%m-%d %H:%M")
    except:
        res = {"errmsg":"读取模型信息失败"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def model_delete(request, model_id):
    res = dict()
    willContinue = True
    try:
        model = Model_info.objects.get(id=model_id)
        os.remove(model.file.path)
        model.delete()
    except:
        res = {"errmsg":"读取模型信息失败"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def model_change(request, model_id):
    res = dict()
    willContinue = True
    print(request.PUT)
    try:
        name = request.PUT.get('name')
        description = request.PUT.get('description','')
        model_type = request.PUT.get('model_type')
        model = Model_info.objects.get(id=model_id)
        if 'file' in request.FILES or model_type != model.model_type:
            oldfile = model.file
            if 'file' in request.FILES:
                model.file = request.FILES['file']
                model.save()
            info = get_model_info(model.file.path, model_type)
            if "stderr" in info:
                res = {"errmsg":"模型不合法"}
                model.file = oldfile
                model.save()
                os.remove(model.file.path)
                willContinue = False
            else:
                try:
                    model.input=info['input']
                    model.output=info['output']
                    model.algorithm=info['algorithm']
                    model.engine=info['engine']
                    model.save()
                except:
                    res = {"errmsg":"模型不合法"}
                    os.remove(model.file.path)
                    willContinue = False
        model.name = name
        model.model_type =model_type
        model.description = description
        model.save()  
    except:
            res = {"errmsg":"上传模型失败"}
            willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def fast_test(request,id,type='model'):
    input_x = dict()
    for key in request.FILES:
        input_x[key] = request.FILES[key]
    for key in request.POST:
        input_x[key] = request.POST[key]
    if type == 'model':
        model = Model_info.objects.get(id=id)
    else:
        mod = Service_info.objects.get(id=id).mod
        model = Model_info.objects.get(id=mod)
    tested_model_path = model.file.path
    tested_model_type = model.model_type
    # TODO: 预处理
    return quick_predict(tested_model_path,type = tested_model_type,x_test = input_x)

def test_add(request,model_id):
    res = dict()
    willContinue = True
    try:
        res['result'] = fast_test(request,model_id)
    except:
        res = {"errmsg":"Request error"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def task_add(request, service_id):
    res = dict()
    willContinue = True
    try:
        test_type = request.GET['type']
    except:
        res = {"errmsg":"Request error"}
        willContinue = False
    try:
        message = request.POST.get('message','')
        service = Service_info.objects.get(id=service_id)
        mod = Model_info.objects.get(id=service.mod)
        if 'file' in request.FILES:
            test.tested_file = request.FILES['file']
        test = Test_info.objects.create(message=message,service=service,mod=mod,test_type=test_type)
        test.save()
        if test_type == 'fast':
            res['result'] = fast_test(request,service_id,type='service')
            test.recent_modified_time = timezone.now()
            test.end_time = timezone.now()
            test.is_finished = True
            test.save()
            service.average_use_time = \
                (service.average_use_time * service.use_times + test.end_time - test.start_time)/(service.use_times + 1)
            service.use_times = service.use_times + 1
            service.save()
        else:
            new_task(request,test.id ,service.id, mode = 'multiple')
            res['task_id'] = test.id
            service.use_times = service.use_times + 1
            service.save()
    except:
        try:
            os.remove(test.tested_file.path)
        except:
            pass
        try:
            test.delete()
        except:
            pass
        res = {"errmsg":"Request error"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

# def test_file_add(request):
#     if request.method != 'POST':
#         return HttpResponse("上传测试文件失败")
#     else:
#         add_mode = request.POST.get('add_mode')
#         if add_mode == 'single':           
#             return test_file_add_single(request)
#         else:
#             # TODO：后续可增加查看单一文件功能
#             test_file_add_single(request)
#             return HttpResponse('压缩文件下测试文件上传成功')

from .ml import batch_predict,quick_predict
from threading import Thread
import cv2
import zipfile
import numpy as np

def start_test(test_file_id , service_id, mode = 'single'):
    test_task =  Test_info.objects.get(id=test_file_id)
    test_file = test_task.file
    test_task.threadID = threading.currentThread().ident
    test_task.is_finished = False
    test_task.save()
    res = {}
    try:
        tested_model_type = test_task.mod.model_type
        tested_model_path = test_task.mod.file.path
        service = Service_info.objects.get(id=service_id)
        # TODO test_file预处理
        if mode == 'single':
            res['result'] = quick_predict(tested_model_path,type = tested_model_type,x_test = test_file)
            test_task.result = res['result']
            test_task.is_finished = True
            test_task.save()
        else:
            # 不解压直接读取zip中的图片
            with zipfile.ZipFile(test_file.path, mode='r') as zfile:  # 只读方式打开压缩包

                for name in zfile.namelist():
                    if '.jpg' not in name:
                        continue

                    with zfile.open(name, mode='r') as image_file:
                        content = image_file.read()  # 一次性读入整张图片信息
                        image = np.asarray(bytearray(content), dtype='uint8')
                        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                        cv2.imshow('image', image)

                zfile.close()
                # TODO 集中np转化
            res['result'] = batch_predict(path = tested_model_path, type = tested_model_type,x_test = test_file)
            test_task.result = res['result']
            test_task.is_finished = True
            test_task.recent_modified_time = timezone.now()
            test_task.end_time = timezone.now()
            test_task.save()
            service.average_use_time = \
                (service.average_use_time * service.use_times + test_task.end_time - test_task.start_time)/(service.use_times + 1)
            service.use_times = service.use_times + 1
            service.save()
            test_task.save()
    except:
        JsonResponse({"errmsg":"获取信息失败"},status=400)
    return JsonResponse(res)

def new_task(request, test_file_id):
    model_id = request.POST.get['model_id']
    param_tuple = (test_file_id, model_id)
    new_thread = Thread(target=start_test, args=param_tuple)
    new_thread.start()
    
def test_quick(request, model_id):
    if request.method == 'POST':
        model = Model_info.objects.get(id=model_id)
        model_type = model.model_type
        model_path = model.file.path
        model_input = model.input
        x_test = []
        try:
            test_data = request.POST
            for key, value in test_data.items():
                if isinstance(value,list):
                    x_test += value
                else:
                    x_test.append(value)
            x_test = np.array(x_test).astype(np.float32)
            if model_type == "pmml":
                x_test = x_test.reshape(1,len(x_test))
            result = quick_predict(model_path,model_type,x_test)
            print("result: ", result)
            return JsonResponse(result,status=200)
        except:
            import traceback
            traceback.print_exc()
            return JsonResponse({"errmsg":"输入参数与模型不符"},status=400)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

# 返回查询的test列表信息
def test_all(request):
    try:
        pageNo = int(request.GET.get('pageNo',1))
        pageSize = int(request.GET.get('pageSize',10))
        message = request.GET.get('message','')
        is_finished = request.GET.get('is_finished',0)

        if is_finished != '':
            tests = Test_info.objects.filter(is_finished=is_finished).order_by('id').values('message','is_finished','id','recent_modified_time')
            print(tests)
        else:
            tests = Model_info.objects.order_by('id').values('message','is_finished','id','recent_modified_time')
        if message != '':
            tests = ModelFilter({"message":message}, queryset=tests).qs

        paginator = Paginator(tests, pageSize)
        context = {'result':{'data':list(paginator.page(pageNo)),
                             'pageSize':pageSize,
                             'pageNo':pageNo,
                             'totalCount':tests.count(),
                             'totalPage':paginator.num_pages
                             }}
        return JsonResponse(context)
    except:
        return JsonResponse({"errmsg":"获取信息失败"},status=400)

# 测试成功，多页未测试
def test_api(request):
    if request.method == 'GET':
        return test_all(request)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def test_info_api(request, test_id):
    if request.method == 'DELETE':
        return test_delete(request, test_id)
    elif request.method == 'GET':
        return test_info(request, test_id)
    elif request.method == 'PUT': # 不要求
        return test_change(request, test_id)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def test_info(request, test_id):
    res = dict()
    willContinue = True
    try:
        test = Test_info.objects.get(id=test_id)
        res = model_to_dict(test)
        if test.tested_file != None:
            res['tested_file']=BASE_URL+res['tested_file'].url
        res['add_time'] = test.add_time.strftime("%Y-%m-%d %H:%M")
        res['recent_modified_time'] = test.add_time.strftime("%Y-%m-%d %H:%M")
        res['endtime'] = test.endtime.strftime("%Y-%m-%d %H:%M")
    except:
        res = {"errmsg":"读取测试信息失败，可能您输入的测试文件已被删除"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def test_delete(request, test_id):
    res = dict()
    willContinue = True
    try:
        tested_file = Test_info.objects.get(id=test_id)
        os.remove(tested_file.tested_file.path)
        tested_file.delete()
        {"test_id":test_id}
    except:
        res = {"errmsg":"删除测试任务失败"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def test_change(request, test_id):
    res = dict()
    willContinue = True
    print(request.PUT)
    try:
        test = Test_info.objects.get(id=test_id)
        message = request.PUT.get('message')
        is_finished = request.PUT.get('is_finished',test.is_finished)

        # 此处不能改文件
        # if 'tested_file' in request.FILES:
        #     test.file = request.FILES['tested_file']
        test.recent_modified_time = timezone.now()
        test.message = message
        test.is_finished = is_finished
        test.save()  
    except:
        res = {"errmsg":"修改测试文件失败"}
        willContinue = False
    
    res['message'] = message
    res['is_finished'] = test.is_finished
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def service_api(request):
    if request.method == 'POST':
        return service_add(request)
    elif request.method == 'GET':
        return service_all(request)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def service_info_api(request, service_id):
    if request.method == 'DELETE':
        return service_delete(request, service_id)
    elif request.method == 'GET':
        return service_info(request, service_id)
    elif request.method == 'PUT':
        # 暂停，启动等操作
        return service_change(request, service_id)
    elif request.method == 'POST':
        return task_add(request, service_id)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def service_add(request):
    res = dict()
    willContinue = True
    if request.method != 'POST':
        res = {"errmsg":"部署失败"}
        willContinue = False
    else:
        try:
            name = request.POST.get('name')
            description = request.POST.get('description','')
            model_id = request.POST.get('model_id')
            service = Service_info.objects.create(name=name,description=description,mod = Model_info.objects.get(id=model_id))
            res = {"service_id":service.id}
        except:
            res = {"errmsg":"部署失败"}
            willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def service_all(request):
    try:
        pageNo = int(request.GET.get('pageNo',1))
        pageSize = int(request.GET.get('pageSize',10))

        name = request.GET.get('name','')
        model_id = request.GET.get('model_id',-1)
        status = request.GET.get('status',-1)

        if model_id != -1:
            services = Service_info.objects.filter(model__id = model_id,).order_by('id').values('name','description','id','create_time',
                                                                        'recent_modified_time','status','average_use_time','use_times')
            print(services)
        else:
            # 不进行模型的筛选
            services = Service_info.objects.order_by('id').values('name','description','id','create_time',
                                                                'recent_modified_time','status','average_use_time','use_times')

        if name != '':
            services = ModelFilter({"name":name}, queryset=services).qs
        if status != -1:
            services = ModelFilter({"status":status}, queryset=services).qs

        paginator = Paginator(services, pageSize)
        context = {'result':{'data':list(paginator.page(pageNo)),
                             'pageSize':pageSize,
                             'pageNo':pageNo,
                             'totalCount':services.count(),
                             'totalPage':paginator.num_pages
                             }}
        return JsonResponse(context)
    except:
        return JsonResponse({"errmsg":"获取部署信息失败"},status=400)

def service_delete(request, service_id):
    res = dict()
    willContinue = True
    try:
        service = Service_info.objects.get(id=service_id)
        service.delete()
        {"id":service_id}
    except:
        res = {"errmsg":"删除部署失败"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp    

def service_info(request, service_id):
    res = dict()
    willContinue = True
    try:
        service = Service_info.objects.get(id=service_id)
        res = model_to_dict(service)
        res['create_time'] = service.create_time.strftime("%Y-%m-%d %H:%M")
        res['recent_modified_time'] = service.recent_modified_time.strftime("%Y-%m-%d %H:%M")
    except:
        res = {"errmsg":"读取测试信息失败，可能您输入的测试文件已被删除"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp   

def service_change(request, service_id):
    res = dict()
    willContinue = True
    print(request.PUT)
    try:
        service = Service_info.objects.get(id=service_id)
        name = request.PUT.get('name',service.name)
        description = request.PUT.get('description',service.description)
        # TODO 改了状态后停止/启动/删除的反应
        status = request.PUT.get('status',service.status)

        service.recent_modified_time = timezone.now()
        service.name = name
        service.description = description
        service.status = status

        service.save()  
        res = model_to_dict(service)
    except:
        res = {"errmsg":"修改测试文件失败"}
        willContinue = False
    

    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp    

# 测试
if __name__ == "__main__":
    print('enter views.main')
    current_work_dir = os.path.dirname (__file__)
    tested_file_path = current_work_dir + '/test.onnx'
    f = open(tested_file_path)
    tested_file = f.read()
    Test_info.objects.create(tested_file)
