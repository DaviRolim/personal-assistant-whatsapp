from typing import Any, Dict, Optional

import requests


def send_message(
    number: str,
    text: str,
    api_key: str,
    quoted: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send a WhatsApp message using the API.
    Returns True if successful, False otherwise.
    """
    url = "http://api:8080/message/sendText/daviwpp"

    # update the text to start with "🤖 *James* 🤖"
    message_prefix = "🤖 *James* 🤖 \n\n"
    text = f"{message_prefix}{text}"
    payload = {
        "number": number,
        "text": text
    }
    
    if quoted:
        payload["quoted"] = quoted
        
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Message sent successfully")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
