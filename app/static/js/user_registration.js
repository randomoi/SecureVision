/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// waits for DOM to load
document.addEventListener("DOMContentLoaded", function() {
    // check email format 
    const emailInputField = document.querySelector('input[name="email"]');
    emailInputField.addEventListener('input', function() {
        // regular expression for valid email format
        const emailValRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!emailValRegex.test(emailInputField.value) && emailInputField.value !== '') {
            // adds 'is-invalid' class for invalid email format
            emailInputField.classList.add('is-invalid');
        } else {
            // removes 'is-invalid' class for valid email format
            emailInputField.classList.remove('is-invalid');
        }
    });

    // checks password format 
    const passwordInputField = document.querySelector('input[name="password"]');
    passwordInputField.addEventListener('input', function() {
        // regular expression for valid password format
        const passwordValRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])/;
        if (!passwordValRegex.test(passwordInputField.value) && passwordInputField.value !== '') {
            // adds 'is-invalid' class for invalid password format
            passwordInputField.classList.add('is-invalid');
        } else {
            // removes 'is-invalid' class for valid password format
            passwordInputField.classList.remove('is-invalid');
        }
    });
});

// References:
// https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector
// https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementById
// https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
// https://gist.github.com/cgkio/7268045
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/test
// https://getbootstrap.com/docs/5.0/forms/validation/

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/