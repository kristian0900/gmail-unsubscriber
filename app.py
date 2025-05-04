from flask import Flask, render_template_string
import automate_gmail
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Gmail Unsubscriber Tool."

@app.route('/run-unsubscribe', methods=['GET'])
def run_unsubscribe():
    try:
        automate_gmail.main()
        return render_template_string("""
            <div style="color: limegreen; font-weight: bold;">
                ✅ Gmail unsubscribe automation completed successfully.
            </div>
        """)
    except Exception as e:
        return render_template_string(f"""
            <div style="color: red; font-weight: bold;">
                ❌ An error occurred:<br>
                <pre>{traceback.format_exc()}</pre>
            </div>
        """), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





