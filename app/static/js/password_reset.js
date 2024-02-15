/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// waits for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // gets references to form elements and error message
    const form = document.getElementById('passwordResetForm');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const passwordMatchError = document.getElementById('passwordMatchError');

    // adds submit event listener to form
    form.addEventListener('submit', function(event) {
        // if the entered passwords match
        if (password.value !== confirmPassword.value) {
            // prevents defualt form submission
            event.preventDefault();

            // adds 'is-invalid' class to confirmPassword input field
            confirmPassword.classList.add('is-invalid');

            // displays password do not match error message
            passwordMatchError.style.display = 'block';
        } else {
            // removes 'is-invalid' class from confirmPassword input field
            confirmPassword.classList.remove('is-invalid');

            // hides password error message
            passwordMatchError.style.display = 'none';
        }
    });
});

// References:
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