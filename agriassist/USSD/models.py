""" ussd models"""

import random
import string
from django.db import models
from .constants import TIME_SLOTS, STATUS_CHOICES, PENDING


class UssdUser(models.Model):
    """ 
    Model to store user information
    """
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class UssdSession(models.Model):
    """ 
    Model to store user session information
    """
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(UssdUser, on_delete=models.CASCADE)
    service_code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
class UssdSessionState(models.Model):
    """
    Tracks user's position in USSD menu flow
    """
    session = models.OneToOneField(UssdSession, on_delete=models.CASCADE, related_name='state')
    current_menu = models.CharField(max_length=50, default='main_menu')
    menu_history = models.JSONField(default=list)  # Stack of previous menus
    temp_data = models.JSONField(default=dict)  # Store partial booking data
    
class UssdBooking(models.Model):
    """ 
    Model to store booking information
    """
    user = models.ForeignKey(UssdUser, on_delete=models.CASCADE, related_name='bookings')
    reference_number = models.CharField(max_length=10, unique=True, editable=False)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=TIME_SLOTS)
    party_size = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    special_requests = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = 'BK' + ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

class MenuCategory(models.Model):
    """
    Menu categories like Breakfast, Appetizers, etc.
    """
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

class MenuItem(models.Model):
    """
    Individual menu items
    """
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
