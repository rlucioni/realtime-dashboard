import os
import time

from flask import Flask, Response, request, render_template
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue


class ServerSentEvent(object):
    """Read more about SSE at http://mzl.la/UPFyxY"""
    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: 'data',
            self.event: 'event',
            self.id: 'id'
        }

    def encode(self):
        if not self.data:
            return ''
        
        lines = ["{}: {}".format(value, key) for key, value in self.desc_map.iteritems() if key]
        return "{}\n\n".format("\n".join(lines))


# Initialize the Flask application
app = Flask(__name__)
subscriptions = []


@app.route('/', methods=['GET'])
def index():
    """Render the index page.

    Returns:
        HttpResponse: 200 if the index page was sent successfully.
    """
    return render_template('index.html')


@app.route('/publish', methods=['POST'])
def publish():
    """Handle data coming from Segment's webhook."""
    def notify():
        msg = str(time.time())
        for sub in subscriptions:
            sub.put(msg)

    data = request.get_json()
    if data.get('event') == 'edx.bi.user.account.authenticated':
        gevent.spawn(notify)

    return "OK"


@app.route('/subscribe', methods=['GET'])
def subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)

        try:
            while True:
                result = q.get()
                event = ServerSentEvent(str(result))
                yield event.encode()
        # Could also use Flask signals
        except GeneratorExit:
            subscriptions.remove(q)

    return Response(gen(), mimetype='text/event-stream')


@app.route('/debug')
def debug():
    return "Current subscription count: {}".format(len(subscriptions))


# Run the app. Visit localhost:5000 to subscribe, and send messages
# by visiting localhost:5000/publish
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    server = WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
