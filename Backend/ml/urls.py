from django.urls import path

from . import views

app_name = 'ml'
urlpatterns = [
    path('model/add', views.model_add),
    path('model/<int:model_id>', views.model_info),
    path('test/add',views.test_file_add),
]
