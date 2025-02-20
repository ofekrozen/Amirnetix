from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name='analysis'),
    path("analyze_simulator/<int:simulator_id>",views.analyze_simulator, name='analyze_simulator'),
    path("vocab_home/",views.vocab_home, name='vocab_home'),
    path("english_vocab/", views.english_vocab,name='english_vocab'),
    path("update_familiarity/", views.update_familiarity, name='update_familiarity'),
]