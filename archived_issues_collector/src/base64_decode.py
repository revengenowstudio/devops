import base64

def base64_decode(data: str) -> str:
    return base64.b64decode(data).decode('utf-8')
