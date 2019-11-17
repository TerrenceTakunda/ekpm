# Generated by Django 2.2.6 on 2019-11-07 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0012_auto_20191107_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(choices=[('Residential', 'Residential'), ('Apartment Building', 'Apartment Building'), ('Office', 'Office'), ('Industrial', 'Industrial'), ('Commercial', 'Commercial'), ('Agricultural', 'Agricultural'), ('Land', 'Land'), ('Other', 'Other')], max_length=55),
        ),
    ]