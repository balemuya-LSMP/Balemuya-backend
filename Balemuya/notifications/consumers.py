import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from geopy.distance import geodesic


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        token = self.get_token_from_query_string()
        if not token:
            return await self.reject_connection("Unauthorized: Missing token.")

        self.user = await self.authenticate_user(token)
        if not self.user:
            return await self.reject_connection("Unauthorized: Invalid or missing token.")
        
        self.group_name = f"user_{self.user.id}_notifications"
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "message": f"Connected to group: {self.group_name}"
        }))

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    def get_token_from_query_string(self):
        query_string = self.scope["query_string"].decode("utf-8")
        return query_string.split("token=")[-1] if "token=" in query_string else None

    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = get_user_model().objects.get(id=user_id)
            return user if user.is_authenticated else None
        except Exception:
            return None

    async def reject_connection(self, message):
        await self.send(text_data=json.dumps({"error": message}))
        await self.close(code=4000)

    async def send_notification(self, event):
        notification = event['message']
        await self.send(text_data=json.dumps({
            'notification': notification
        }))

    async def notify_user_about_service_post(self, service_post):
        group_name = f"user_{service_post.customer.id}_notifications"
        message = f"New service post created: {service_post.title}"
        
        await self.channel_layer.group_send(group_name, {
            'type': 'send_notification',
            'message': message
        })

    async def notify_professionals_about_service_post(self, service_post):
        professionals_in_range = await self.get_professionals_in_proximity_and_category(service_post)
        for professional in professionals_in_range:
            group_name = f"professional_{professional.id}_notifications"
            message = f"New service post in your category: {service_post.title}"
            
            await self.channel_layer.group_send(group_name, {
                'type': 'send_notification',
                'message': message
            })

    async def notify_customer_about_application(self, service_post, professional):
        group_name = f"user_{service_post.customer.id}_notifications"
        message = f"Professional {professional.name} has applied for your service post."
        
        await self.channel_layer.group_send(group_name, {
            'type': 'send_notification',
            'message': message
        })

    async def notify_professional_about_verification(self, professional):
        group_name = f"professional_{professional.id}_notifications"
        message = "Your account has been verified!"
        
        await self.channel_layer.group_send(group_name, {
            'type': 'send_notification',
            'message': message
        })

    @database_sync_to_async
    def get_professionals_in_proximity_and_category(self, service_post):
        from users.models import Professional, Address 
        service_post_location = (service_post.location.latitude, service_post.location.longitude)
        proximity_radius = 50  # in km
        category = service_post.category 

        professionals = Professional.objects.all()
        professionals_in_range_and_category = []

        for professional in professionals:
            if professional.category != category:
                continue  

            current_address = professional.user.addresses.filter(is_current=True).first()

            if not current_address:
                continue  

            # Get the latitude and longitude from the user's current address
            professional_location = (current_address.latitude, current_address.longitude)

            # Calculate distance between the professional and the service post
            distance = geodesic(service_post_location, professional_location).kilometers
            
            # Check if the professional is within the proximity radius
            if distance <= proximity_radius:
                professionals_in_range_and_category.append(professional)

        return professionals_in_range_and_categoryin_range_and_category
