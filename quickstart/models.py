from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=300)
    prescription = models.BooleanField()

    # class Meta:
    #     app_label = 'quickstart'