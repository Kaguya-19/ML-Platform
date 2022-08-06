from django.db import models

# Create your models here.
class Model_info(models.Model):
    file = models.FileField(upload_to='model_info')

class Test_info(models.Model):
    tested_file = models.FileField(upload_to='test_files_info')