from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.user_logout, name="logout"),
    path("hydration/", views.hydration, name="hydration"),
    path("sleep/", views.sleep, name="sleep"),
    path("fitness/", views.fitness, name="fitness"),
    path("study/", views.study, name="study"),
   
   path(
    "hydration/delete/<int:id>/",
    views.delete_hydration,
    name="delete_hydration"
),

path(
    "hydration/edit/<int:id>/",
    views.edit_hydration,
    name="edit_hydration"
),

   path(
    "profile/",
    views.profile,
    name="profile"
),

path(
    "sleep/edit/<int:id>/",
    views.edit_sleep,
    name="edit_sleep"
),
path(
    "sleep/delete/<int:id>/",
    views.delete_sleep,
    name="delete_sleep"
),

path(
    "fitness/edit/<int:id>/",
    views.edit_fitness,
    name="edit_fitness"
),

path(
    "fitness/delete/<int:id>/",
    views.delete_fitness,
    name="delete_fitness"
),

path(
    "study/edit/<int:id>/",
    views.edit_study,
    name="edit_study"
),

path(
    "study/delete/<int:id>/",
    views.delete_study,
    name="delete_study"
),

path("reflection/", views.reflection, name="reflection"),
path(
    "previous-reflections/",
    views.previous_reflections,
    name="previous_reflections"
),

path(
    "reflection/<int:reflection_id>/edit/",
    views.edit_reflection,
    name="edit_reflection"
),

path(
    "reflection/<int:reflection_id>/delete/",
    views.delete_reflection,
    name="delete_reflection"
),

]