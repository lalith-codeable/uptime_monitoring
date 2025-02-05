import os
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from http_server.models import Website, Webhook

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def website(db):  # Ensure database access is allowed
    return Website.objects.create(
        url="https://ctqhttp.lalith.xyz.com/",
        name="Ctq testnet",
        expected_status_code=304
    )

@pytest.fixture
def webhook(db):
    return Webhook.objects.create(url=DISCORD_WEBHOOK_URL)

@pytest.mark.django_db
def test_get_websites(api_client, website):
    url = reverse('sites-add-list')  # Use updated name from `urlpatterns`
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data["data"]) > 0

@pytest.mark.django_db
def test_add_website_with_webhook(api_client):
    url = reverse('sites-add-list')  # Updated URL name
    data = {
        "url": "https://spacex.com",
        "name": "spacex",
        "expected_status_code": 200
    }
    
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == 201
    assert response.data["success"] is True
    assert response.data["data"]["url"] == "https://spacex.com"

@pytest.mark.django_db
def test_add_website_with_env_webhook(api_client):
    url = reverse('sites-add-list')  # Updated URL name
    data = {
        "url": "https://guthib.com",
        "name": "You spelled it wrong",
        "expected_status_code": 200
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == 201
    assert response.data["success"] is True
    assert response.data["data"]["url"] == "https://guthib.com"

@pytest.mark.django_db
def test_delete_website(api_client, website):
    url = reverse('site-delete', args=[website.id])  # Updated URL name
    
    response = api_client.delete(url)

    assert response.status_code == 204

@pytest.mark.django_db
def test_get_website_history(api_client, website):
    url = reverse('site-history', args=[website.id])  # Updated URL name

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["success"] is True

@pytest.mark.django_db
def test_add_webhook(api_client):
    url = reverse('webhook-management')  # Updated URL name
    data = {"webhook_url": "https://discord.com/api/webhooks/99999/new_webhook"}

    response = api_client.post(url, data, format='json')

    assert response.status_code in [200, 201]
    assert response.data["success"] is True
    assert Webhook.objects.filter(url="https://discord.com/api/webhooks/99999/new_webhook").exists()

@pytest.mark.django_db
def test_remove_webhook(api_client, webhook):
    url = reverse('webhook-management')  # Updated URL name

    response = api_client.delete(url, {"webhook_url": webhook.url}, format='json')

    assert response.status_code == 204
    assert not Webhook.objects.filter(url=webhook.url).exists()
