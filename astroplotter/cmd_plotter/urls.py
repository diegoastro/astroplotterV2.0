# cmd_plotter/urls.py

from django.urls import path
from .views import plot_cmd

app_name = 'cmd_plotter'

urlpatterns = [
    path('plot-cmd/', plot_cmd, name='plot_cmd'),
    
]
