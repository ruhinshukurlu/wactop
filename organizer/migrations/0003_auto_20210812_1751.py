# Generated by Django 3.0.4 on 2021-08-12 13:51

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizer', '0002_auto_20210727_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizer',
            name='about',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
