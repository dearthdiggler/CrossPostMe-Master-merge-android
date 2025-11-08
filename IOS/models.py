# Example: Ported API models for iOS app (to be rewritten in Swift/Dart)
# Reference: CrossPostMe/models.py


class User:
    def __init__(self, id, username, email, is_active):
        self.id = id
        self.username = username
        self.email = email
        self.is_active = is_active


class StatusCheck:
    def __init__(self, id, client_name, timestamp):
        self.id = id
        self.client_name = client_name
        self.timestamp = timestamp


# Add more models as needed for your mobile app
