from django.urls import path, include

from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('registration/', views.ClientRegistrationView.as_view(),
         name='client-registration')
]
