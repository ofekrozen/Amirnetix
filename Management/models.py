from django.db import models
from Simulator.models import CustomUser, AnswerOption
from django.conf import settings

# Create your models here.

class Level_Choices(models.IntegerChoices):
    NOT_CHOSEN = 0,'O'
    PERFECT = 1,'✓'
    PARTIALLY = 2,'-'
    NOT_AT_ALL = 3,'✗'
    

class Word(models.Model):
    eng_word = models.CharField(max_length=50, unique=True)
    heb_word = models.CharField(max_length=50, blank=True, null=True)
    is_root = models.BooleanField(default=False)
    part_of_speech = models.CharField(max_length=20, choices=[
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('other', 'Other')
    ],default=None, blank=True, null=True)
    sublist = models.IntegerField(default=None, blank=True,null=True)  # AWL sublist (1-10)
    word_level = models.IntegerField(default=0, choices=Level_Choices.choices)
    source = models.CharField(max_length=50, default=None, blank=True, null=True)
    example_sentence = models.TextField(default=None, blank=True, null=True)
    usage_tips = models.TextField(default=None, blank=True, null=True)  # Tips to help learn the word in context

    class Meta:
        ordering = ['sublist', 'eng_word']

    def __str__(self):
        return f"{self.eng_word} - {self.heb_word} - {self.word_level}"
    
    def is_used(self):
        return AnswerOption.objects.filter(description__icontains=self.eng_word).exists()

class Word_Form(models.Model):
    root_word = models.ForeignKey(Word,on_delete=models.CASCADE)
    eng_word = models.CharField(max_length=50, unique=True)
    heb_word = models.CharField(max_length=50, blank=True, null=True)
    part_of_speech = models.CharField(max_length=20, choices=[
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('other', 'Other')
    ],default=None, blank=True, null=True)
    example_sentence = models.TextField(default=None, blank=True, null=True)
    usage_tips = models.TextField(default=None, blank=True, null=True)  # Tips to help learn the word in context

    class Meta:
        ordering = ['root_word', 'eng_word']

    def __str__(self):
        return f"root: {self.root_word.eng_word} form: {self.eng_word} - {self.heb_word}"

class Student_Word_Knowledge(models.Model):
    # LEVEL_CHOICES = [
    #     (0, '○'),  # 0: Not chosen
    #     (1, '✓'),  # 1: Perfect
    #     (2, '-'),  # 2: Partially
    #     (3, '✗'),  # 3: Not at all
    # ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    familiarity = models.IntegerField(choices=Level_Choices.choices)
    selection_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'word')
        ordering = ['student','selection_date','word']

    def __str__(self):
        return f"{self.student.username} - {self.word.eng_word}: {self.familiarity}"
