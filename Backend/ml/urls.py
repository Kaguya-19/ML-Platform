from django.urls import path

from . import views

app_name = 'ml'
urlpatterns = [
    path('model', views.model_api),
    path('model/<int:model_id>', views.model_info_api),
    path('test',views.test_api),
    path('test/<int:test_id>',views.test_info_api),
    # 部署
    path('deploy',views.service_api),
    path('deploy/<int:service_id>',views.service_info_api),
    path('deploy/<int:deploy_id>/task',views.task_add),
    # path('celery/get',views.get_result_by_taskid),
    # path('celery/test',views.task_add_view)
]

