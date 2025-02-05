import os
import json
import psycopg2
import uuid
from kafka import KafkaConsumer
import requests
from psycopg2 import pool
from datetime import timezone, datetime

# Kafka setup
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "website_uptime_topic")
KAFKA_CONSUMER_GROUP = os.environ.get("KAFKA_CONSUMER_GROUP", "website_uptime_group")

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    group_id=KAFKA_CONSUMER_GROUP,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)

# PostgreSQL connection pooling setup
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://username:password@localhost:5432/mydatabase")
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def get_last_status(website_id):
    """Retrieve the last recorded status and timestamp for the website"""
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT status, last_status_change FROM http_server_statuslog
        WHERE website_id = %s
        ORDER BY checked_at DESC LIMIT 1
        """,
        (website_id,),
    )
    last_record = cursor.fetchone()
    cursor.close()
    connection_pool.putconn(conn)

    # Debugging: Print retrieved data
    print(f"DEBUG: Last record for {website_id}: {last_record}")

    return last_record if last_record else (None, None)  # Return status and timestamp

def save_status_log(website_id, status, response_time, last_status, last_status_change):
    """Save the status log for the website"""
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    new_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # If the status has changed, update last_status_change timestamp
    if last_status is None or last_status != status:
        last_status_change = now

    cursor.execute(
        """
        INSERT INTO http_server_statuslog (id, website_id, status, response_time, checked_at, last_status_change)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (new_id, website_id, status, response_time, now, last_status_change),
    )
    conn.commit()
    cursor.close()
    connection_pool.putconn(conn)

def send_discord_notification(webhooks, website_url, status):
    """Send a notification to the Discord webhooks"""
    message = "🟢 Website is UP!" if status == "up" else "🔴 Website is DOWN!"
    data = {"content": f"{message}\nSite: {website_url}"}
    print(f"DEBUG: Sending notification: {data}")
    for webhook in webhooks:
        try:
            response = requests.post(webhook, json=data)
            if response.status_code != 204:
                print(f"WARNING: Failed to send notification to {webhook}, status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"ERROR: Failed to send notification to {webhook}: {e}")

def process_message(message):
    """Process the website status check from the Kafka message"""
    website_id = message.get("id")
    url = message.get("url")
    expected_status_code = message.get("expected_status_code", 200)  # Default to 200 if not specified
    webhooks = message.get("webhooks", [])

    try:
        response = requests.get(url, timeout=10)
        status = "up" if response.status_code == expected_status_code else "down"
        response_time = response.elapsed.total_seconds()
    except requests.RequestException as e:
        status = "down"
        response_time = None
        print(f"ERROR: Failed to check website {url}: {e}")

    # Get the last recorded status and its timestamp
    last_status, last_status_change = get_last_status(website_id)

    # Debugging: Check current and last status before saving
    print(f"DEBUG: Last status: {last_status}, Current status: {status}")

    # Save status log with correct last_status_change handling
    save_status_log(website_id, status, response_time, last_status, last_status_change)

    # Send notification if it's the first check or the status has changed
    if last_status is None or last_status != status:
        print(f"DEBUG: Sending notification for {url} (status change detected)")
        if webhooks:
            send_discord_notification(webhooks, url, status)

    print(f"Processed: {url} - Status: {status}")

def start_consumer():
    """Start the Kafka consumer to listen for new messages"""
    print("Starting Kafka consumer...")
    for message in consumer:
        process_message(message.value)

if __name__ == "__main__":
    start_consumer()
