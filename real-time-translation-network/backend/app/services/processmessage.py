import logging
from threading import Event
import time
import json
import redis
import pika
from typing import Dict
import asyncio
from core.config import settings
from services.language_detection import language_detection
from services.translation import translation_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessMessageService:
    def __init__(self) -> None:
        self.mesage_id = None
        self.stop_event = Event()
        self.request = {}
        logger.info("Initializing ProcessMessageService")
        self.setup_rabbitmq()
        self.setup_redis()
    
    def setup_rabbitmq(self):
        """Setup RabbitMQ connection and channel."""
        try:
            logger.info("Setting up RabbitMQ connection")
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.RABBITMQ_URL)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.TRANSLATION_QUEUE)
            logger.info("RabbitMQ setup completed")
        except Exception as e:
            logger.error(f"Failed to setup RabbitMQ: {e}")
            raise

    def setup_redis(self):
        """Setup Redis connection."""
        try:
            logger.info("Setting up Redis connection")
            # pool = redis.ConnectionPool().from_url(settings.REDIS_URL)
            self.redis_client = redis.Redis().from_url(settings.REDIS_URL)
            # self.redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
            self.redis_client.ping()
            logger.info("Redis setup completed")
        except Exception as e:
            logger.error(f"Failed to setup Redis: {e}")
            raise
    
    def process(self, request: Dict):
        """
        Perform the message processing.
        Here the language_detection service is called, which (in your flow) eventually triggers translation.
        """
        logger.info("Starting message processing")
        try:
            # Assign a unique ID based on the current time (or use another unique method)
            self.mesage_id = round(time.time())
            request['id'] = self.mesage_id
            # Kick off language detection (which triggers the further pipeline)
            language_detection.process(request)
        except Exception as e:
            logger.error(f"Error during message processing: {e}")
            raise

    def store(self, request: Dict) -> str:
        """
        Store the translation request in Redis and publish a notification for subscribers.
        :param request: The translation request to store
        :return: The request ID
        """
        try:
            logger.info("Storing translation request in Redis")

            # Validate request ID
            request_id = request.get('id')
            if not request_id:
                logger.error("Request ID is missing or invalid.")
                raise ValueError("Request ID is required to store the translation request.")

            # Serialize the request
            try:
                serialized_request = json.dumps(request)
            except TypeError as e:
                logger.error(f"Error serializing request: {e}")
                raise ValueError("Request contains non-serializable data.")

            # Ensure Redis connection is healthy
            try:
                self.redis_client.ping()
            except redis.ConnectionError as e:
                logger.error(f"Redis connection error: {e}")
                raise ConnectionError("Failed to connect to Redis.")

            # Store the request in Redis
            self.redis_client.set(request_id, serialized_request)
            self.redis_client.publish('translation_channel', serialized_request)
            logger.info(f"Stored request with ID: {request_id} and data: {serialized_request}")

            return request_id
        except Exception as e:
            logger.error(f"Error storing request in Redis: {e}")
            raise

    def consume(self):
        """
        Consume messages from the RabbitMQ translation queue.
        When a message is received from translation, it is stored in Redis.
        """
        while not self.stop_event.is_set():
            try:
                def callback(ch, method, properties, body):
                    logger.info(f"Received message from translation queue: {body}")
                    try:
                        # Assuming the body is a JSON-encoded string
                        request_data = json.loads(body.decode())
                    except Exception as e:
                        logger.error(f"Error decoding message: {e}")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                    
                    # Store the final processed request in Redis and publish a notification.
                    self.store(request_data)
                    logger.info("Message processing and storage completed")
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                try:
                    logger.info("Starting ProcessMessage Consumer...")
                    # Note: Using auto_ack=False to ensure messages are acknowledged after processing.
                    self.channel.basic_consume(queue=settings.TRANSLATION_QUEUE, on_message_callback=callback, auto_ack=False)
                    logger.info("Waiting for messages...")
                    while not self.stop_event.is_set():
                        self.connection.process_data_events(time_limit=1)
                except Exception as e:
                    logger.error(f"Error during message consumption: {e}")
                    raise
            except Exception as e:
                logger.error(f"ProcessMessage consumer error: {e}")
        self.close()

    # def subscribe(self):
    #     """
    #     Subscribe to the Redis Pub/Sub channel ('translation_channel') to receive notifications in real time.
    #     This can be run in a separate thread or integrated into your asynchronous workflow.
    #     """

    #             # Optionally, fetch the stored data from Redis.
    #             # data = self.redis_client.get(request_id)
    #             # if data:
    #             #     logger.info(f"Retrieved data for {request_id}: {data.decode()}")
    #             # else:
    #             #     logger.warning(f"No data found for request ID: {request_id}")

    def close(self):
        """Close RabbitMQ connection"""
        logger.info("Closing RabbitMQ connection...")
        try:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
            raise

# Initialize an instance of your process message service.
process_message = ProcessMessageService()
