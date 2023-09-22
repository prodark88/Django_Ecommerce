# Generated by Django 4.2.4 on 2023-09-21 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_rename_varitation_category_variation_variation_category_and_more'),
        ('orders', '0002_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='size',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='variation',
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='variation',
            field=models.ManyToManyField(blank=True, to='store.variation'),
        ),
    ]
