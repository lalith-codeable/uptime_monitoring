import os
import json
import time
import psycopg2
from kafka import KafkaProducer
from datetime import timezone, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from psycopg2 import pool

# Kafka setup
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "website_uptime_topic")

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# PostgreSQL connection pooling setup
DATABASE_URL = os.environ.get("DATABASE_URL")
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def push_to_kafka(website_data):
    try:
        producer.send(KAFKA_TOPIC, website_data)
        producer.flush()
        print(f"Pushed data for {website_data['url']} at {website_data['timestamp']}")
    except Exception as e:
        print(f"Error pushing data to Kafka: {e}")

def get_websites():
    # Get a fresh connection from the connection pool
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    # Log to confirm the query is being executed correctly
    print("Querying database for websites...")

    cursor.execute("""
        SELECT CAST(w.id AS TEXT), w.url, w.name,
               ARRAY(SELECT wh.url
                     FROM http_server_webhook wh
                     JOIN http_server_website_associated_webhooks ww
                     ON ww.webhook_id = wh.id
                     WHERE ww.website_id = w.id) AS webhooks
        FROM http_server_website w
    """)
    websites = cursor.fetchall()

    # Log the results for debugging
    print(f"Retrieved {len(websites)} websites.")

    cursor.close()
    # Release the connection back to the pool
    connection_pool.putconn(connection)
    return websites

def collect_and_push_data():
    websites = get_websites()
    current_time = datetime.now(timezone.utc)
    
    # Collect website data and push to Kafka in a single batch
    for website in websites:
        website_data = {
            "id": str(website[0]),
            "url": website[1],
            "name": website[2],
            "webhooks": website[3],  
            "timestamp": current_time.isoformat(),
        }
        push_to_kafka(website_data)

def schedule_checks():
    scheduler = BackgroundScheduler()
    scheduler.start()

    collect_and_push_data()
    # Schedule the batch push every 1 minute
    scheduler.add_job(collect_and_push_data, trigger='interval', minutes=1, id='collect_and_push_data')

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shutdown successfully.")

if __name__ == "__main__":
    print("Starting Kafka producer with batch push every 1 minute for website checks...")
    schedule_checks()
