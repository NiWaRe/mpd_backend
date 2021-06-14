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

admin.site.register(Product)
admin.site.register(Doctors)
admin.site.register(Patients)
admin.site.register(Inventory)
admin.site.register(PrescriptionTypes)
admin.site.register(Prescriptions)
admin.site.register(UserOwnsMedication)