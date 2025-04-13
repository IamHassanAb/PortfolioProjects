import logging
import threading
from services.translation import translation_service
from services.processmessage import process_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UtilityService:
    def __init__(self):
        self.translation_thread = None
        self.processmessage_thread = None
        self.redis_subscriber_thread = None

    def start_translation_consumer(self):
        try:
            logger.info("Starting translation consumer...")
            # translation_service.stop_event.set()
            translation_service.consume()
        except Exception as e:
            logger.error(f"Error in translation consumer: {e}")

    def start_processmessage_consumer(self):
        try:
            # process_message.stop_event.set()
            logger.info("Starting process message consumer...")
            process_message.consume()
        except Exception as e:
            logger.error(f"Error in process message consumer: {e}")

    def start_redis_subscriber(self):
        try:
            logger.info("Starting Redis subscriber...")
            process_message.subscribe()
        except Exception as e:
            logger.error(f"Error in Redis subscriber: {e}")

    async def start_background_tasks(self):
        self.translation_thread = threading.Thread(
            target=self.start_translation_consumer, daemon=True
        )
        self.processmessage_thread = threading.Thread(
            target=self.start_processmessage_consumer, daemon=True
        )
        # self.redis_subscriber_thread = threading.Thread(
        #     target=self.start_redis_subscriber, daemon=True
        # )

        self.translation_thread.start()
        self.processmessage_thread.start()
        # self.redis_subscriber_thread.start()

    def close_background_tasks(self):
        logger.info("Stopping background tasks...")
        translation_service.stop_event.set()  # Signal the translation consumer to stop
        self.translation_thread.join()  # Wait for the thread to finish
        logger.info("'Translation' consumer thread closed.")

        process_message.stop_event.set()  # Signal the process message consumer to stop
        self.processmessage_thread.join()  # Wait for the thread to finish
        logger.info("'Process Message' consumer thread closed.")
        



utility_service = UtilityService()