from celery import shared_task, current_task

@shared_task
def add(x, y):
    return x + y

from .models import Model_info,Test_info,Service_info
import cv2
import zipfile
import numpy as np
from .pre_process_example import defualt_process
from django.utils import timezone
from .ml import batch_predict,quick_predict
from threading import local
import re
import os

preprocess_data=local()

def makeKeraspath(path):
    current_work_dir = os.path.dirname(path)
    return current_work_dir + '/' + os.path.basename(path)[:-4]

@shared_task
def new_task_thread(test_file_id , service_id):
    test_task =  Test_info.objects.get(id=test_file_id)
    test_file = test_task.tested_file
    res = {}
    test_task.result = res
    test_task.save()
    tested_model_type = test_task.mod.model_type
    if tested_model_type == 'keras':
        model_path = makeKeraspath(model_path)
    tested_model_path = test_task.mod.file.path
    service = Service_info.objects.get(id=service_id)
    print("In Thread")
    try:
        input_info = test_task.mod.input
        if tested_model_type == 'pmml':
            input_shape = len(input_info)
        elif tested_model_type == 'onnx':
            input_shape = input_info[0]['shape']
            if input_shape[0] == "batch_size":
                input_shape = input_shape[1:]
        elif tested_model_type == 'keras':
            input_shape = input_info[0]['shape']
            input_shape = input_shape[1:]
        else:
            return
        x_test=[]
        if service.func_str != '':
            global preprocess_data
            func_str = service.func_str 
        if '.zip' in test_file.name:
            with zipfile.ZipFile(test_file.path, mode='r') as zfile:  # 只读方式打开压缩包
                for name in zfile.namelist():  # 获取zip文档内所有文件的名称列表
                    if service.func_str != '':
                        with zfile.open(name, 'r') as file_to_read:
                            print('fuck1') 
                            preprocess_data.input = file_to_read
                            preprocess_data.result = {}
                            exec(func_str)
                            # preprocessed_res = preprocess_result['result']
                            x_test.append(preprocess_data.result)
                    else:
                        if '.jpg' in name:
                            with zfile.open(name, mode='r') as image_file:
                                content = image_file.read()  # 一次性读入整张图片信息
                                image = np.asarray(bytearray(content), dtype='uint8')
                                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                                image = defualt_process(image)
                                x_test.append(image[0])
                                # cv2.imshow('image', image)
                        elif '.txt' in name:
                            with zfile.open(name, 'r') as file_to_read:  # 打开文件，将其值赋予file_to_read
                                while True:
                                    lines = file_to_read.readline()  # 整行读取数据
                                    if not lines:  # 若该行为空
                                        break  # 喀嚓
                                    else:
                                        this_lines = re.split(r"\s|,|;",lines)
                                        number_this_lines = [float(x) for x in this_lines]
                                        if len(number_this_lines) != np.prod(input_shape):
                                            res = {"errmsg":"输入的文本行数据量不适配此模型"}
                                            test_task.result = res
                                            test_task.status = 'interrupted'
                                            test_task.save()
                                            return
                                        x_test.append(list(np.array(number_this_lines).reshape(tuple(input_shape))))
                        elif '.csv' in test_file.name:
                            with open(test_file.path, mode='r', encoding='utf-8') as f:
                                if service.func_str != '': 
                                    preprocess_data.input = f
                                    preprocess_data.result = {}
                                    exec(func_str)
                                    # preprocessed_res = preprocess_result['result']
                                    x_test.append(preprocess_data.result)
                                else:
                                    input_file_string = f.read()
                                    input_file_list = input_file_string.split('\n')
                                    # 发现有时候最后会多一行，去掉
                                    if input_file_list[-1] == "":
                                        input_file_list.pop()
                                    for line in input_file_list:
                                        # 使用zip将两组数据打包成字典
                                        tmp_data = line.split(',')
                                        number_tmp_data = [float(x) for x in tmp_data]
                                        if len(number_tmp_data) != np.prod(input_shape):
                                            continue
                                        x_test.append(number_tmp_data)
                                zfile.close()
        elif '.jpg' in test_file.name:
            content = cv2.imread(test_file.path)
            image = defualt_process(content)
            x_test.append(image[0])
            # cv2.imshow('image', image)
        elif '.txt' in test_file.name:
            with open(test_file.path, mode='r', encoding='utf-8') as f:  # 打开文件，将其值赋予file_to_read
                input_file_string = f.read()
                input_file_list = input_file_string.split('\n')
                # 发现有时候最后会多一行，去掉
                if input_file_list[-1] == "":
                    input_file_list.pop()
                for line in input_file_list:
                    # 使用zip将两组数据打包成字典
                    tmp_data = re.split(r"\s|,|;",line)
                    number_tmp_data = [float(x) for x in tmp_data]
                    if len(number_tmp_data) != np.prod(input_shape):
                        continue
                    x_test.append(number_tmp_data)
                    
                
                # zfile.close()
        elif '.csv' in test_file.name:
            with open(test_file.path, mode='r', encoding='utf-8') as f:
                if service.func_str != '': 
                    preprocess_data.input = f
                    preprocess_data.result = {}
                    exec(func_str)
                    # preprocessed_res = preprocess_result['result']
                    x_test.append(preprocess_data.result)
                else:
                    input_file_string = f.read()
                    input_file_list = input_file_string.split('\n')
                    # 发现有时候最后会多一行，去掉
                    if input_file_list[-1] == "":
                        input_file_list.pop()
                    for line in input_file_list:
                        # 使用zip将两组数据打包成字典
                        tmp_data = line.split(',')
                        number_tmp_data = [float(x) for x in tmp_data]
                        if len(number_tmp_data) != np.prod(input_shape):
                            continue
                        x_test.append(number_tmp_data)
        else:
            res = {"errmsg":"不支持处理该类型文件"}
            test_task.result = res
            test_task.status = 'interrupted'
            test_task.save()
            return
        x_test = np.array(x_test).astype(np.float32)
        print(x_test)
        res = batch_predict(path = tested_model_path, type = tested_model_type,x_test = x_test)
    except:
        import traceback
        res = {"errmsg":traceback.format_exc()}
        test_task.result = res
        test_task.status = 'interrupted'
        test_task.save()
        return
    test_task.result = res
    test_task.status = 'finished'
    test_task.recent_modified_time = timezone.now()
    test_task.end_time = timezone.now()
    test_task.save()
    deltaTime = (test_task.end_time - test_task.add_time).total_seconds()*1000
    service.average_use_time = \
        (service.average_use_time * service.use_times + deltaTime)/(service.use_times + 1)
    service.use_times = service.use_times + 1
    if deltaTime > service.max_use_time:
        service.max_use_time = deltaTime
    if deltaTime < service.min_use_time:
        service.min_use_time = deltaTime
    service.save()
    test_task.save()        
    return
