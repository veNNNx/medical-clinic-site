from django.urls import path
from django.contrib import admin
from django.urls import path, include  # new
from . import views

urlpatterns = [
    path("", views.home),
    path("home", views.home),
    path("sign-up", views.sign_up),
    path("create-post", views.create_post),
    path("schedule", views.schedule),
    path("patients", views.patients),
    path("doctors", views.doctors),
    path("profile/<int:id>", views.patient_profile),
    path("doctor/<int:id>", views.doctor_profile),
    path("my-visits", views.my_visits),
    path("delete/visit/<int:id>", views.delete_visit),
    path("new-visit", views.new_visit),
    path("new-visit/<int:id>", views.select_time),
    path("my-profile", views.my_profile),
    path("chat-list", views.chat_list),
    path("create-chat/<int:id>", views.create_chat),
    path("chat/<int:id>", views.chat),
]
