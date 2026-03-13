from django.urls import path
from apps.question import views


urlpatterns = [
    path("list/", views.QuestionListView.as_view()),

    path("add/", views.QuestionAddView.as_view()),
    path("batch/", views.QuestionDeleteListView.as_view()),
    path("<int:id>/", views.QuestionInfoView.as_view()),
    
    # 导入导出题目
    path("import/", views.QuestionImportView.as_view()),
    path("export/", views.QuestionExportView.as_view()),
]