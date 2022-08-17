import django_filters

from .models import Model_info

class ModelFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',lookup_expr='icontains')  
    class Meta:
        model = Model_info
        fields = ['name',]