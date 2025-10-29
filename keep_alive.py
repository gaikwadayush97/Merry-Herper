from flask import Flask
from threading import Thread

# Create a simple Flask web server
# This will be used for uptime monitoring services like UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    # Simple response to confirm the bot is running
    return "Merry Harper Bot is alive!"

def run():
    # Run Flask server on port 8080
    # host='0.0.0.0' makes it accessible from outside
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Start the Flask server in a separate thread
    # This allows the bot to run while the server is also running
    t = Thread(target=run)
    t.daemon = True  # Thread will close when main program exits
    t.start()
    print("Keep-alive server started on port 8080")
