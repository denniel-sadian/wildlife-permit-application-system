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
    path('applications/<int:pk>/submit/', views.SubmitRedirectView.as_view(),
         name='submit_application'),
    path('applications/<int:pk>/unsubmit/', views.UnsubmitRedirectView.as_view(),
         name='unsubmit_application'),
    path('applications/create/', views.PermitApplicationCreateView.as_view(),
         name='create_application'),

    # Permits
    path('permits/', views.PermitListView.as_view(),
         name='permit_list'),
    path('permits/<int:pk>/', views.PermitDetailView.as_view(),
         name='permit_detail')

]
