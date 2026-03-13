from django.urls import path
from apps.user import views


urlpatterns = [
    path("login/", views.UserLoginView.as_view()),
    path("info/", views.UserInfoView.as_view()),
    path("register/", views.UserRegisterView.as_view()),
    path("update/", views.UserUpdateView.as_view()),
    path("password/", views.UserPasswordView.as_view()),
]