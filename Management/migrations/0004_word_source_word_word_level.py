# Generated by Django 4.2.11 on 2024-10-31 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Management", "0003_word_form"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="source",
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="word", name="word_level", field=models.IntegerField(default=0),
        ),
    ]
