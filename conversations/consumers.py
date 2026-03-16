# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from conversations.services.core.dialogue_engine import process_message


# class VoiceBotConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.accept()

#         await self.send(json.dumps({
#             "message": "Connected to Voice Bot"
#         }))


#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         agent_id = data.get("agent_id")
#         message = data.get("message")
#         session_id = data.get("session_id")

#         # Call your existing bot engine
#         response = process_message(
#             agent_id=agent_id,
#             message=message,
#             session_id=session_id
#         )

#         await self.send(json.dumps(response))


from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from conversations.services.core.dialogue_engine import process_message


class VoiceBotConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        await self.send(json.dumps({
            "message": "Connected to Voice Bot"
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)

        agent_id = data.get("agent_id")
        message = data.get("message")
        session_id = data.get("session_id")

        # Call your existing bot engine
        response = await sync_to_async(process_message)(
            agent_id,
            message,
            session_id
        )

        await self.send(text_data=json.dumps(response))