from django.urls import path
from .views import ussd_callback

app_name = 'ussd'

urlpatterns = [
    path('callback/', ussd_callback),
]
