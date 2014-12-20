(function( window, $ ) {
    // The EventSource interface is used to receive server-sent events. It
    // connects to a server over HTTP and receives events in "text/event-stream"
    // format without closing the connection. Read more at http://goo.gl/zftAYW.
    var eventSource = new EventSource( '/stream' ),
        $rippleContainer = $( '#ripple-container' ),
        $ripple = $( '<div/>' ),
        radius = 35;

    // The `onmessage` handler is called if no name is specified for a
    // server-sent event.
    eventSource.onmessage = function( event ) {
        event.preventDefault();
        console.log( event.data );

        // Don't animate keep-alive events.
        if ( event.data != ':keep-alive' ) {
            $ripple
                .addClass( 'circle' )
                .css({
                    top: $rippleContainer.height()/2 - radius,
                    left: $rippleContainer.width()/2 - radius
                })
                .appendTo( $rippleContainer );

            window.setTimeout( function() {
                $ripple.remove();
            }, 2000);
        }
    };
})( window, jQuery );
