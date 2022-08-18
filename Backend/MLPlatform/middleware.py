from django.utils.deprecation import MiddlewareMixin
from django.http.multipartparser import MultiPartParser
from django.http.request import QueryDict
 # from https://blog.csdn.net/qq_36320532/article/details/90037342
 
class RestfulMiddleware(MiddlewareMixin):
 
    def process_request(self, request):
        if request.method == 'PUT':
            # 前端是axios请求时应用以下代码
            put = MultiPartParser(request.META, request, request.upload_handlers).parse()
            request.PUT = put[0]
