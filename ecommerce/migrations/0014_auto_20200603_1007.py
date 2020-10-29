# Generated by Django 2.2.10 on 2020-06-03 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0013_auto_20200602_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='being_delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default=123, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='refund_accept',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_reuqest',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='revieved',
            field=models.BooleanField(default=False),
        ),
    ]