from django.urls import path

from . import views


urlpatterns = [
    path('', views.PermitApplicationListView.as_view(), name='list_applications'),
    path('<int:pk>/', views.PermitApplicationUpdateView.as_view(),
         name='update_application'),
    path('create/', views.PermitApplicationCreateView.as_view(),
         name='create_application')
]
