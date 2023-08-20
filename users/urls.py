from django.urls import path

from . import views


urlpatterns = [
    path('clients/', views.ClientRegistrationView.as_view(), name='client-registration')
]
