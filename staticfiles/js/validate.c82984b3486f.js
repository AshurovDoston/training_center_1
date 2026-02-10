/**
 * validate.js — Client-side form validation for login and signup
 *
 * Validates forms before submission and shows inline error messages.
 * Also gives real-time feedback when a user leaves a field (blur event).
 *
 * IMPORTANT: Client-side validation is for user experience only.
 * The server ALWAYS re-validates because a user could bypass JavaScript.
 * This is called "defense in depth" — never trust the client alone.
 *
 * === KEY CONCEPTS ===
 *
 * form.addEventListener('submit', function):
 *   Runs our validation code when the user clicks the submit button.
 *
 * event.preventDefault():
 *   Stops the form from submitting to the server. We call this when
 *   validation fails, so the user can fix errors first.
 *
 * element.closest(selector):
 *   Walks up the DOM tree from the element to find the nearest ancestor
 *   matching the selector. Used here to find the parent .form-group.
 *
 * element.textContent:
 *   Gets or sets the text inside an element. We use it to display
 *   error messages in the <span> placeholders.
 *
 * Regular Expressions (regex):
 *   Patterns for matching text. Used here to validate email format.
 *   /^[^\s@]+@[^\s@]+\.[^\s@]+$/ means: something@something.something
 *
 * 'blur' event:
 *   Fires when the user clicks or tabs AWAY from an input field.
 *   This gives immediate feedback without being annoying while typing.
 */

document.addEventListener('DOMContentLoaded', function () {

    /* =================================================================
       HELPER FUNCTIONS
       ================================================================= */

    /**
     * showError — Display an error message for a form field.
     *
     * Finds the error <span> by ID, sets its text, and adds a red border
     * to the input's parent .form-group.
     */
    function showError(input, errorId, message) {
        var errorSpan = document.getElementById(errorId);
        if (errorSpan) {
            errorSpan.textContent = message;
        }
        /* .closest() walks up the DOM to find the parent .form-group */
        var group = input.closest('.form-group');
        if (group) {
            group.classList.add('form-group--error');
            group.classList.remove('form-group--valid');
        }
    }

    /**
     * clearError — Remove the error message and add green border.
     */
    function clearError(input, errorId) {
        var errorSpan = document.getElementById(errorId);
        if (errorSpan) {
            errorSpan.textContent = '';
        }
        var group = input.closest('.form-group');
        if (group) {
            group.classList.remove('form-group--error');
            group.classList.add('form-group--valid');
        }
    }

    /**
     * isValidEmail — Check if a string looks like an email address.
     *
     * Uses a regular expression (regex). The pattern means:
     *   ^           — start of string
     *   [^\s@]+     — one or more characters that are NOT spaces or @
     *   @           — literal @ symbol
     *   [^\s@]+     — one or more characters that are NOT spaces or @
     *   \.          — literal dot
     *   [^\s@]+     — one or more characters that are NOT spaces or @
     *   $           — end of string
     *
     * .test(string) returns true if the string matches the pattern.
     */
    function isValidEmail(email) {
        var pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return pattern.test(email);
    }

    /* =================================================================
       LOGIN FORM VALIDATION
       ================================================================= */

    var loginForm = document.querySelector('#login-form');

    if (loginForm) {
        /*
         * 'submit' event fires when the user clicks the submit button
         * or presses Enter in a form field.
         */
        loginForm.addEventListener('submit', function (event) {
            var isValid = true;

            var username = loginForm.querySelector('#id_username');
            var password = loginForm.querySelector('#id_password');

            /* Validate username — must not be empty */
            if (!username.value.trim()) {
                showError(username, 'username-error', 'Please enter your username.');
                isValid = false;
            } else {
                clearError(username, 'username-error');
            }

            /* Validate password — must not be empty */
            if (!password.value) {
                showError(password, 'password-error', 'Please enter your password.');
                isValid = false;
            } else {
                clearError(password, 'password-error');
            }

            /* If any field failed validation, prevent the form from submitting */
            if (!isValid) {
                event.preventDefault();
            }
        });

        /*
         * REAL-TIME VALIDATION ON BLUR
         *
         * 'blur' fires when the user clicks or tabs away from an input.
         * querySelectorAll('input[required]') finds all inputs with the
         * required attribute — username and password on the login form.
         */
        var loginInputs = loginForm.querySelectorAll('input[required]');
        loginInputs.forEach(function (input) {
            input.addEventListener('blur', function () {
                /*
                 * Build the error span ID from the input's ID.
                 * id_username → username → username-error
                 */
                var fieldName = this.id.replace('id_', '');
                var errorId = fieldName + '-error';

                if (!this.value.trim()) {
                    showError(this, errorId, 'This field is required.');
                } else {
                    clearError(this, errorId);
                }
            });
        });
    }

    /* =================================================================
       SIGNUP FORM VALIDATION
       ================================================================= */

    var signupForm = document.querySelector('#signup-form');

    if (signupForm) {
        signupForm.addEventListener('submit', function (event) {
            var isValid = true;

            var username = signupForm.querySelector('#id_username');
            var email = signupForm.querySelector('#id_email');
            var password1 = signupForm.querySelector('#id_password1');
            var password2 = signupForm.querySelector('#id_password2');

            /* Username: required, minimum 3 characters */
            if (!username.value.trim()) {
                showError(username, 'username-error', 'Please choose a username.');
                isValid = false;
            } else if (username.value.trim().length < 3) {
                showError(username, 'username-error', 'Username must be at least 3 characters.');
                isValid = false;
            } else {
                clearError(username, 'username-error');
            }

            /* Email: required, must look like a valid email */
            if (!email.value.trim()) {
                showError(email, 'email-error', 'Please enter your email.');
                isValid = false;
            } else if (!isValidEmail(email.value.trim())) {
                showError(email, 'email-error', 'Please enter a valid email address.');
                isValid = false;
            } else {
                clearError(email, 'email-error');
            }

            /* Password: required, minimum 8 characters */
            if (!password1.value) {
                showError(password1, 'password1-error', 'Please enter a password.');
                isValid = false;
            } else if (password1.value.length < 8) {
                showError(password1, 'password1-error', 'Password must be at least 8 characters.');
                isValid = false;
            } else {
                clearError(password1, 'password1-error');
            }

            /* Confirm password: must match the password above */
            if (!password2.value) {
                showError(password2, 'password2-error', 'Please confirm your password.');
                isValid = false;
            } else if (password1.value !== password2.value) {
                showError(password2, 'password2-error', 'Passwords do not match.');
                isValid = false;
            } else {
                clearError(password2, 'password2-error');
            }

            if (!isValid) {
                event.preventDefault();
            }
        });

        /* Real-time blur validation for signup fields */
        var signupInputs = signupForm.querySelectorAll('input[required]');
        signupInputs.forEach(function (input) {
            input.addEventListener('blur', function () {
                var fieldName = this.id.replace('id_', '');
                var errorId = fieldName + '-error';

                if (!this.value.trim()) {
                    showError(this, errorId, 'This field is required.');
                } else if (fieldName === 'email' && !isValidEmail(this.value.trim())) {
                    showError(this, errorId, 'Please enter a valid email address.');
                } else if (fieldName === 'password1' && this.value.length < 8) {
                    showError(this, errorId, 'Password must be at least 8 characters.');
                } else {
                    clearError(this, errorId);
                }
            });
        });
    }

});
