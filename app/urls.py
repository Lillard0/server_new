import app.views

from django.urls import path

urlpatterns = [
    path('<str:module>/', app.views.SysView.as_view()),
    path('colleges/<str:module>/', app.views.CollegesView.as_view()),
    path('grades/<str:module>/', app.views.GradesView.as_view()),
    path('projects/<str:module>/', app.views.ProjectsView.as_view()),
    path('students/<str:module>/', app.views.StudentsView.as_view()),
    path('teachers/<str:module>/', app.views.TeachersView.as_view()),
    path('practises/<str:module>/', app.views.PractisesView.as_view()),
    path('options/<str:module>/', app.views.OptionsView.as_view()),
    path('exams/<str:module>/', app.views.ExamsView.as_view()),
    path('examlogs/<str:module>/', app.views.ExamLogsView.as_view()),
    path('answerlogs/<str:module>/', app.views.AnswerLogsView.as_view()),
]