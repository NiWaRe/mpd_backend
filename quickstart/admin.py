from django.contrib import admin

# Register your models here.
from .models import (
    Product,
    Doctors, 
    Patients, 
    Inventory, 
    PrescriptionTypes, 
    Prescriptions, 
    UserOwnsMedication, 
)

admin.site.register(
    Product, 
    Doctors, 
    Patients, 
    Inventory, 
    PrescriptionTypes, 
    Prescriptions, 
    UserOwnsMedication, 
)