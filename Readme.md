# Uptime Monitoring Service with Discord Notifications

## Overview

This project is a scalable uptime monitoring service that periodically checks website availability and sends notifications via Discord webhooks when a site goes down or recovers. It is built using Django for the REST API, with Kafka-based producers and consumers handling background tasks.

## Features

### Website Monitoring

- Add and remove websites from monitoring.
- Store website check intervals (default: 5 minutes).
- Perform HTTP requests to check website status.
- Track uptime and downtime history.

### Discord Integration

- Configure Discord webhook URL(s).
- Send notifications when:
  - A website becomes unreachable.
  - A website recovers.
  - The first failed attempt after a success.
  - The first success after a failure.

### Architecture

- **Django Backend**: Provides RESTful endpoints.
- **Kafka Producer**: Pushes websites to the Kafka queue at fixed intervals.
- **Kafka Consumers**: Process messages, check website status, and send Discord notifications.
- **Dockerized Setup**: Optimized multi-stage builds for efficiency.
- **Database**: Stores website details, status history, and configurations.

## API Endpoints

### Site Management

- `POST /sites` - Add a new website to monitor.
- `DELETE /sites/{id}` - Remove a website from monitoring.
- `GET /sites` - List all monitored websites.
- `GET /sites/{id}/history` - Get status history of a website.

### Webhook Configuration

- `POST /webhook` - Configure Discord webhook URL.

## Deployment

### Prerequisites

- Docker & Docker Compose
- Kafka & Zookeeper (Handled within Docker Compose)
- Python 3.10+

### Setup & Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/lalith-codeable/uptime_monitoring.git
   cd uptime-monitoring
   ```
2. Create a .env file in the root of the project
    ```sh
    #reference example.env
    touch .env 
    ```
3. Run Migration for database:
    ```sh
    cd backend; python manage.py makemigrations; python manage.py migrate
    ```
4. Build and start the services:
   ```sh
   docker-compose up --build 
   or 
   docker-compose up --build -d 
   ```
4. The API will be available at `http://localhost:8000`.

## Sample JSON Payloads

### Adding a Website

```json
{
    "url": "https://example.com",
    "name": "My Website",
    "expected_status_code": 200
}
```

### Status Check Response

```json
{
    "url": "https://example.com",
    "status": "up",
    "response_time_ms": 123,
    "last_checked": "2024-01-16T20:00:00Z",
    "last_status_change": "2024-01-16T19:00:00Z"
}
```

## Notification Format

**Website Down Alert**

```
  🔴 Website Down Alert
Site: My Website (https://example.com)
Status: DOWN
Time: 2024-01-16 20:00:00 UTC
```

**Website Recovery Alert**

```
🟢 Website Recovery Alert
Site: My Website (https://example.com)
Status: UP
Time: 2024-01-16 20:05:00 UTC
```

## Testing

- Unit tests for core monitoring logic.
- Mock tests for Discord notifications.
- Run tests with:
  ```sh
  docker-compose exec backend pytest
  or 
  cd backend; pytest
  ```

## Design Decisions

- **Kafka Queue**: Used for decoupling monitoring logic from request handling.
- **Docker Multi-Stage Builds**: Optimized for performance and reduced image size.
- **Two Kafka Consumers**: Improves fault tolerance and parallel processing.
- **Multi webhook**: Support for multiple Discord webhooks.


