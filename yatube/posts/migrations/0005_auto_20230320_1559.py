# Generated by Django 2.2.16 on 2023-03-20 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='media/', verbose_name='Картинка'),
        ),
    ]
