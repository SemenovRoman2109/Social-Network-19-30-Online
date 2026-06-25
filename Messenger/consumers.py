from channels.generic.websocket import AsyncWebsocketConsumer

online_users = set()

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(group= self.user_group_name, channel= self.channel_name)
        online_users.add(set(self.channel_name))
        await self.accept()

    async def disconnect(self):
        if self.user.id in online_users:
            online_users[self.user.id].discard(self.channel_name)
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get("action")
        if action == "get_user_status":
            user_id = content["user_id"]
            await self.send_json({
                "action": "user_status",
                "user_id": user_id,
                "status": "online" if user_id in online_users else "offline"
            })

    async def get_statuses(self, content):
        user_ids = content["user_ids"]
        
        online = []
        
        for u in user_ids:
            if u in online_users:
                online.append(u)
        
        await self.send_json({
            "online_users": online
        })