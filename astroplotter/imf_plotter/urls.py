from django.urls import path
from .views import imf_plot, data_download

app_name = 'imf_plotter'

urlpatterns = [
    path('', imf_plot, name='imf_plot'),
    path('download/', data_download, name='data_download'),
]