from django.urls import path

from . import views


urlpatterns = [
    path('payments/pay_via_gcash_redirect/<int:pk>/', views.PayViaGcashRedirectView.as_view(),
         name='pay_via_gcash_redirect'),
    path('payments/authorization_complete/<int:pk>/', views.AuthorizationCompleteDetailView.as_view(),
         name='authorization_complete'),
    path('payments/webhook/', views.webhook, name='webhook')
]
