/**
 * main.js — Global scripts loaded on every page
 *
 * This file handles two features:
 * 1. Mobile hamburger menu toggle (show/hide navigation)
 * 2. Smooth scrolling for anchor links (links that start with #)
 *
 * === KEY JAVASCRIPT CONCEPTS USED HERE ===
 *
 * document.querySelector(selector)
 *   Finds the FIRST HTML element matching a CSS selector.
 *   Example: document.querySelector('#hamburger-btn') finds <button id="hamburger-btn">
 *
 * document.querySelectorAll(selector)
 *   Finds ALL elements matching a CSS selector. Returns a NodeList (like an array).
 *
 * element.addEventListener(event, function)
 *   Attaches a function that runs when the specified event occurs.
 *   Common events: 'click', 'input', 'submit', 'keydown', 'DOMContentLoaded'
 *
 * element.classList.toggle(className)
 *   Adds the class if it's missing, removes it if it's present.
 *   Returns true if the class was added, false if removed.
 *
 * element.setAttribute(name, value)
 *   Changes an HTML attribute. Used here for aria-expanded accessibility.
 */

/* ===== Wait for HTML to be fully loaded before running scripts ===== */

/*
 * 'DOMContentLoaded' fires when the HTML document has been completely parsed.
 * We wrap all our code in this listener to prevent errors from trying to
 * find elements that haven't been created yet.
 */
document.addEventListener('DOMContentLoaded', function () {

    /* =================================================================
       1. MOBILE HAMBURGER MENU TOGGLE
       ================================================================= */

    /* Find the hamburger button and navigation element by their IDs */
    var hamburgerBtn = document.querySelector('#hamburger-btn');
    var mainNav = document.querySelector('#main-nav');

    /* Only set up the toggle if both elements exist on the page */
    if (hamburgerBtn && mainNav) {

        hamburgerBtn.addEventListener('click', function () {
            /*
             * classList.toggle() does two things in one call:
             * - If the element DOESN'T have the class, it ADDS it → returns true
             * - If the element DOES have the class, it REMOVES it → returns false
             *
             * .nav--open controls visibility of the mobile menu (see base.css)
             * .hamburger--active transforms the 3 lines into an X (see base.css)
             */
            var isOpen = mainNav.classList.toggle('nav--open');
            hamburgerBtn.classList.toggle('hamburger--active');

            /*
             * aria-expanded is an accessibility attribute that tells screen
             * readers whether the menu is currently open or closed.
             * We update it to match the actual state.
             */
            hamburgerBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    }

    /* =================================================================
       2. SMOOTH SCROLLING FOR ANCHOR LINKS
       ================================================================= */

    /*
     * querySelectorAll('a[href^="#"]') finds all <a> tags whose href
     * attribute starts with "#". These are "anchor links" that point to
     * a section on the same page (e.g., href="#featured-courses").
     *
     * The ^= is a CSS attribute selector meaning "starts with."
     */
    var anchorLinks = document.querySelectorAll('a[href^="#"]');

    /*
     * .forEach() loops through each element in the NodeList.
     * For each anchor link, we add a click event listener.
     */
    anchorLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {

            /* Get the href value, e.g., "#featured-courses" */
            var targetId = this.getAttribute('href');

            /* Skip if it's just "#" with nothing after it */
            if (targetId === '#') return;

            /* Try to find the element with that ID on the page */
            var targetElement = document.querySelector(targetId);

            if (targetElement) {
                /*
                 * event.preventDefault() stops the browser's default behavior.
                 * Normally, clicking an anchor link instantly jumps to the target.
                 * We prevent that so we can scroll smoothly instead.
                 */
                event.preventDefault();

                /*
                 * scrollIntoView() scrolls the page so the target element
                 * is visible in the viewport.
                 *
                 * behavior: 'smooth' — animate the scroll instead of jumping
                 * block: 'start' — align the top of the element with the top of the viewport
                 */
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

});
