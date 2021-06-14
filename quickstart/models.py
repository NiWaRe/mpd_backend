from django.db import models

# only if users from REST API Framework should be used. 
# from django.contrib.auth.models import User

# NOTE: in case some field turns out to be only sometimes necessary
# add null=True (and blank=True)
# https://books.agiliq.com/projects/django-orm-cookbook/en/latest/null_vs_blank.html

class Product(models.Model):
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=300)
    prescription = models.BooleanField()

    # class Meta:
    #     app_label = 'quickstart'

class Doctors(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    # path can be left empty (null=True not possible for textfields)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self): 
        # name in django admin / shell
        return str(self.doctor_id) + "_" + self.name

    class Meta:
        # name in db (otherwise quickstart_doctors would be the name of the db)
        db_table = 'doctors'
        # __str__ name of model (would be 'doctorss' otherwise in admin panel)
        verbose_name_plural = 'doctors'

class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    isChronic = models.BooleanField()
    condition = models.CharField(max_length=100, blank=True)
    doctor_id = models.ForeignKey(Doctors, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self): 
        return str(self.patient_id) + "_" + self.name

    class Meta:
        db_table = 'patients'
        verbose_name_plural = 'patients'

class Inventory(models.Model):
    medication_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300)
    ppDosageInMg = models.IntegerField()
    prescriptionNeeded = models.BooleanField()
    inStock = models.BooleanField()
    manufacturer = models.CharField(max_length=300)
    # path, desc can be left empty (null=True not possible for textfields)
    imagePath = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self): 
        return self.name + "_" + self.manufacturer

    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'inventory'

class PrescriptionTypes(models.Model):
    prescription_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50) 
    recurring = models.BooleanField()
    description = models.CharField(max_length=1000, blank=True) 

    def __str__(self): 
        return self.name

    class Meta:
        db_table = 'prescription_types'
        verbose_name_plural = 'prescription_types'

class Prescriptions(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    prescription_type_id = models.ForeignKey(PrescriptionTypes, null=True, on_delete=models.SET_NULL)
    doctor_id = models.ForeignKey(Doctors, null=True, on_delete=models.SET_NULL)
    redeemed = models.BooleanField()
    validUntil = models.DateTimeField()
    description = models.CharField(max_length=1000, blank=True) 

    def __str__(self): 
        return str(self.prescription_id)

    class Meta:
        db_table = 'prescriptions'
        verbose_name_plural = 'prescriptions'
    
# NOTE: Django doesn't support composite primary keys
# That's why we have to use another AutoField primary key 
# add the two keys (here the FKs) as normal columns with a 
# "unique_together" constraint
class UserOwnsMedication(models.Model):
    user_owns_medication_id = models.AutoField(primary_key=True)
    medication_id = models.ForeignKey(Inventory, null=True, on_delete=models.SET_NULL)
    patient_id = models.ForeignKey(Patients, null=True, on_delete=models.SET_NULL)
    boughtTime = models.DateTimeField()
    remainingDosageInMg = models.IntegerField()
    prescription_id = models.ForeignKey(Prescriptions, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=1000, blank=True) 

    def __str__(self): 
        return str(self.medication_id) + "_" + str(self.patient_id)

    class Meta:
        db_table = 'user_owns_medication'
        verbose_name_plural = 'prescriptions'
        unique_together = (('medication_id', 'patient_id'),)