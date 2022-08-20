from array import array
import threading
from tkinter.filedialog import test
from turtle import Turtle

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.core.paginator import  Paginator
import datetime
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

def test_file_add_single(request):
    try:
        tested_file = request.FILES['tested_file']
        message = request.POST.get('message')
        model_id = request.POST.get('model_id',None)
        service_id = request.POST.get('service_id',None)
        test = Test_info.objects.create(tested_file=tested_file,message=message)
    except:
        os.remove(test.tested_file.path)
        test.delete()
        return HttpResponse('单个测试文件上传失败,请检查file/message/model_id/service_id')
    try:
        if model_id != None:
            test.mod = Model_info.objects.get(id=model_id) 
    except:
        os.remove(test.tested_file.path)
        test.delete()
        return HttpResponse('单个测试文件上传失败，请检查model_id')
    try:
        if service_id != None:
            test.service = Service_info.objects.get(id=service_id)
    except:
        os.remove(test.tested_file.path)
        test.delete()
        return HttpResponse('单个测试文件上传失败，请检查service_id')       
    test.save()
    return HttpResponse('单个测试文件上传成功')

def test_file_add(request):
    if request.method != 'POST':
        return HttpResponse("上传测试文件失败")
    else:
        add_mode = request.POST.get('add_mode')
        if add_mode == 'single':           
            return test_file_add_single(request)
        else:
            # TODO：后续可增加查看单一文件功能
            test_file_add_single(request)
            return HttpResponse('压缩文件下测试文件上传成功')

from .ml import batch_predict,quick_predict
from threading import Thread
import cv2
import zipfile
import numpy as np


# TODO return HttpResponse需要修改
def start_test(request, test_file_id , model_id):
    test_task =  Test_info.objects.get(id=test_file_id)
    test_file = test_task.file
    test_task.mod = Model_info.objects.get(id=model_id)
    test_task.threadID = threading.currentThread().ident
    test_task.is_finished = False
    res = {}
    test_task.result = res
    test_task.save()
    tested_model_type = test_task.mod.model_type
    tested_model_path = test_task.mod.file.path

    input_info = test_task.mod.input
    if tested_model_type == 'pmml':
        input_shape = len(input_info)
    elif tested_model_type == 'onnx':
        input_shape = input_info[0]['shape']
    elif tested_model_type == 'keras':
        input_shape = input_info[0]['shape']
        input_shape = input_shape[1:]
    else:
        return HttpResponse("模型信息读取错误")
    # if mode == 'single':
    #     test_file_name = test_file.name
    #     if '.jpg' in test_file_name:
    #         # 处理图片
    #         image = cv2.imread(test_file.path)
    #         global preprocess_result
    #         preprocess_result = {}
    #         func_str = request.POST.get('func_str')  # TODO:具体互动细节(获取脚本)
    #         exec(func_str)
    #         preprocessed_img = preprocess_result['result']
    #         if preprocessed_img.shape != tuple(input_shape):
    #             return HttpResponse("输入图片不适配此模型")
    #         x_test = preprocessed_img
    #     elif '.txt' in test_file_name:
    #         # 处理文本
    #         with open(test_file.path, 'r') as file_to_read:
    #             lines = file_to_read.readline()  # 整行读取数据
    #             this_lines = lines.split()
    #             number_this_lines = [float(x) for x in this_lines]
    #             if len(number_this_lines) != np.prod(input_shape):
    #                 return HttpResponse("输入的文本行数据量不适配此模型")
    #             x_test = np.array(number_this_lines).reshape(tuple(input_shape))
    #     else:
    #         return HttpResponse("不支持处理")
    #     res['result'] = quick_predict(tested_model_path,type = tested_model_type,x_test = x_test)
    #     test_task.result = res['result']
    #     test_task.is_finished = True
    #     test_task.save()
    # else:
    x_test=[]
    if '.zip' in test_file.name:
        with zipfile.ZipFile(test_file.path, mode='r') as zfile:  # 只读方式打开压缩包
            for name in zfile.namelist():  # 获取zip文档内所有文件的名称列表
                if '.jpg' in name:
                    with zfile.open(name, mode='r') as image_file:
                        content = image_file.read()  # 一次性读入整张图片信息
                        image = np.asarray(bytearray(content), dtype='uint8')
                        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                        global preprocess_result
                        preprocess_result = {}
                        func_str = request.POST.get('func_str')  # TODO:具体互动细节（获取脚本）
                        exec(func_str)
                        preprocessed_img = preprocess_result['result']
                        if preprocessed_img.shape != tuple(input_shape):
                            return HttpResponse("输入图片不适配此模型")
                        x_test.append(preprocessed_img.tolist())
                        # cv2.imshow('image', image)
                elif '.txt' in name:
                    with zfile.open(name, 'r') as file_to_read:  # 打开文件，将其值赋予file_to_read
                        while True:
                            lines = file_to_read.readline()  # 整行读取数据
                            if not lines:  # 若该行为空
                                break  # 喀嚓
                            else:
                                this_lines = lines.split()
                                number_this_lines = [float(x) for x in this_lines]
                                if len(number_this_lines) != np.prod(input_shape):
                                    return HttpResponse("输入的文本行数据量不适配此模型")
                                x_test.append(list(np.array(number_this_lines).reshape(tuple(input_shape))))
            zfile.close()
    elif '.csv' in test_file.name:
        with open(test_file.path, mode='r', encoding='utf-8') as f:
            input_file_string = f.read()
            input_file_list = input_file_string.split('\n')
            # 发现有时候最后会多一行，去掉
            if input_file_list[-1] == "":
                input_file_list.pop()
            for i in range(1, len(input_file_list)):
                # 使用zip将两组数据打包成字典
                tmp_data = input_file_list[i].split(',')
                number_tmp_data = [float(x) for x in tmp_data]
                if len(number_tmp_data) != np.prod(input_shape):
                    continue
                x_test.append(number_tmp_data)
    else:
        return HttpResponse("不支持处理该类型文件")

    x_test = np.array(x_test)
    res['result'] = batch_predict(path = tested_model_path, type = tested_model_type,x_test = x_test)
    test_task.result = res['result']
    test_task.is_finished = True
    test_task.save()

    return JsonResponse(res)

def new_task(request, test_file_id):
    model_id = request.POST.get['model_id']
    param_tuple = (request, test_file_id, model_id)
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
    if request.method == 'POST':
        return test_file_add(request)
    elif request.method == 'GET':
        return test_all(request)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def test_info_api(request, tested_file_id):
    if request.method == 'DELETE':
        return test_delete(request, tested_file_id)
    elif request.method == 'GET':
        return test_info(request, tested_file_id)
    elif request.method == 'PUT': # 不要求
        return test_change(request, tested_file_id)
    else:
        return JsonResponse({"errmsg":"请求有误"},status=400)

def test_info(request, tested_file_id):
    res = dict()
    willContinue = True
    try:
        test = Test_info.objects.get(id=tested_file_id)
        res = model_to_dict(test)
        res['tested_file']=BASE_URL+res['tested_file'].url
        # res['addTime'] = tested_file.addTime.strftime("%Y-%m-%d %H:%M")
    except:
        res = {"errmsg":"读取测试信息失败，可能您输入的测试文件已被删除"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def test_delete(request, tested_file_id):
    res = dict()
    willContinue = True
    try:
        tested_file = Test_info.objects.get(id=tested_file_id)
        os.remove(tested_file.tested_file.path)
        tested_file.delete()
        {"成功删除测试任务":tested_file_id}
    except:
        res = {"errmsg":"删除测试任务失败"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

from django.utils import timezone
def test_change(request, tested_file_id):
    res = dict()
    willContinue = True
    print(request.PUT)
    try:
        test = Test_info.objects.get(id=tested_file_id)
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
        # TODO 这里没测试有没有删除干净，包括文件
        service.delete()
        {"成功删除部署":service_id}
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
        # res['tested_file']=BASE_URL+res['tested_file'].url
        # res['addTime'] = tested_file.addTime.strftime("%Y-%m-%d %H:%M")
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
