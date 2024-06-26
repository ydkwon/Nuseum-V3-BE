# Generated by Django 4.1.5 on 2023-08-11 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='이 사용자의 특정 권한입니다.사용자는 그룹별로 부여된 모든 권한을 받게 됩니다.', related_name='custom_users_permissions', to='auth.permission', verbose_name='사용자 권한'),
        ),
        migrations.DeleteModel(
            name='NormalUser',
        ),
    ]
