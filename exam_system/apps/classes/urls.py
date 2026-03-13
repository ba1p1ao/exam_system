from django.urls import path
from apps.classes import views


urlpatterns = [
    path("options/", views.ClassOptionView.as_view()),
    path("list/", views.ClassListView.as_view()),
    path("create/", views.ClassCreateView.as_view()),
    path("<int:class_id>/", views.ClassView.as_view()),
    path("<int:class_id>/status/", views.ClassStatusView.as_view()),
    path("<int:class_id>/statistics/", views.ClassStatisticsView.as_view()),
    path("<int:class_id>/members/", views.ClassMembersView.as_view()),
    path("<int:class_id>/members/add/", views.ClassMembersAddView.as_view()),
    path("<int:class_id>/members/remove/", views.ClassMembersRemoveView.as_view()),
    path("<int:class_id>/available-students/", views.ClassAvailableStudentsView.as_view()),

    # 班级成绩排名
    path("<int:class_id>/exam-ranking/", views.ClassExamRankingView.as_view()),
    path("<int:class_id>/score-trend/", views.ClassScoreTrendView.as_view()),
]