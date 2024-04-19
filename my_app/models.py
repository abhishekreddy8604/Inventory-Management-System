import datetime
from django.db import models

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

import random

def generate_random_user_id():
    return random.randint(100, 999)  # Generates a random 3-digit number

class userModel(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_id = models.PositiveIntegerField(primary_key=True, unique=True, default=generate_random_user_id)

    class Meta:
        db_table = "manager_user"



class ProductModel(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='product_images')
    created_at = models.DateTimeField(auto_now_add=True)
    manager = models.ForeignKey(userModel, on_delete=models.CASCADE, related_name='products_managed')
    modified_by = models.ForeignKey(userModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='products_modified')
    modified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "products"

    def save(self, *args, **kwargs):
        self.modified_at = datetime.datetime.now() 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    def create_audit_entry(self):
        latest_audit = self.audits.order_by('-version').first()
        version = latest_audit.version + 1 if latest_audit else 0

        ProductAudit.objects.create(
            product=self,
            version=version,
            product_name=self.product_name,
            quantity=self.quantity,
            price=self.price,
            modified_by=self.modified_by,
        )

class ProductAudit(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='audits')
    version = models.PositiveIntegerField()
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(userModel, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "product_audit"








