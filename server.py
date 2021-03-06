import os
from functools import wraps

import gevent
from gevent.queue import Queue
from flask import Flask, Response, request, render_template


USERNAME = str(os.environ.get('USERNAME'))
PASSWORD = str(os.environ.get('PASSWORD'))
TRIGGER_EVENTS = ['edx.course.enrollment.activated', 'edx.bi.user.account.registered', 'Completed Order']


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
        by a pair of newline characters (i.e., a blank line).
        """
        if not self.data:
            # A colon as the first character of a message makes the message, in
            # essence, a comment. Messages beginning with a colon are ignored.
            return ':'

        # Process attributes, turning them into the lines of a message.
        lines = ['{}: {}'.format(key, value) for key, value in self.field_map.iteritems() if value]

        # Return a message which ends in a blank line and whose lines are separated
        # by a single newline character.
        return '{}\n\n'.format('\n'.join(lines))


app = Flask(__name__)
subscriptions = []


def check_credentials(username, password):
    """Check if a username and password combination is valid."""
    return username == USERNAME and password == PASSWORD


def authenticate():
    """Send a 401 response which enables basic auth."""
    return Response(
        'Authentication required',
        401,
        {'WWW-Authenticate': 'Basic realm="Authentication required"'}
    )


def requires_auth(route):
    """Require authentication to access a route."""
    @wraps(route)
    def with_auth(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_credentials(auth.username, auth.password):
            return authenticate()

        return route(*args, **kwargs)

    return with_auth


def notify(message):
    """Publish a message to all subscribers."""
    for subscription in subscriptions:
        subscription.put(message)


def event_stream():
    """Generate an event stream."""
    subscription = Queue()
    subscriptions.append(subscription)

    # Send a comment line to prevent request timeouts
    subscription.put(':keep-alive\n\n')

    try:
        for message in subscription:
            event = ServerSentEvent(str(message))
            # Each yield is sent to the client.
            yield event.encode()
    # Exception raised when the generator is closed
    except GeneratorExit:
        subscriptions.remove(subscription)


@app.route('/')
@requires_auth
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
        Status code 200 if a message is published successfully, or if no action
            is taken.
    """
    data = request.get_json()
    event_name = data.get('event')

    if event_name in TRIGGER_EVENTS:
        gevent.spawn(notify, event_name)

    return "OK"


@app.route('/stream')
@requires_auth
def stream():
    """Generate an event stream.
    
    Subscribes the client to future messages. Read more about this streaming
    pattern at http://goo.gl/4MDRNL.

    Returns:
        Status code 200 as events are generated successfully.
    """
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/subscriptions')
def debug():
    """Show a count of subscriptions.

    Returns:
        Status code 200 if a subscription count is returned successfully.
    """
    return "Current subscription count: {}".format(len(subscriptions))


if __name__ == '__main__':
    app.run()
