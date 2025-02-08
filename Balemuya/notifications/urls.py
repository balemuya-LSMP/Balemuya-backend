from django.urls import path
from .views import NotificationListView,MarkNotificationAsReadView,MarkAllNotificationAsReadView


urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),
    path('<uuid:pk>/read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),
    path('read/', MarkAllNotificationAsReadView.as_view(), name='notification-mark-read'),

]