from flask import Flask, render_template, request, redirect
import automate_gmail

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-unsubscribe', methods=['POST'])
def run_unsubscribe():
    # Run the Gmail unsubscribe tool
    automate_gmail.main()
    return redirect('/success')

@app.route('/success')
def success():
    return "<h2>✅ Unsubscribing complete! You may close this window.</h2>"

if __name__ == '__main__':
    app.run(debug=True)
def main():
    asyncio.run(run())


