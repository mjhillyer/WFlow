# Generated by Django 3.0.7 on 2020-08-04 02:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0023_auto_20200802_0119'),
    ]

    operations = [
        migrations.AddField(
            model_name='poam',
            name='controls',
            field=models.CharField(blank=True, help_text='Comma delimited list of security controls affected by the weakness identified.', max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='milestone_changes',
            field=models.TextField(blank=True, help_text='List of changes to milestones.', null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='milestones',
            field=models.TextField(blank=True, help_text='One or more milestones that identify specific actions to correct the weakness with an associated completion date.', null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='poam_id',
            field=models.IntegerField(blank=True, help_text='The sequential ID for the information system', null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='remediation_plan',
            field=models.TextField(blank=True, help_text='A high-level summary of the actions required to remediate the plan.', null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='risk_rating_adjusted',
            field=models.CharField(blank=True, help_text='The current or modified risk rating of the weakness.', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='risk_rating_original',
            field=models.CharField(blank=True, help_text='The initial risk rating of the weakness.', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='scheduled_completion_date',
            field=models.CharField(blank=True, help_text='Comma.', max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='weakness_detection_source',
            field=models.CharField(blank=True, help_text=' Name of organization, vulnerability scanner, or other entity that first identified the weakness.', max_length=180, null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='weakness_name',
            field=models.CharField(blank=True, help_text='Name for the identified weakness that provides a general idea of the weakness.', max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='poam',
            name='weakness_source_identifier',
            field=models.CharField(blank=True, help_text='ID or reference provided by the detection source identifying the weakness.', max_length=180, null=True),
        ),
        migrations.AlterField(
            model_name='poam',
            name='statement',
            field=models.ForeignKey(help_text='The Poam details for this statement. Statement must be type Poam', on_delete=django.db.models.deletion.CASCADE, related_name='poam', to='controls.Statement'),
        ),
        migrations.AlterField(
            model_name='statement',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='A UUID (a unique identifier) for this Statement.'),
        ),
    ]