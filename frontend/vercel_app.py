import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),
        "--server.port", os.environ.get("PORT", "8080"),
        "--server.address", "0.0.0.0",
    ]
    sys.exit(stcli.main())
