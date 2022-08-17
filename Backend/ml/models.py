from django.db import models

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
    addTime = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(blank=True,null=True,default=0) #0:Undeploy, 1:Deployed, 2:pause

class Test_info(models.Model):
    tested_file = models.FileField(upload_to='test_files_info')
    # 备注信息
    message = models.CharField(max_length=100,default= 'default')
    # model的id
    mod = models.ForeignKey(to=Model_info, on_delete=models.CASCADE, null=True)
    thread_ID = models.IntegerField(default=-1)
    is_finished = models.BooleanField(blank=True,null=True,default=False)
    result = models.JSONField(blank=True,null=True)