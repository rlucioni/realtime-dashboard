(function( window, $ ) {
    // The EventSource interface is used to receive server-sent events. It
    // connects to a server over HTTP and receives events in "text/event-stream"
    // format without closing the connection. Read more at http://goo.gl/zftAYW.
    var eventSource = new EventSource( '/stream' ),
        REGISTRATION = 'edx.bi.user.account.registered',
        ENROLLMENT = 'edx.course.enrollment.activated',
        PAYMENT = 'Completed Order',
        $rippleContainer = $( '#ripple-container' ),
        $ripple = $( '<div/>' ),
        radius = 35,
        message;

    $ripple
        .addClass( 'circle' )
        .css({
            top: $rippleContainer.height()/2 - radius,
            left: $rippleContainer.width()/2 - radius
        });

    // The `onmessage` handler is called if no name is specified for a
    // server-sent event.
    eventSource.onmessage = function( event ) {
        event.preventDefault();
        message = event.data;
        
        console.log( message );

        // Don't animate keep-alive events.
        if ( message != ':keep-alive' ) {
            if ( message === REGISTRATION ) {
                $ripple
                    .removeClass( 'enrollment payment' )
                    .addClass( 'registration' );
            } else if ( message === ENROLLMENT ) {
                $ripple
                    .removeClass( 'registration payment' )
                    .addClass( 'enrollment' );
            } else if ( message === PAYMENT ) {
                $ripple
                    .removeClass( 'enrollment registration' )
                    .addClass( 'payment' );
            }
            
            $ripple.appendTo( $rippleContainer );

            window.setTimeout( function() {
                $ripple.remove();
            }, 2000);
        }
    };
})( window, jQuery );
