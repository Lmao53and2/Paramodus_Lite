# run_app.py
import os
from streamlit.web import bootstrap

def resolve(path: str) -> str:
    return os.path.abspath(os.path.join(os.getcwd(), path))

if __name__ == "__main__":
    script = resolve("app.py")
    bootstrap.run(
        script,
        "streamlit run",
        [],
        {"_is_running_with_streamlit": True},
    )
