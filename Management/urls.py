from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name='index'),
    path("edit_test/<int:simulator_id>", views.edit_test,name='edit_test'),
    path("generate/", views.generate_test,name='generate_test'),
    path("save_new_simulator/", views.save_new_simulator,name='save_new_simulator'),
    path("save_edited_simulator/", views.save_edited_simulator,name='save_edited_simulator'),
    path("translate/<int:simulator_id>",views.add_simulator_heb_translation,name='translate'),
    path("upload_words/<str:list_type>",views.upload_words,name='upload_words'),
    path("create_simulator/",views.create_simulator, name='create_simulator'),
    path('admin/fetch-unused-words/', views.fetch_unused_words, name='fetch_unused_words'),
    path("select_2/",views.select_2, name='select_2'),
    path("first_100/",views.first_100, name='first_100'),
]