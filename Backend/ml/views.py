import threading

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.core.paginator import  Paginator
import datetime
# Create your views here.
from .models import Model_info,Test_info
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

def test_file_add_single(file):
    model = Test_info.objects.create(tested_file=file)
    return model

def test_file_add(request):
    if request.method != 'POST':
        return HttpResponse("上传测试文件失败")
    else:
        add_mode = request.POST.get('add_mode')
        if add_mode == 'single':
            test_file_add_single(file = request.FILES['tested_file'])
            return HttpResponse('单个测试文件上传成功')
        else:
            # TODO：后续可增加查看单一文件功能
            test_file_add_single(file = request.FILES['tested_file'])
            return HttpResponse('压缩文件下测试文件上传成功')

from .ml import batch_predict,quick_predict
from threading import Thread
import cv2
import zipfile
import numpy as np

def start_test(test_file_id , model_id, mode = 'single'):
    test_task =  Test_info.objects.get(id=test_file_id)
    test_file = test_task.file
    test_task.mod = Model_info.objects.get(id=model_id)
    test_task.threadID = threading.currentThread().ident
    test_task.is_finished = False
    test_task.save()
    tested_model_type = test_task.mod.model_type
    tested_model_path = test_task.mod.file.path
    res = {}
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
        test_task.save()
    return JsonResponse(res)

def new_task(request, test_file_id, mode = 'single'):
    model_id = request.POST.get['model_id']
    param_tuple = (test_file_id, model_id, mode)
    new_thread = Thread(target=start_test, args=param_tuple)
    new_thread.start()

# 测试
if __name__ == "__main__":
    print('enter views.main')
    current_work_dir = os.path.dirname (__file__)
    tested_file_path = current_work_dir + '/test.onnx'
    f = open(tested_file_path)
    tested_file = f.read()
    Test_info.objects.create(tested_file)
