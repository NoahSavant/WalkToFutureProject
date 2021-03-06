# Generated by Django 4.0.3 on 2022-04-10 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_customer_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('description', models.TextField()),
                ('brand', models.CharField(max_length=150)),
                ('size', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('color', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='images')),
                ('slug', models.SlugField()),
            ],
        ),
    ]
