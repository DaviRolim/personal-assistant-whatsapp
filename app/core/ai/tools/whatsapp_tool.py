import os
from typing import Any, Dict, Optional

import requests


def send_message(
    number: str,
    text: str,
    api_key: str,
    instance: str,
    quoted: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send a WhatsApp message using the API.
    Returns True if successful, False otherwise.
    """
    url = f"{os.getenv('EVOLUTION_API_URL')}/message/sendText/{instance}"
    message_prefix = r"🤖 *James*\n\n"
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


async def get_base64_from_media_message(
    instance: str,
    message_id: str,
    api_key: str,
    convert_to_mp4: bool = False
) -> Optional[str]:
    """
    Get base64 encoded data from a media message.
    
    Args:
        instance: ID of the WhatsApp instance
        message_id: ID of the message containing media
        api_key: Evolution API key
        convert_to_mp4: Whether to convert video to MP4 format (for videos only)
        
    Returns:
        Optional[str]: Base64 encoded string of the media if successful, None otherwise
    """
    url = f"{os.getenv('EVOLUTION_API_URL')}/chat/getBase64FromMediaMessage/{instance}"
    
    payload = {
        "message": {
            "key": {
                "id": message_id
            }
        },
        "convertToMp4": convert_to_mp4
    }
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f'response: {response.json()}')
        response.raise_for_status()
        return response.json().get("base64")
    except Exception as e:
        print(f"Error getting base64 from media message: {e}")
        return None


