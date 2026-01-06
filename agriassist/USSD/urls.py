from django.urls import path
from .views import USSDCallbackView

app_name = 'ussd'

urlpatterns = [
    path('callback/', USSDCallbackView.as_view(), name='ussd-callback'),
]
