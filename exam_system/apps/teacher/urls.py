from django.urls import path
from apps.teacher import views


urlpatterns = [
    path("classes/", views.TeacherClassesView.as_view())
]