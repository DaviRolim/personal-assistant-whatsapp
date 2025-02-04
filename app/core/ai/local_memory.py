# Singleton list to store message history
_message_history = []

def get_messages():
    return _message_history

def add_message(role: str, content: str):
    _message_history.append({"role": role, "content": content})

def clear_messages():
    global _message_history
    _message_history = []
