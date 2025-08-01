from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random

class User(AbstractUser):
    is_driver = models.BooleanField(default=False)

class Ride(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('accepted','Accepted'),('completed','Completed')]
    user = models.ForeignKey(User, related_name='rides', on_delete=models.CASCADE)
    driver = models.ForeignKey(User, related_name='assigned_rides', null=True, blank=True, on_delete=models.SET_NULL)
    pickup = models.CharField(max_length=255)
    drop = models.CharField(max_length=255)
    fare = models.FloatField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # ➕ Add rating and feedback
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

class DriverLocation(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    paid = models.BooleanField(default=False)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 300


