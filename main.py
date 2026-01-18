import uvicorn
import ngrok

from server import create_app
from config import ngrok_url, username, password


if __name__ == "__main__":
    app = create_app(valid_username=username, valid_password=password)

    public_url = ngrok.connect(
        addr=8000,
        auth=f"{username}:{password}",
        bind_tls=True,
        authtoken_from_env=True,
        domain=ngrok_url,
    )

    print(f"🔗 Public URL: {public_url}")

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        ngrok.kill()

