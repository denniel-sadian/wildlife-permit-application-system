from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """Vewset for user notifications."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.none()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        notifications = (
            Notification
            .objects
            .filter(user__id=self.request.user.id)
            .order_by('-created_at'))
        return notifications
