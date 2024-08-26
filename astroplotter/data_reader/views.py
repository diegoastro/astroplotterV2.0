from django.shortcuts import render, redirect
from .forms import UploadedFileForm
from .models import UploadedFile, FileColumn
from astropy.table import Table
import os

def home(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UploadedFileForm()
    return render(request, 'data_reader/home.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            print(f"Debug: File saved with path '{uploaded_file.file.path}'")

            # Determine the file extension
            file_path = uploaded_file.file.path
            file_extension = os.path.splitext(file_path)[1].lower()

            # Try to read the file based on its extension
            try:
                if file_extension in ['.csv']:
                    df = Table.read(file_path, format='csv')
                elif file_extension in ['.txt', '.dat']:
                    df = Table.read(file_path, format='ascii')
                else:
                    return render(request, 'data_reader/upload.html', {
                        'form': form,
                        'error': 'Unsupported file type. Please upload a CSV or ASCII file.'
                    })
                print(f"Debug: File read successfully with columns: {df.colnames}")
            except Exception as e:
                print(f"Debug: Error reading file: {e}")
                return render(request, 'data_reader/upload.html', {
                    'form': form,
                    'error': f'Error reading file: {e}'
                })

            # Save the column names
            for column in df.colnames:
                print(f"Debug: Saving column '{column}' for file '{uploaded_file}'")
                FileColumn.objects.create(file=uploaded_file, column_name=column)

            return redirect('data_reader:upload_success')
        else:
            print("Debug: Form is not valid")
            print(form.errors)
    else:
        form = UploadedFileForm()
    return render(request, 'data_reader/upload.html', {'form': form})

def upload_success(request):
    return render(request, 'data_reader/upload_success.html')
