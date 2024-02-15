/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

$(document).ready(function() {
    // checks each nav-link to see if it matches current URL
    $('a.nav-link').each(function() {
        if (this.href === window.location.href) {
            // adds 'active' class to matching nav-link
            $(this).addClass('active');
            // finds nearest collapsible parent and add 'show' class to expand it
            $(this).closest('.collapse').addClass('show');
        }
    });

    // displays Google Drive connection confirmation message
    function displayGoogleDriveConnectionMessage() {
        // fades it after 2 secs
        $('#confirmationMessage').fadeIn('slow').delay(2000).fadeOut('slow');
    }

    // AJAX call to verify if Google Drive connection message needs to be shown
    $.get('/check-google-drive-connection', function(response) {
        if (response.connectedOneTime) {
            // if connected, show message 
            displayGoogleDriveConnectionMessage();
        }
    });

    // updates Google Drive connection button based on status
    function updateGoogleDriveButtonBasedOnStatus(isConnected) {
        if (isConnected) {
            // update button text, class, and disables button
            $('#connectToGoogleDrive')
                .text('Drive Connected')
                .removeClass('btn-secondary')
                .addClass('btn-success')
                .prop('disabled', true);
        } else {
            // updates button text, class, and enables button
            $('#connectToGoogleDrive')
                .text('Not Connected')
                .addClass('btn-secondary')
                .removeClass('btn-success')
                .prop('disabled', false);
        }
    }

    // AJAX call to verify Google Drive status
    $.get('/api/google-drive/status', function(response) {
        // calls update function to set button state
        updateGoogleDriveButtonBasedOnStatus(response.isConnected);
    });

    // AJAX call to verify if Google Drive connection message should be dispalyed
    $.get('/check-google-drive-connection', function(response) {
        if (response.connectedOneTime) {
            // updates to show message 
            $('#universal-message-container')
                .html("<div class='alert alert-success'>Connected to Google Drive!</div>")
                .fadeIn('slow')
                .delay(2000)
                .fadeOut('slow');
        }
    });

    // attaches event listener to connect to Google Drive button
    $('#connectToGoogleDrive').click(function() {
        var connectUrl = $(this).data('connect-url');
        // redirects to Google Drive connection URL when button is clicked
        window.location.href = connectUrl;
    });
});

// References:

// https://api.jquery.com
// https://www.w3schools.com/jquery/jquery_fade.asp#:~:text=The%20jQuery%20fadeOut()%20method%20is%20used%20to%20fade%20out,the%20duration%20of%20the%20effect.
// https://api.jquery.com/fadeOut/
// https://www.w3schools.com/jquery/eff_fadeout.asp
// https://css-tricks.com/snippets/jquery/add-active-navigation-class-based-on-url/
// https://www.youtube.com/watch?v=HpjW9eaFLIg
// https://stackoverflow.com/questions/20060467/add-active-navigation-class-based-on-url
// https://forum.freecodecamp.org/t/help-with-jquery-scrolling/47393
// https://stackoverflow.com/questions/71439216/jquery-fadeout-message-after-2-seconds
// https://learn.jquery.com/using-jquery-core/faq/how-do-i-disable-enable-a-form-element/
// https://stackoverflow.com/questions/47685621/how-do-you-make-an-ajax-call-to-google-drive-api
// https://stackoverflow.com/questions/3522090/event-when-window-location-href-changes

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/