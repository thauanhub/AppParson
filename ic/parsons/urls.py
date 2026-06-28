from django.urls import path
from . import views

urlpatterns = [
    path('<int:problem_id>/', views.show_problem, name='show_problem'),
]