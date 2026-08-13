from django.urls import path
from . import views

urlpatterns = [
    path('', views.parsons_home, name='parsons_home'),
    path('savelog/', views.save_user_log, name='savelog'),
    path('<int:problem_id>/', views.show_problem, name='show_problem'),
]
