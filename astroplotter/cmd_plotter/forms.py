#cmd_plotter/forms.py
from django import forms
from data_reader.models import UploadedFile, FileColumn
import pandas as pd

class ColumnSelectionForm(forms.Form):
    uploaded_file = forms.ModelChoiceField(queryset=UploadedFile.objects.all(), label="Select File")
    x_column = forms.ChoiceField(label="Select X-axis Column", required=True)
    y_column = forms.ChoiceField(label="Select Y-axis Column", required=True)
    use_color_column = forms.BooleanField(label="Use Auxiliar Column", required=False)
    color_column = forms.ChoiceField(label="Select Auxiliar Column", required=False)
    colorscale_choice = forms.ChoiceField(label="Select Color Scale", choices=[
        ('Rainbow', 'Rainbow'),
        ('Viridis', 'Viridis'),
        ('Jet', 'Jet'),
        ('Hot', 'Hot'),
        ('Electric', 'Electric')
    ], required=False)
    invert_x_axis = forms.BooleanField(label="Flip X-axis", required=False)
    invert_y_axis = forms.BooleanField(label="Flip Y-axis", required=False)
    log_x_axis = forms.BooleanField(label="Log X-axis", required=False)
    log_y_axis = forms.BooleanField(label="Log Y-axis", required=False)

    def __init__(self, *args, **kwargs):
        uploaded_files = kwargs.pop('uploaded_files', None)
        super().__init__(*args, **kwargs)
        
        if uploaded_files:
            self.fields['uploaded_file'].queryset = uploaded_files

        if 'uploaded_file' in self.data:
            try:
                file_id = int(self.data.get('uploaded_file'))
                self.fields['x_column'].choices = self.get_column_choices(file_id)
                self.fields['y_column'].choices = self.get_column_choices(file_id)
                self.fields['color_column'].choices = self.get_column_choices(file_id)
            except (ValueError, TypeError) as e:
                print(f"Debug: Exception in form init: {e}")

    def get_column_choices(self, file_id):
        columns = FileColumn.objects.filter(file_id=file_id).values_list('column_name', 'column_name')
        return list(columns)

    def clean(self):
        cleaned_data = super().clean()
        use_color_column = cleaned_data.get('use_color_column', False)
        color_column = cleaned_data.get('color_column')

        if use_color_column and not color_column:
            self.add_error('color_column', 'Please select an auxiliary column if "Use Auxiliar Column" is checked.')

        return cleaned_data
