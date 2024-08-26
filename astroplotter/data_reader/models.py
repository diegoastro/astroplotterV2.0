# data_reader/models.py

from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class FileColumn(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=100)

    def __str__(self):
        return self.column_name
