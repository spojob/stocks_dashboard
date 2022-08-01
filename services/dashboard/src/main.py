from app import app
import settings as settings

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)