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

]