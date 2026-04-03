from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Financial Record Management Backend is Working</h1><p>Visit <a href='/api/'>/api/</a> for the API or <a href='/admin/'>/admin/</a> for the admin panel.</p>")

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('finance.urls')),
    path('api/auth/', include('users.urls')),
]