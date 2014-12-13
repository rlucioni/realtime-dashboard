import os
import time

import gevent
from gevent.queue import Queue
from flask import Flask, Response, request, render_template


class ServerSentEvent(object):
    """A message to be included in an event stream.

    Read more about server-sent events at http://goo.gl/YTettR.

    Attributes:
        event (str): The event's type. If specified, an event will be dispatched
            on the browser to the listener for the specified event name; the site 
            would use addEventListener() to listen for named events. The onmessage
            handler is called if no event name is specified for a message.

        data (str): The data field for the message. When an EventSource receives
            multiple consecutive lines that begin with "data:" it will concatenate
            them, inserting a newline character between each one. Trailing
            newlines are stripped.

        id (str): The event ID to set the EventSource object's last event ID value to.
        
        field_map (dict): Contains the aformentioned attributes.
    """
    def __init__(self, data):
        """Initialize ServerSentEvent with data."""
        self.event = None
        self.data = data
        self.id = None
        self.field_map = {
            'event': self.event,
            'data': self.data,
            'id': self.id
        }

    def encode(self):
        """Encode the event's data as a string.

        According to the specification, an event stream is a simple stream of text
        data, which must be encoded using UTF-8. Each message should be separated
        by a pair of newline characters.
        """
        if not self.data:
            # A colon as the first character of a message makes the message, in
            # essence, a comment. Messages beginning with a colon are ignored.
            return ':'

        lines = ['{}: {}'.format(key, value) for key, value in self.field_map.iteritems() if value]

        return '{}\n\n'.format('\n'.join(lines))


app = Flask(__name__)
subscriptions = []


@app.route('/')
def index():
    """Render the index page.

    Returns:
        Status code 200 if the index page is sent successfully.
    """
    return render_template('index.html')


@app.route('/publish', methods=['POST'])
def publish():
    """Publish a POSTed message to all subscribers.

    Can be used as the target URL for a webhook to publish messages based on the
    webhook's payload.

    Returns:
        Status code 200 if a message is published successfully.
    """
    def notify():
        message = str(time.time())
        for subscription in subscriptions:
            subscription.put(message)

    # data = request.get_json()
    # if data.get('event') == 'edx.bi.user.account.authenticated':
    gevent.spawn(notify)

    return "OK"


@app.route('/subscribe')
def subscribe():
    """Generate an event stream.
    
    Subscribes the client to future messages. Read more about this streaming
    pattern at http://goo.gl/4MDRNL.

    Returns:
        Status code 200 as events are generated successfully.
    """
    def events():
        queue = Queue()
        subscriptions.append(queue)

        try:
            for message in queue:
                event = ServerSentEvent(str(message))
                # Each yield is sent to the client.
                yield event.encode()
        except GeneratorExit:
            subscriptions.remove(queue)

    return Response(events(), mimetype='text/event-stream')


@app.route('/subscription_count')
def debug():
    """Show a count of subscriptions.

    Returns:
        Status code 200 if a subscription count is returned successfully.
    """
    return "Current subscription count: {}".format(len(subscriptions))


if __name__ == '__main__':
    app.run(debug=True)
