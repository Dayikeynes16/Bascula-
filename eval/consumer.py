# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PesoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Unir al consumidor a un grupo específico
        await self.channel_layer.group_add("grupo_peso", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo al desconectar
        await self.channel_layer.group_discard("grupo_peso", self.channel_name)

    async def receive(self, text_data):
        # Manejar datos recibidos (si es necesario)
        pass

    async def enviar_peso(self, event):
        # Enviar el peso a los clientes WebSocket
        peso = event['peso']
        await self.send(text_data=json.dumps({
            'peso': peso
        }))


