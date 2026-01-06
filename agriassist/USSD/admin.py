# """ admin """
# from django.contrib import admin
# from .models import UssdUser

# @admin.register(UssdUser)
# class UssdUserAdmin(admin.ModelAdmin):
#     """UssdUserAdmin"""
#     list_display = ['phone_number', 'first_name', 'last_name', 'total_bookings', 'created_at']
#     search_fields = ['phone_number', 'first_name', 'last_name']
#     list_filter = ['created_at']
#     readonly_fields = ['created_at', 'updated_at']
#     ordering = ['-created_at']
