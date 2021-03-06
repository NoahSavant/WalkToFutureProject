# Generated by Django 4.0.3 on 2022-04-20 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_cart_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='color',
        ),
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
        migrations.CreateModel(
            name='Size_Quantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]
