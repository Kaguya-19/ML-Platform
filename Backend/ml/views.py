from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.
from .models import Model_info,Test_info


def model_add_singlemodel(file):
    Model_info.objects.create(file)

import rarfile,zipfile
import os
def model_add(request,add_mode = 'single'):
    if request.method == 'GET':
        return HttpResponse("上传模型失败")
    if request.method == 'POST':
        if add_mode == 'single':
            model_add_singlemodel(file = request.FILES['file'])
            return HttpResponse('单个模型上传成功')
        else:
            # 解压zip/rar的模型文件并保存至model
            current_work_dir = os.path.dirname (__file__)
            tmp_models_dir = current_work_dir + '/tmpTest'

            if not os.path.exists(tmp_models_dir):
                os.makedirs(dir)

            src_file = request.FILES['file']
            file_type = '.zip'

            if file_type == '.zip':
                # 需要安装zip包：pip install zipp
                zip_file = zipfile.ZipFile(src_file)
                for names in zip_file.namelist():
                    zip_file.extract(names, tmp_models_dir)
                zip_file.close()
            elif file_type == '.rar':
                # 需要安装rar包：pip install rarfile
                rar = rarfile.RarFile(src_file)
                os.chdir(tmp_models_dir)
                rar.extractall()
                rar.close()

            # TODO 多线程     
            files=os.listdir(tmp_models_dir)
            for i in files:
                file_path=os.path.join(tmp_models_dir+i)
                f = open(file_path)
                file = f.read()
                f.close()
                model_add_singlemodel(file)
            pass
            return HttpResponse('压缩文件下模型上传成功')



from .ml import get_model_info
def model_info(request, model_id):
    model_path = Model_info.objects.filter(id=model_id).first().file.path
    info = get_model_info(model_path, model_path[-4:])
    return JsonResponse(info)

def test_file_add_single(file):
    Test_info.objects.create(file)

def test_file_add(request):
    if request.method == 'GET':
        return HttpResponse("上传测试文件失败")
    if request.method == 'POST':
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
