# Generated by Django 4.2.11 on 2024-10-25 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Simulator", "0002_alter_useranswer_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="answeroption",
            name="hebrew_desc",
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="question",
            name="hebrew_desc",
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="chapter_type",
            field=models.CharField(
                choices=[
                    ("SC", "Sentence Completion"),
                    ("RC", "Reading Comprehension"),
                    ("RS", "Restatement"),
                    ("OT", "Other"),
                ],
                max_length=2,
            ),
        ),
    ]
