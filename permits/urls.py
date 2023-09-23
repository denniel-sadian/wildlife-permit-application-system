from django.urls import path

from . import views


urlpatterns = [
    # Permit Applications
    path('applications/', views.PermitApplicationListView.as_view(),
         name='list_applications'),
    path('applications/<int:pk>/', views.PermitApplicationUpdateView.as_view(),
         name='update_application'),
    path('applications/<int:pk>/delete/', views.PermitApplicationDeleteView.as_view(),
         name='delete_application'),
    path('applications/create/', views.PermitApplicationCreateView.as_view(),
         name='create_application')
]
