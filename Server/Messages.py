class Messages:
    def __init__(self, server, client, request):
        self.server = server
        self.client = client
        self.request = request

    def handle(self):
        self.validate()
        #Send message to target or broadcast

    def validate(self):
        #Check if required fields are present in request
        #Check if session_id is valid