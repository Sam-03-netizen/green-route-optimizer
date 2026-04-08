from src.api.app import app
import uvicorn


def main():
    """Entry point for OpenEnv validator."""
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()