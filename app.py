from flask import Flask, render_template, redirect, url_for
import automate_gmail

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-unsubscriber")
def run_unsubscriber():
    try:
        automate_gmail.run_automation()
        return "Unsubscribe process completed successfully!"
    except Exception as e:
        return f"Error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/test-auth')
def test_auth():
    try:
        from automate_gmail import authenticate_gmail
        service = authenticate_gmail()
        profile = service.users().getProfile(userId='me').execute()
        return f"✅ Auth Success! Gmail address: {profile['emailAddress']}"
    except Exception as e:
        return f"❌ Auth Failed: {str(e)}", 500


