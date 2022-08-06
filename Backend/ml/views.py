from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
# Create your views here.
from .models import Model_info
def model_add(request):
    if request.method == 'GET':
        return HttpResponse("上传失败")
    if request.method == 'POST':
        Model_info.objects.create(file=request.FILES['file'])

from .ml import get_model_info
def model_info(request, model_id):
    model_path = Model_info.objects.filter(id=model_id).first().file.path
    info = get_model_info(model_path, model_path[-4:])
    return JsonResponse(info)
