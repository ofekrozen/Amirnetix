from django.db import models
from Auth.models import CustomUser
from django.core.exceptions import ValidationError
from datetime import datetime

# Create your models here.
class SimulatorLevel(models.IntegerChoices):
    MIX = 0, 'Mix'
    EASY = 1, 'Easy'
    MEDIUM = 2, 'Medium'
    HARD = 3, 'Hard'

class Simulator(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    level = models.IntegerField(choices=SimulatorLevel.choices, default=SimulatorLevel.MIX)
    create_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_last_attempt(self, user: CustomUser):
        try:
            return SimulatorAttempt.objects.filter(user=user, simulator=self).order_by('-start_time').first()
        except:
            return None
        

class ChapterType(models.TextChoices):
    SENTENCE_COMPLETION = 'SC', 'Sentence Completion'
    READING_COMPREHENSION = 'RC', 'Reading Comprehension'
    RESTATEMENT = 'RS', 'Restatement'
    OTHER = 'OT', 'Other'

class Chapter(models.Model):
    simulator = models.ForeignKey(Simulator, on_delete=models.CASCADE, related_name='chapters')
    order = models.PositiveIntegerField()
    chapter_type = models.CharField(max_length=2, choices=ChapterType.choices)
    title = models.CharField(max_length=100)
    time_limit = models.PositiveIntegerField(help_text="Time in minutes")
    reading_text = models.TextField(blank=True, null=True)  # Only for Reading Comprehension
    hebrew_text = models.TextField(blank=True,null=True)

    class Meta:
        unique_together = ('simulator', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.simulator} - chapter number {self.order} - {self.chapter_type}"
    
    def clean(self):
        super().clean()
        if self.chapter_type == ChapterType.READING_COMPREHENSION and not self.reading_text:
            raise ValidationError('Reading Comprehension chapters must have reading_text.')
        elif self.chapter_type != ChapterType.READING_COMPREHENSION and self.reading_text:
            raise ValidationError('Non Reading Comprehension chapters must not have a reading_text.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def count_questions(self):
        return Question.objects.filter(chapter = self).count()

class Question(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField()
    description = models.TextField()
    hebrew_desc = models.TextField(default=None, null=True, blank=True)

    class Meta:
        unique_together = ('chapter', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter} - question number {self.order}"
    
    def clean(self):
        super().clean()
        correct_answers = AnswerOption.objects.filter(question = self, is_correct = True).count()
        # correct_answers = self.answer_options.filter(is_correct=True).count()
        if correct_answers > 1:
            raise ValidationError('Each question must have exactly one correct answer.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    order = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    hebrew_desc = models.TextField(default=None, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('question', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.question} - Option number {self.order}"

class SimulatorAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='simulator_attempts')
    simulator = models.ForeignKey(Simulator, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.simulator.name} - Attempt on {self.start_time}"
    
    def get_success_rate(self):
        user_answers = UserAnswer.objects.filter(simulator_attempt = self).all()
        question_cnt = Question.objects.filter(chapter__simulator = self.simulator).count()
        cnt_correct = 0
        for ans in user_answers:
            if ans.selected_option.is_correct:
                cnt_correct += 1
        return round(cnt_correct/question_cnt,2)
    
    def get_user_answer(self, question):
        """
        Returns the UserAnswer instance for a given question.
        """
        return self.user_answers.filter(question=question).first()
    
    def Success_Rates(self):
        all_questions = UserAnswer.objects.filter(simulator_attempt = self).all()
        success_rates = {
            'Total':{
                'total':0,
                'correct':0
            },
            'SC':{
                'total':0,
                'correct':0
            },
            'RC':{
                'total':0,
                'correct':0
            },
            'RS':{
                'total':0,
                'correct':0
            }
        }
        for q in all_questions:
            success_rates['Total']['total'] += 1
            chapter_type = q.question.chapter.chapter_type
            if q.question.chapter.chapter_type in success_rates.keys():
                success_rates[chapter_type]['total'] += 1
                if q.selected_option.is_correct:
                    success_rates['Total']['correct'] += 1
                    success_rates[chapter_type]['correct'] += 1
        for key in success_rates:
            correct = success_rates[key]['correct']
            total = success_rates[key]['total']
            if total > 0:
                success_rates[key]['success_rate'] = int(round(correct/total,2)*100)
            else:
                success_rates[key]['success_rate'] = 0
        return success_rates
    
    def Answer_Times(self):
        all_questions = UserAnswer.objects.filter(simulator_attempt = self).order_by('timestamp').all()
        last_time = self.start_time
        times = {'q_times':{},'averages':{'Total': 0,'SC':0,'RS':0,'RC':0}}
        for q in all_questions:
            q_type = q.question.chapter.chapter_type
            q_id = q.id
            try:
                answer_time = (q.timestamp - last_time).total_seconds()
                times['q_times'][f'{q_type}_{q_id}'] = answer_time
                times['averages']['Total'] += answer_time
                times['averages'][q_type] += answer_time
                last_time = q.timestamp
            except:
                pass
        for key in times['averages']:
            total_for_key = self.Success_Rates()[key]['total']
            if total_for_key > 0:
                times['averages'][key] = round(times['averages'][key] / total_for_key,2)
            else:
                times['averages'][key] = 0
        return times

class UserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_answers')
    simulator_attempt = models.ForeignKey(SimulatorAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('user','simulator_attempt', 'question')

    def __str__(self):
        return f"{self.user.username} - {self.selected_option}"
    