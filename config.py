import os 


ngrok_url = "overly-mutual-seagull.ngrok-free.app"
username  = "xerox"
password  = os.environ["NGROK_PASSWORD"] if "NGROK_PASSWORD" in os.environ else ""
