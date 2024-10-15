from django.db import models

# Create your models here.
class Company(models.Model):
    # public traded company 
    name = models.CharField(max_length=120)
    ticker = models.CharField(max_length=10, unique=True, db_index=True)
 