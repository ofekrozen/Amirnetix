from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name='simulator_list'),
    path("simulator/<int:simulator_id>",views.start_simulator,name="start_simulator"),
    path("finish_simulator/",views.finish_simulator,name="finish_simulator"),
]