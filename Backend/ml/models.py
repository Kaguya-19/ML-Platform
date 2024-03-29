from django.db import models
import os
# Create your models here.
class Model_info(models.Model):
    file = models.FileField(upload_to='model_info')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300,blank=True,default='')
    model_type = models.CharField(max_length=10)
    input = models.JSONField(blank=True,null=True)
    output = models.JSONField(blank=True,null=True)
    algorithm = models.CharField(blank=True,null=True,max_length=50)
    engine = models.CharField(blank=True,null=True,max_length=50)
    add_time = models.DateTimeField(auto_now_add=True)

# 一个model->多个service
class Service_info(models.Model):
    name = models.CharField(max_length=100,default = 'default')
    description = models.TextField(max_length=300,blank=True,default='')
    mod = models.ForeignKey(to=Model_info, on_delete=models.CASCADE, null=True,related_name='model') # 对应的模型

    add_time = models.DateTimeField(auto_now_add=True)
    recent_modified_time = models.DateTimeField(auto_now=True)
    status = models.CharField(blank=True,default='deployed',max_length=20) #deployed,paused,undeployed
    # 调用次数，平均使用时间，mod
    average_use_time = models.IntegerField(blank=True,null=True,default=0) # 单位是秒
    min_use_time = models.IntegerField(blank=True,null=True,default=2147483647)
    max_use_time = models.IntegerField(blank=True,null=True,default=0)
    use_times = models.IntegerField(blank=True,null=True,default=0) # 使用次数
    func_str = models.TextField(blank=True,null=True,default='',max_length=100000)


# 一个service->多个test，或者test不对应service
class Test_info(models.Model):
    tested_file = models.FileField(upload_to='test_files_info')
    # 备注信息
    description = models.TextField(max_length=100,default= 'default')

    thread_ID = models.IntegerField(default=-1)
    task_ID = models.CharField(null=True,blank=True,max_length=100,default = 'default')

    status= models.CharField(blank=True,null=True,default='run',max_length=15) #run paused finished interrupted
    result = models.JSONField(blank=True,null=True)

    add_time = models.DateTimeField(auto_now_add=True)
    recent_modified_time = models.DateTimeField(auto_now=True)
    # endtime如果没完成的话隐藏显示
    end_time = models.DateTimeField(auto_now=True)

    # 对应model和service的外键
    mod = models.ForeignKey(to=Model_info, on_delete=models.CASCADE, null=True) 
    service = models.ForeignKey(to=Service_info, on_delete=models.CASCADE,blank = True,null=True,related_name='tests')