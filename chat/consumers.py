from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        """
        Event when client connects
        """
        # Accept the connexion
        self.accept()
        # Send data to the client
        # self.send(text_data="Yeah !")
        #
        print("Hi!")
        async_to_sync(self.channel_layer.group_send)("Main", {
            "type": "send.hi",
            "data": "Hello Everyone !"
        })
        
    def disconnect(self, code):
        """
        Event when client disconnects
        """
        return super().disconnect(code)
    
    #
    def send_hi(self, event):
        """
        Event: Send "hi" to the client
        """
        print("Hi")
        data = {
            "data": event["data"]
        }
        self.send_json(data)