from django.urls import path

from . import views

urlpatterns = [
    path('', views.parsons_faded_home, name='parsons_faded_home'),
    path('<int:problem_id>/', views.parsons_faded_problem,
         name='parsons_faded_problem'),
]
