from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
import sys, traceback

def custom_500_handler(request):
    exc_type, exc_value, _ = sys.exc_info()
    return JsonResponse({
        'error': 'Internal Server Error',
        'type': str(exc_type),
        'value': str(exc_value),
        'traceback': traceback.format_exc()
    }, status=500)

handler500 = custom_500_handler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('buggyman.urls')),
]
