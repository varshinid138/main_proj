# Generated by Django 5.1 on 2024-09-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='videos/')),
                ('converted_text', models.FileField(blank=True, null=True, upload_to='converted/')),
            ],
        ),
    ]
