(function(window, $) {
    // The EventSource interface is used to receive server-sent events. It
    // connects to a server over HTTP and receives events in "text/event-stream"
    // format without closing the connection. Read more at http://goo.gl/zftAYW.
    var eventSource = new EventSource('/subscribe'),
        eventContainer = $('#events'),
        $div = $('<div/>');

    // The `onmessage` handler is called if no name is specified for a
    // server-sent event.
    eventSource.onmessage = function(event) {
        event.preventDefault();
        console.log(event.data);

        $div
            .addClass('circle')
            .css({
                top: eventContainer.height()/2 - 35,
                left: eventContainer.width()/2 - 35
            })
            .appendTo(eventContainer);

        window.setTimeout(function() {
            $div.remove();
        }, 2000);
    };
})(window, jQuery);
