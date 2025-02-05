from django.urls import path
from .views import WebsiteAPI, RemoveWebsiteAPI, WebsiteHistoryAPI, WebhookAPI

urlpatterns = [
    path('sites/', WebsiteAPI.as_view(), name='sites-add-list'),
    path('sites/<uuid:pk>/', RemoveWebsiteAPI.as_view(), name='site-delete'),
    path('sites/<uuid:pk>/history/', WebsiteHistoryAPI.as_view(), name='site-history'),
    path('webhooks/', WebhookAPI.as_view(), name='webhook-management'),
]
