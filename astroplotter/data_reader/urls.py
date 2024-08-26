
from django.urls import path
from . import views
from .views import upload_file, upload_success


app_name = 'data_reader'


urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload_success/', views.upload_success, name='upload_success'),
]