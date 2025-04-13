import logging
# from transformers import pipeline
import requests
from core.config import settings
import pika
import json
from threading import Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.stop_event = Event()
        self.models = {}
        self.request = {}
        self.setup_rabbitmq()
        logger.info("TranslationService initialized.")
    
    def setup_rabbitmq(self):
        """Setup RabbitMQ connection and channel"""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.RABBITMQ_URL)
            )
            # Create Connection to Translation Queue
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.TRANSLATION_QUEUE)
            logger.info("RabbitMQ connection and channel setup completed.")
        except Exception as e:
            logger.error(f"Error setting up RabbitMQ: {e}")
            raise

    def get_model(self, source_lang: str = settings.DEFAULT_SOURCE_LANG, target_lang: str = settings.DEFAULT_TARGET_LANG):
        """Get or create translation model for language pair"""
        model_key = f"{source_lang}-{target_lang}"
        logger.info(f"Fetching model for language pair: {model_key}")
        if model_key not in self.models:
            model_name = settings.HUGGINGFACE_MODEL_URL.format(
                src=source_lang,
                tgt=target_lang
            )
            logger.info(f"Model not found in cache. Loading model for {model_key}: {model_name}")
            self.models[model_key] = model_name
            logger.info("After setting model key-value")
        else:
            logger.info(f"Model for {model_key} found in cache.")
        return self.models[model_key]
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang:
            logger.info("Source and target languages are the same. Returning original text.")
            return text
            
        logger.info(f"Translating text from {source_lang} to {target_lang}.")
        model_url = self.get_model(source_lang, target_lang)
        response = requests.post(
            model_url,
            headers={"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"},
            json={"inputs": text}
        )
        response_json = response.json()  # Properly parse the response
        translation = response_json[0].get('translation_text', '')
        logger.info(f"Translation completed: {translation}")
        return translation

    
    def publish_translation(self):
        """Queue translation request in RabbitMQ"""
        message = {
            "id": self.request.get('id'),
            "text": self.request.get('text'),
            "translation_text": self.request.get('translation_text'),
            "source_lang": self.request.get('source_lang'),
            "target_lang": self.request.get('target_lang'),
        }
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.TRANSLATION_QUEUE,
                body=json.dumps(message)
            )
            logger.info("Translation request published to RabbitMQ.")
        except Exception as e:
            logger.error(f"Error publishing translation request: {e}")
            raise

    def produce(self):
        try:
            logger.info("Producing translation request.")
            self.request['translation_text'] = self.translate(**self.request)
            self.publish_translation()
        except Exception as e:
            logger.error(f"Error in produce method: {e}")

    def consume(self):
        while not self.stop_event.is_set():
            try:
                def callback(ch, method, properties, body):
                    logger.info(f"Received message from RabbitMQ: {body}")
                    try:
                        message = json.loads(body.decode())
                        logger.info(f"Processing message: {message}")
                        text = message.get('text')
                        source_lang = message.get('source_lang')
                        target_lang = message.get('target_lang')
                        translated_text = self.translate(text=text, source_lang=source_lang, target_lang=target_lang)
                        message['translation_text'] = translated_text
                        logger.info(f"Translation result: {translated_text}")
                        self.channel.basic_publish(
                            exchange='',
                            routing_key=settings.TRANSLATION_QUEUE,
                            body=json.dumps(message)
                        )
                        logger.info("Updated message published with translation.")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                    finally:
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                logger.info("Starting to consume messages from RabbitMQ...")
                self.channel.basic_consume(queue=settings.DETECTION_QUEUE, on_message_callback=callback)
                while not self.stop_event.is_set():
                    self.connection.process_data_events(time_limit=1)
            except Exception as e:
                logger.error(f"Error in consume method: {e}")
            finally:
                self.close()

    def close(self):
        """Close RabbitMQ connection"""
        try:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")

# Create global instance
translation_service = TranslationService()
