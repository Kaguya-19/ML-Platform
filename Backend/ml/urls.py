from django.urls import path

from . import views

app_name = 'ml'
urlpatterns = [
    path('model/add', views.model_add),
    path('model/<int:model_id>', views.model_info),
    path('model/delete/<int:model_id>', views.model_delete),
    path('test/add', views.test_file_add), # 测试文件添加
    path('test/task', views.new_task) # 选择好模型开始测试
]
