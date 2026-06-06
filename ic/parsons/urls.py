from django.urls import path
from . import views

urlpatterns = [
    path('problema/<int:problem_id>/', views.resolver_parsons, name='resolver_parsons'),
]