from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('auth/login/', views.CustomLoginView.as_view(), name='login'),
    path('auth/password_change/', views.CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('auth/', include('django.contrib.auth.urls')),
    path('registration/', views.ClientRegistrationView.as_view(),
         name='registration'),
    path('profile/', views.ProfileView.as_view(),
         name='profile')
]
