# main.py
import uvicorn
import ngrok  # pyngrok-like wrapper (depending on your library)

from server import create_app

VALID_USERNAME = "user"
VALID_PASSWORD = "pass"

if __name__ == "__main__":
    app = create_app(valid_username=VALID_USERNAME, valid_password=VALID_PASSWORD)

    public_url = ngrok.connect(
        addr=8000,
        auth=f"{VALID_USERNAME}:{VALID_PASSWORD}",
        bind_tls=True,
        authtoken_from_env=True,
    )

    print(f"🔗 Public URL: {public_url}")

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        ngrok.kill()

