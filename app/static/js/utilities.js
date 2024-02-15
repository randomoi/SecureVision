/*
START - This code was copied from referenced resources. Please see referenced links.
*/

// https://getbootstrap.com/docs/5.0/components/tooltips/

// gets list of elements with 'data-bs-toggle="tooltip"' attribute
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))

// initialize tooltips for each element in the list
var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// http://www.java2s.com/ref/javascript/javascript-string-totitlecase.html
// converts a string to title case 
function toTitleCase(str) {
    return str.replace(/\w\S*/g, function(txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

// https://getbootstrap.com/docs/5.0/components/toasts/
// shows toast message
function displayToast(message) {
    // gets toast container element by ID
    const toastContainer = document.getElementById('toast-message-container');

    // creates a unique ID for toast
    const toastId = `toast-${Date.now()}`;

    // creates HTML structure for toast
    const toastHtml = `
        <div class="toast align-items-center toast-success-color" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>`;

    // adds toast HTML to toast container
    toastContainer.innerHTML += toastHtml;

    // create new Bootstrap Toast element with a  3 secs delay
    const toastElement = new bootstrap.Toast(document.getElementById(toastId), {
        delay: 3000
    });

    // shows toast message
    toastElement.show();
}

// https://codyhouse.co/ds/components/info/flash-messages
// https://getbootstrap.com/docs/5.0/components/alerts/
// waits for DOM to load
document.addEventListener("DOMContentLoaded", function() {
    // selects all elements with class 'flash-message'
    var flashMessages = document.querySelectorAll('.flash-message');

    // set a timeout to hide each message after 2 secs
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            // hides message 
            message.style.display = 'none';
        }, 2000);
    });
});


// References:
// https://getbootstrap.com/docs/5.0/components/tooltips/
// http://www.java2s.com/ref/javascript/javascript-string-totitlecase.html
// https://getbootstrap.com/docs/5.0/components/toasts/
// https://codyhouse.co/ds/components/info/flash-messages
// https://getbootstrap.com/docs/5.0/components/alerts/

/*
END - This code was copied from referenced resources. Please see referenced links.
*/