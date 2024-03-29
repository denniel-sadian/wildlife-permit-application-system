"""biodiversity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers

from ajax_select import urls as ajax_select_urls

from users import api_views as users_api_views

TITLE = 'Biodiversity Administration'
admin.site.site_header = TITLE
admin.site.site_title = TITLE
admin.site.index_title = TITLE

admin.autodiscover()

router = routers.DefaultRouter()
router.register('notifications', users_api_views.NotificationViewSet)

urlpatterns = [
    path('', include('users.urls')),
    path('', include('animals.urls')),
    path('', include('payments.urls')),
    path('', include('permits.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('ajax_select/', include(ajax_select_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
