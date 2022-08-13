from django.urls import path

from . import views

app_name = 'ml'
urlpatterns = [
    path('model', views.model_api),
    path('model/<int:model_id>', views.model_info_api),
    path('test/add',views.test_file_add),
]
