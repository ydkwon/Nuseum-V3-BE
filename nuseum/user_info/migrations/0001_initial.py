# Generated by Django 4.1.5 on 2023-11-15 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User_Affliction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('affliction', models.CharField(default='None', max_length=200, verbose_name='고민')),
                ('affliction_detail', models.CharField(default='None', max_length=200, verbose_name='고민상세')),
            ],
            options={
                'verbose_name': '사용자 고민',
                'verbose_name_plural': '사용자 고민',
                'db_table': 'USERAFFLICTION_TB',
                'managed': True,
            },
        ),
    ]
