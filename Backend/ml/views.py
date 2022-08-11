from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.core import serializers
# Create your views here.
from .models import Model_info,Test_info
from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie

def model_add_singlemodel(name,description,model_type,file):
    model = Model_info.objects.create(name=name,description=description,model_type=model_type,file=file)
    return model

import rarfile,zipfile
import os
from .ml import get_model_info

@ensure_csrf_cookie
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
        models = Model_info.objects.order_by('id').values('name','model_type','id')
        context = {'models':list(models)} #TODO:page
        return JsonResponse(context)
    except:
        return JsonResponse({"errmsg":"获取信息失败"},status=400)

def model_info(request, model_id):
    res = dict()
    willContinue = True
    try:
        model = Model_info.objects.get(id=model_id)
        res = model_to_dict(model)
        res['file']=None
    except:
        res = {"errmsg":"读取模型信息失败"}
        willContinue = False
    resp = JsonResponse(res, json_dumps_params={'ensure_ascii':False})
    if willContinue:
        resp.status_code = 200
    else:
        resp.status_code = 400
    return resp

def test_file_add_single(file):
    Test_info.objects.create(file=file)

def test_file_add(request):
    if request.method != 'POST':
        return HttpResponse("上传测试文件失败")
    else:
        add_mode = request.POST.get('add_mode')
        if add_mode == 'single':
            test_file_add_single(file = request.FILES['file'])
            return HttpResponse('单个测试文件上传成功')
        else:
            # TODO：后续可增加查看单一文件功能
            test_file_add_single(file = request.FILES['file'])
            return HttpResponse('压缩文件下测试文件上传成功')


from .ml import batch_predict,quick_predict

def test_singlefile(request, test_file_id ,mode = 'single'):
    tested_file_path =  Test_info.objects.filter(id=test_file_id).first().file.path
    tested_model_type = '.onnx' # path[-4:]
    
    f = open(tested_file_path)
    tested_file = f.read()
    f.close()
    
    if mode == 'single':
        tested_model_path = tested_file_path
        tested_result = quick_predict(tested_model_path,type = tested_model_type,x_test = tested_file)
    else:
        # TODO 好像没解压缩,这里要加一个接口
        tested_result = batch_predict(path = tested_model_path, type = tested_model_type,x_test = tested_file)
    return JsonResponse(tested_result, mode)


# 测试
if __name__ == "__main__":
    print('enter views.main')
    current_work_dir = os.path.dirname (__file__)
    tested_file_path = current_work_dir + '/test.onnx'
    f = open(tested_file_path)
    tested_file = f.read()
    Test_info.objects.create(tested_file)
