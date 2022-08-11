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

class Test_info(models.Model):
    tested_file = models.FileField(upload_to='test_files_info')