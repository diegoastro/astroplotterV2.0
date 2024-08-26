from django import forms
from data_reader.models import UploadedFile, FileColumn
import pandas as pd

class IMFPlotForm(forms.Form):
    uploaded_file = forms.ModelChoiceField(queryset=UploadedFile.objects.all(), label="Select File")
    mass_column = forms.ChoiceField(label="Select the 'mass column'", required=True)
    log_scale = forms.BooleanField(label="Data is in logartihmic scale", required=False)
    def __init__(self, *args, **kwargs):
        uploaded_files = kwargs.pop('uploaded_files', None)
        super().__init__(*args, **kwargs)
        
        if uploaded_files:
            self.fields['uploaded_file'].queryset = uploaded_files

        if 'uploaded_file' in self.data:
            try:
                file_id = int(self.data.get('uploaded_file'))
                self.fields['mass_column'].choices = self.get_column_choices(file_id)
            except (ValueError, TypeError) as e:
                print(f"Debug: Exception in form init: {e}")

    def get_column_choices(self, file_id):
        columns = FileColumn.objects.filter(file_id=file_id).values_list('column_name', 'column_name')
        return list(columns)
