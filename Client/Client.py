import socket
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal

class Client(QObject):
    response_received = pyqtSignal(dict)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = ''
        self.session_id = ''
        self.connected = False
        self.receive_thread = threading.Thread(target=self.receiveMessages, daemon=True)
        

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.connected = True
            print(f"Connection established to {self.host}:{self.port}")
            
        except Exception as e:
            print(f"Error connecting to server:\n{e}")

    def disconnect(self):
        if self.connected:
            self.sock.close()
            self.connected = False
            print("Disconnected from the server")
    
    def sendMessage(self, message, receiver='BROADCAST'):
        if self.connected:
            message_obj = {
                'type' : 'MESSAGE',
                'session_id' : self.session_id,
                'receiver' : receiver,
                'message' : message
            }
            self.sock.send(json.dumps(message_obj).encode('utf-8'))
    
    def authenticate(self, username, password):
        if self.connected:
            authentication_obj = {
                'type' : 'AUTHENTICATE',
                'username' : username,
                'password' : password
            }
            self.sock.send(json.dumps(authentication_obj).encode('utf-8'))
            response = self.receiveMessages(True)
            
            if response and response.get('session_id', ''):
                self.session_id = response['session_id']
                self.username = username
                self.password = password
                return True
            return False
    
    def register(self, username, password):
        if self.connected:
            registration_obj = {
                'type' : 'REGISTER',
                'username' : username,
                'password' : password
            }
            self.sock.send(json.dumps(registration_obj).encode('utf-8'))
            response = self.receiveMessages(True)
            if response and response.get('type', '') == 'SUCCESS':
                return True
            return False
    
    def logout(self):
        if self.connected and self.session_id:
            logout_obj = {
                'type' : 'LOGOUT',
                'session_id' : self.session_id
            }
            self.sock.send(json.dumps(logout_obj).encode('utf-8'))

    
    def receiveMessages(self, runOnce=False):
        while self.connected or runOnce:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Recieved message {data}")

                try:
                    response = json.loads(data)
                except json.JSONDecodeError as json_error:
                    print(f'Error decoding JSON: {json_error}')
                    print(f'Received data: {data}')
                    continue
                
                if runOnce:
                    return response

                self.response_received.emit(response)
            except Exception as e:
                print(f"Error while recieving messages.\n{e}")
                break
        self.disconnect()
