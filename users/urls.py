from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('auth/password_change/', views.CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('auth/', include('django.contrib.auth.urls')),
    path('registration/', views.ClientRegistrationView.as_view(),
         name='registration')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
