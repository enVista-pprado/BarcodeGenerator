import sys
import subprocess
import os

def main():
    # Determine folder where the EXE is running
    if getattr(sys, "frozen", False):
        app_dir = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to app.py (inside same folder)
    app_path = os.path.join(app_dir, "app.py")

    # Use the bundled Python interpreter
    python = sys.executable

    # Launch Streamlit app
    subprocess.Popen([python, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
