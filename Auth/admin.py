from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Simulator.models import (
    CustomUser,
    Simulator,
    Chapter,
    Question,
    AnswerOption,
    UserAnswer,
    SimulatorAttempt
)
from Management.models import *
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Simulator)
admin.site.register(Chapter)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(UserAnswer)
admin.site.register(SimulatorAttempt)
admin.site.register(Word)
admin.site.register(Word_Form)
admin.site.register(Student_Word_Knowledge)