from django.urls import path
from apps.mistake import views

urlpatterns = [
    path("list-with-statistics/", views.MistakeListWithStatisticsView.as_view()),
    path("<int:mistake_id>/mastered/", views.MistakeMasteredView.as_view()),
    path("export/", views.MistakeExportView.as_view()),
]

