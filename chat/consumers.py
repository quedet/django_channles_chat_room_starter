from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from channels.auth import login, logout

from .models import Client, Room, Message

class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        """
        Event when client connects
        """
        # Accept the connexion
        self.accept()
        # Gets a random user not logged in
        user = User.objects.exclude(id__in=Client.objects.all().values("user")).order_by("?").first()
        # Login
        async_to_sync(login)(self.scope, user)
        self.scope["session"].save()
        # Display the username
        self.send_html({
            "selector": "#logged-user",
            "html": self.scope['user'].username,
        })
        # Register the client in the database to control who is conencted
        Client.objects.create(user=user, channel=self.channel_name)
        # Assign the group "hi", the first room that be displayed when you enter
        self.add_client_to_room("hi", True)
        # List the messages
        self.list_room_messages()
        
    
    def disconnect(self, close_code):
        """
        Event when client disconnects
        """
        # Remove the client from the current room
        self.remove_client_from_current_room()
        # Deregister the client
        Client.objects.get(channel=self.channel_name).delete()
        # Logout user
        logout(self.scope, self.scope["user"])
    
    
    def receive_json(self, data_received, **kwargs):
        """
            Event when data is received
            All information will arrive in 2 variables:
            'action' with the action to be taken
            'data' with the information
        """
        # Get the data
        data = data_received["data"]
        # Depending on the action we will do ne task or another
        match data_received["action"]:
            case "Change group":
                if data["isGroup"]:
                    self.add_client_to_room(data["groupName"], data["isGroup"])
                else:
                    user_target = User.objects.filter(username=data["groupName"]).first()
                    
                    room = Room.objects.filter(users_subscribed__in=[self.scope["user"]], is_group=False).intersection(Room.objects.filter(users_subscribed__in=[user_target], is_group=False)).first()
                    
                    if room and user_target and room.users_subscribed.count() == 2:
                        self.add_client_to_room(room.name)
                    else:
                        room = Room.objects.filter(users_subscribed__in=[user_target,], is_group=False,).last()
                        if room and room.users_subscribed.count() == 1:
                            self.add_client_to_rrom(room.name)
                        else:
                            self.add_client_to_room()
                self.send_room_name()
                
            case "New message":
                self.save_message(data["message"])
        self.list_room_messages()
        
    def send_html(self, event):
        """
        Event: Send html to the client
        """
        data = {
            "selector": event["selector"],
            "html": event["html"]
        }
        self.send_json(data)
    
    def list_room_messages(self):
        """List all messages from a group"""
        room_name = self.get_name_room_active()
        # Get the room
        room = Room.objects.get(name=room_name)
        # Get all messages from the room
        messages = Message.objects.filter(room=room).order_by("created_at")
        # Render Html and send to client
        async_to_sync(self.channel_layer.group_send)(room_name, {
            "type": "send.html",
            "selector": "#messages-list",
            "html": render_to_string("components/_list_messages.html", {"messages": messages})
        })
        
        
    def send_room_name(self):
        """Send the room name to the client"""
        room_name  =self.get_name_room_active()
        room = Room.objects.get(name=room_name)
        data = {
            "selector": "#group-name",
            # Concadena # if it is a group for aesthetic reasons
            "html": ("#" if room.is_group else "") + room_name,
        }
        self.send_json(data)
        
        
    def save_message(self, text):
        """Save a message in the database"""
        # Get the room
        room = Room.objects.get(name=self.get_name_room_active())
        # Save message
        Message.objects.create(user=self.scope["user"], room=room, text=text)
    
    
    def add_client_to_room(self, room_name=None, is_group=False):
        """Add customer to a room within channels and save the reference in the Room model"""
        client = Client.objects.get(user=self.scope["user"])
        self.remove_client_from_current_room()
        room, created = Room.objects.get_or_create(name=room_name, is_group=is_group)
        
        if not room.name:
            room.name = f"private_{room.id}"
            room.save()
        room.clients_active.add(client)
        room.users_subscribed.add(client.user)
        room.save()
        async_to_sync(self.channel_layer.group_add)(room.name, self.channel_name)
        self.send_room_name()
        
    def get_name_room_active(self):
        """Get the name of the groop from login user"""
        room = Room.objects.filter(clients_active__user_id=self.scope["user"].id).first()
        return room.name
    
    def remove_client_from_current_room(self):
        """Remove client from current group"""
        client = Client.objects.get(user=self.scope["user"])
        rooms = Room.objects.filter(clients_active__in=[client])
        
        for room in rooms:
            async_to_sync(self.channel_layer.group_discard)(room.name, self.channel_name)
            room.clients_active.remove(client)
            room.save()