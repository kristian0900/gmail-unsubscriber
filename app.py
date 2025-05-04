from flask import Flask
from automate_gmail import authenticate_gmail

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Gmail Unsubscriber Tool."

@app.route('/test-auth')
def test_auth():
    try:
        service = authenticate_gmail()
        return "✅ Gmail service authenticated successfully."
    except Exception as e:
        return f"❌ Auth failed: {e}"

@app.route('/run-unsubscribe', methods=['POST'])
def run_unsubscribe():
    import automate_gmail
    automate_gmail.main()
    return 'Unsubscribe tool run successfully.'



