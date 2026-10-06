import requests


def send_sms(to, text):

    data = {
        "from": "50004001512961",
        "to": to,
        "text": text,
    }

    response = requests.post('https://console.melipayamak.com/api/send/simple/0cacb0e6e90c49878d9718154631acb7', json=data)

    return response.json()