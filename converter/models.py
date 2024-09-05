from django.db import models

class Video(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    converted_text = models.FileField(upload_to='converted/', null=True, blank=True)

    def __str__(self):
        return self.name