from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/current_medication/', views.currentMedication),
    path('api/new_prescriptions/', views.newPrescriptions),
    path('api/redeem_prescription/', views.redeemPrescription),
    path('api/reorder_prescription/', views.reorderPrescription),
    path('api/answer_request/<int:prescription_id>/<str:status_str>/<str:recipient>', views.answerRequest),
    path('api/responsible_doctors/', views.responsibleDoctors),
]

urlpatterns = format_suffix_patterns(urlpatterns)