from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/current_medication/', views.currentMedication),
]

urlpatterns = format_suffix_patterns(urlpatterns)