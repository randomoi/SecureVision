/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

document.addEventListener("DOMContentLoaded", function() {
    // checks if passwords match
    const form = document.querySelector('form');
    const currentPasswordInputField = document.getElementById('current_password');
    const currentPasswordError = document.getElementById('current_password_error');
    const newPasswordInputField = document.getElementById('new_password');
    const confirmPasswordInputField = document.getElementById('confirm_password');
    const confirmPasswordError = document.getElementById('confirm_password_error');

    // adds event listener to confirmPasswordInputField for real-time validation
    confirmPasswordInputField.addEventListener('input', function() {
        // if new password and confirm password do not match and confirm password is not empty
        if (newPasswordInputField.value !== confirmPasswordInputField.value && confirmPasswordInputField.value !== '') {
            // shows error message and add the 'is-invalid' class to confirm password input field
            confirmPasswordError.style.display = 'block';
            confirmPasswordError.textContent = 'Passwords do not match!';
            confirmPasswordInputField.classList.add('is-invalid');
        } else {
            // hides error message and removes 'is-invalid' class from confirm password input field
            confirmPasswordError.style.display = 'none';
            confirmPasswordError.textContent = '';
            confirmPasswordInputField.classList.remove('is-invalid');
        }
    });

    // adds event listener to form submission
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // prevents default form submission 

        // sends POST request to validate current password on form submission
        fetch('/validate-current-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value,
                },
                body: 'current_password=' + encodeURIComponent(currentPasswordInputField.value)
            })
            .then(response => {
                if (!response.ok) {
                    // handles error
                    return response.json().then(data => Promise.reject(data));
                }
                return response.json();
            })
            .then(data => {
                // submit form with correct password
                form.submit();
            })
            .catch(error => {
                // password is incorrect shows error message
                currentPasswordError.style.display = 'block';
                currentPasswordError.textContent = error.error || 'Error while validating your password.';
                currentPasswordInputField.classList.add('is-invalid');
            });
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