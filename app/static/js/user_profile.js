/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// waits for DOM to load
document.addEventListener("DOMContentLoaded", function() {
    // gets change password link and password change elements
    var linkForChangePassword = document.getElementById("linkForChangePassword");
    var passwordChangeSection = document.getElementById("changePasswordSection");

    // toggles password section visibility
    function togglePasswordChangeSection(show) {
        passwordChangeSection.style.display = show ? 'block' : 'none';
        linkForChangePassword.style.display = show ? 'none' : 'block';
    }

    // checks for validation errors in password section
    var passwordErrors = passwordChangeSection.querySelectorAll('.alert-danger');
    var shouldShowPasswordSection = passwordErrors.length > 0;

    // sets visibility based on errors
    togglePasswordChangeSection(shouldShowPasswordSection);

    // adds event listener to change password link
    if (linkForChangePassword) {
        linkForChangePassword.addEventListener("click", function(event) {
            event.preventDefault();
            togglePasswordChangeSection(true);
        });
    }
});

// References:
// https://www.w3schools.com/howto/howto_js_toggle_hide_show.asp
// https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector
// https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById
// https://developer.mozilla.org/en-US/docs/Web/API/Element/classList
// https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then
// https://gist.github.com/odewahn/5a5eeb23279eed6a80d7798fdb47fe91
// https://stackoverflow.com/questions/68289406/flask-hidden-input-field-with-csrf-token-is-visible-in-elements-pane
// https://webpy.org/cookbook/csrf
// https://stackoverflow.com/questions/22363838/submit-form-after-calling-e-preventdefault

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/