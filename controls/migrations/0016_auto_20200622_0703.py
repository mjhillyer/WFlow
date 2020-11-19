# Generated by Django 3.0.7 on 2020-06-22 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0015_elementcommoncontrol'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statement',
            options={'ordering': ['producer_element__name', 'sid'], 'permissions': [('can_grant_smt_owner_permission', 'Grant a user statement owner permission')]},
        ),
        migrations.AddIndex(
            model_name='statement',
            index=models.Index(fields=['producer_element'], name='producer_element_idx'),
        ),
    ]