# Generated by Django 2.1.7 on 2019-02-18 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0006_gebiedsgerichtwerkenpraktijkgebieden'),
    ]

    operations = [
        migrations.AddField(
            model_name='grootstedelijkgebied',
            name='gsg_type',
            field=models.CharField(max_length=5, null=True),
        ),
    ]
