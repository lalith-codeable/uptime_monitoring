from django.contrib import admin
from django.urls import path, include
from uptime_monitor import views

urlpatterns = [
    path('',views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('http_server.urls')),
]

handler404 = 'uptime_monitor.views.error_404_view'