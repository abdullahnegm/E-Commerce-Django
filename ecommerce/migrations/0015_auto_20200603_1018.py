# Generated by Django 2.2.10 on 2020-06-03 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0014_auto_20200603_1007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='refund_reuqest',
            new_name='received',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='revieved',
            new_name='refund_request',
        ),
    ]
