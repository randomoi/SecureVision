/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// changes file name in dropdown for notifications and motion mode
$(document).ready(function() {
    // retrieves stored notification preference from localStorage
    var storedNotificationPreference = localStorage.getItem('notificationPreference');

    // retrieves stored email notification preference from localStorage
    var storedNotificationPreference = localStorage.getItem('notificationPreference');

    // if stored email preference exists and matches it uses it
    if (storedNotificationPreference && ['all', 'hourly', 'none'].includes(storedNotificationPreference)) {
        $('#email-notifications-select').val(storedNotificationPreference);
    } else { // otherwise, sets to 'all'
        $('#email-notifications-select').val('all');
    }

    // listens for changes 
    $('#email-notifications-select').change(function() {
        // gets selected value from dropdown
        var valueSelected = $(this).val();

        // gets CSRF token from meta tag
        var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        // sends AJAX request to update email notification preference
        $.ajax({
            url: '/update_notifications',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                preference: valueSelected
            },
            success: function(response) {
                // capitalizes valueSelected 
                var emailNotificationPreferenceText = valueSelected.charAt(0).toUpperCase() + valueSelected.slice(1);

                // shows success message in '#universal-message-container'
                $('#universal-message-container')
                    .text("Email notification preference changed to " + emailNotificationPreferenceText)
                    .removeClass()
                    .addClass('alert alert-success')
                    .fadeIn('slow');

                // stores email notification preference in localStorage
                localStorage.setItem('notificationPreference', valueSelected);

                // hides success message after 2 secs
                setTimeout(function() { $('#universal-message-container').fadeOut('slow'); }, 2000);
            },
            error: function(response) {
                // shows error message in '#universal-message-container'
                $('#universal-message-container')
                    .text("Error! Can not update notification preference.")
                    .removeClass()
                    .addClass('alert alert-danger')
                    .fadeIn('slow');

                // hides error message 2 secs
                setTimeout(function() { $('#universal-message-container').fadeOut('slow'); }, 2000);
            }
        });
    });

    // listens for changes to 'motion-detection-select' dropdown
    $('#motion-detection-select').change(function() {
        // gets selected detection mode from dropdown
        var modeSelected = $(this).val();

        // gets CSRF token from meta tag
        var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        // sends AJAX request to update detection mode
        $.ajax({
            url: '/setup_motion_detection_mode',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                mode: modeSelected
            },
            success: function(response) {
                // shows success message in '#universal-message-container'
                $('#universal-message-container')
                    .text("Detection mode updated to " + modeSelected)
                    .removeClass()
                    .addClass('alert alert-success')
                    .fadeIn('slow')
                    .delay(2000)
                    .fadeOut('slow');
            },
            error: function(error) {
                // shows error message in '#universal-message-container'
                $('#universal-message-container')
                    .text("Error! Can not update detection mode.")
                    .removeClass()
                    .addClass('alert alert-danger')
                    .fadeIn('slow')
                    .delay(2000)
                    .fadeOut('slow');
            }
        });
    });

});


// References:
// https://api.jquery.com/fadeOut/
// https://learn.jquery.com/using-jquery-core/document-ready/
// https://stackoverflow.com/questions/42593178/how-can-i-do-metaname-csrf-token-attrcontent-in-vanilla-javascrip
// https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
// https://developer.mozilla.org/en-US/docs/Web/API/Element/getAttribute
// https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector
// https://flexiple.com/javascript/javascript-capitalize-first-letter#
// https://flexiple.com/javascript/javascript-capitalize-first-letter#
// https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
// https://www.w3schools.com/jsref/met_storage_getitem.asp

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/