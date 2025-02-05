import os
import uuid
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Website, StatusLog, Webhook
from .serializers import WebsiteSerializer, StatusLogSerializer, WebhookSerializer

class WebsiteAPI(APIView):
    def get(self, request):
        try:
            websites = Website.objects.all()
            serializer = WebsiteSerializer(websites, many=True)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        webhook_urls = request.data.pop('webhooks', [])  
        serializer = WebsiteSerializer(data=request.data)

        if serializer.is_valid():
            website = serializer.save()

            if webhook_urls:
                for url in webhook_urls:
                    webhook, created = Webhook.objects.get_or_create(url=url)
                    website.associated_webhooks.add(webhook)
            else:
                default_webhook = os.getenv("DISCORD_WEBHOOK_URL")
                if default_webhook:
                    webhook, _ = Webhook.objects.get_or_create(url=default_webhook)
                    website.associated_webhooks.add(webhook)

            return Response({ "success": True, "data": WebsiteSerializer(website).data}, status=status.HTTP_201_CREATED)

        return Response({ "success": False, "error": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

class RemoveWebsiteAPI(APIView):
    def delete(self, request, pk):
        try:
            website = Website.objects.get(pk=uuid.UUID(str(pk)))
        except Website.DoesNotExist:
            return Response({"success": False, "error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        website.delete()
        return Response({"success": True, "data": f"Website {pk} has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


class WebsiteHistoryAPI(APIView):
    def get(self, request, pk):
        try:
            website = Website.objects.get(pk=uuid.UUID(str(pk)))
        except (Website.DoesNotExist, ValueError):
            return Response({"success": False, "error": "Website not found"}, status=status.HTTP_404_NOT_FOUND)

        status_logs = StatusLog.objects.filter(website=website)
        serializer = StatusLogSerializer(status_logs, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class WebhookAPI(APIView):
    def get(self, request):
        try:
            webhooks = Webhook.objects.all()
            serializer = WebhookSerializer(webhooks, many=True)
            return Response({ "success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ "success": False, "error": "An unexpected error occurred" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        webhook_url = request.data.get("webhook_url")
        if not webhook_url:
            return Response({ "success": False, "error": "No webhook URL provided"}, status=status.HTTP_400_BAD_REQUEST)

        webhook, created = Webhook.objects.get_or_create(url=webhook_url)

        for website in Website.objects.all():
            website.associated_webhooks.add(webhook)

        return Response({ "success": True, "data": "Webhook added and associated with all websites"}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        webhook_url = request.data.get("webhook_url")
        if not webhook_url:
            return Response({ "success": False, "error": "No webhook URL provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            webhook = Webhook.objects.get(url=webhook_url)
            for website in Website.objects.all():
                website.associated_webhooks.remove(webhook)
            webhook.delete()
            return Response({"success": True, "data": "Webhook removed from all websites"}, status=status.HTTP_204_NO_CONTENT)
        except Webhook.DoesNotExist:
            return Response({"success": False, "error": "Webhook not found"}, status=status.HTTP_404_NOT_FOUND)

