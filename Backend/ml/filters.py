import django_filters

class textFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description',lookup_expr='icontains')