import requests
from config import BASE_URL

def get_updates(offset, timeout):
    params = {"offset": offset, "timeout": timeout}
    response = requests.get(f"{BASE_URL}/getUpdates", params=params)
    response.raise_for_status()
    return response.json()


def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}

    if reply_markup:
        import json
        data["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(f"{BASE_URL}/sendMessage", json=data)
    response.raise_for_status()
    return response.json()