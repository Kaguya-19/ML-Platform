from django.urls import path

from . import views

app_name = 'ml'
urlpatterns = [
    path('model', views.model_api),
    path('model/<int:model_id>', views.model_info_api),
    path('test',views.test_api),
    path('test/<int:tested_file_id>',views.test_info_api),
    path('test/quick/<int:model_id>', views.test_quick),
    path('test/task', views.new_task), # 选择好模型开始测试
    # 部署
    path('service',views.service_api),
    path('service/<int:service_id>',views.service_info_api),
]
