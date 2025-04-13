import threading
import json
import asyncio
import logging
from fastapi import FastAPI, WebSocket, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from utils.utils import utility_service
from services.processmessage import process_message as process_message_service
# from services.translation import translation_service  # ensure this runs as needed
# from services.language_detection import language_detection  # ensure this runs as needed


import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app : FastAPI):
    await utility_service.start_background_tasks()
    yield
    utility_service.close_background_tasks()
    

app = FastAPI(title="Real-Time Translation Network",lifespan=lifespan)

# Configure CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Real-Time Translation Network API"}

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection established for room: {room_id}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data} in room: {room_id}")
            message = json.loads(data)
            # Process the message (kick off the pipeline)
            process_message_service.process(message)
            print("After ")
            
            # Polling mechanism to get the response
            # response_string = process_message_service.redis_client.get(process_message_service.mesage_id)
            pubsub = process_message_service.redis_client.pubsub()
            pubsub.subscribe('translation_channel')
            logger.info("Subscribed to 'translation_channel'")
            for message in pubsub.listen():
                if message['type'] == 'message':
                    request_id = json.loads(message['data'])["id"]
                    logger.info(f"Received published message for request ID: {request_id}")
                    response_string = process_message_service.redis_client.get(request_id)
                    if response_string:
                        response = json.loads(response_string)
                        await websocket.send_text(json.dumps(response))
                        logger.info(f"Sent response: {response} to room: {room_id}")
            # logger.info("Polling for response: '{response_string}'".format(response_string))
            # if response_string:
            #     response = json.loads(response_string)
            #     await websocket.send_text(json.dumps(response))
            #     logger.info(f"Sent response: {response} to room: {room_id}")
            # else:
            #     logger.warning(f"No response found for message ID: {message['id']}")

    except Exception as e:
        logger.error(f"Error in websocket: {e}")
        if not websocket.client_state.name == "DISCONNECTED":
            try:
                await websocket.close()
            except RuntimeError as close_err:
                logger.warning(f"WebSocket already closed: {close_err}")

    finally:
        logger.info(f"WebSocket connection closed for room: {room_id}")





if __name__ == "__main__":

    logger.info("Starting FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)