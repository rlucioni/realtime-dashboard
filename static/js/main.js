(function(window, $) {
    var eventSource = new EventSource('/subscribe'),
        eventContainer = $('#events'),
        $div = $('<div/>');

    eventSource.onmessage = function(event) {
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
