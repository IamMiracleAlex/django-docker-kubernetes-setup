from channels.consumer import AsyncConsumer
import json

from channels.db import database_sync_to_async
from django.db.models import Q
from django_tenants.utils import schema_context

from accounts.models import User


class NotificationConsumer(AsyncConsumer):
	def __init__(self):
		self.data = dict()
		self.notifications = list()
		self.schema = 'public'
		self.user_id = None
		self.room = None

	async def websocket_connect(self, event):
		await self.send({"type": "websocket.accept"})

	async def websocket_receive(self, event):
		self.data = json.loads(event['text'])

		if self.data['action'] == 'connect':
			# data sent is {"action": "connect": "company": "", "user_id": 1}
			# data received is {"action": "connect", "room": "{schema}_{user_id}"}
			self.schema = self.data['company']
			self.user_id = self.data['user_id']
			self.room = f"{self.schema}_{self.user_id}"
			await self.channel_layer.group_add(
				self.room,
				self.channel_name
			)
			data = {"action": "connect", "room": self.room}
			await self.channel_layer.group_send(
				self.room, {"type": "send_message", "data": json.dumps(data)})
			# user = await self.get_user()
			# print(f"{user} connected successfully")

		if self.data['action'] == 'receive':

			# data sent is {"action": "receive": "room": "{company}_{user_id}"
			# data received is {"room":"{company}_{user_id}" , "data": [], "action": "receive"}
			if not self.room:
				self.room = self.data['room']
			if not self.user_id:
				self.user_id = self.data['room'].split('_')[1]
			if not self.schema:
				self.user_id = self.data['room'].split('_')[0]
			await self.retrieve_notifications()
			message = {"room": self.room, "data": self.notifications, "action": "receive"}
			await self.channel_layer.group_send(
				self.room, {"type": "send_message", "data": json.dumps(message)})
			# print('receive data')

	async def send_message(self, event):
		await self.send({"type": "websocket.send", "text": event['data']})

	async def websocket_disconnect(self, event):
		print('disconnected')

	@database_sync_to_async
	def retrieve_notifications(self):
		with schema_context(self.schema):
			pass
			return

	# @database_sync_to_async
	# def get_user(self):
	# 	with schema_context(self.schema):
	# 		return User.objects.get(id=self.user_id).full_name()
	#
