from django.db import models

# Create your models here.
class Model_info(models.Model):
    file = models.FileField(upload_to='model_info')