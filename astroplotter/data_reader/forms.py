# data_reader/forms.py

from django import forms
from data_reader.models import UploadedFile

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']