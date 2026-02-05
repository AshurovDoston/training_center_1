/**
 * search.js — Real-time course search/filter
 *
 * Filters course cards on the course list page as the user types.
 * Everything happens in the browser — no server request needed.
 *
 * HOW IT WORKS:
 * 1. User types in the search input (#course-search)
 * 2. The 'input' event fires on every keystroke
 * 3. We loop through all .course-card elements
 * 4. Each card has data-title and data-instructor attributes (set in the template)
 * 5. If the search text is found in either attribute, the card stays visible
 * 6. Otherwise, we add .course-card--hidden to hide it
 * 7. If ALL cards are hidden, we show a "no results" message
 *
 * === KEY CONCEPTS ===
 *
 * 'input' event:
 *   Fires every time the input value changes — on typing, deleting, or pasting.
 *   Better than 'keyup' because it also catches paste from right-click menu.
 *
 * element.dataset:
 *   JavaScript way to read data-* attributes from HTML.
 *   <div data-title="hello"> → element.dataset.title returns "hello"
 *
 * string.includes(substring):
 *   Returns true if the string contains the substring, false otherwise.
 *   "hello world".includes("world") → true
 *
 * classList.add() / classList.remove():
 *   Add or remove a CSS class from an element without affecting other classes.
 */

document.addEventListener('DOMContentLoaded', function () {

    /* Find the search input, course grid, and no-results message */
    var searchInput = document.querySelector('#course-search');
    var courseGrid = document.querySelector('#course-grid');
    var noResultsMessage = document.querySelector('#search-no-results');

    /* Only run if the search input and course grid exist on this page */
    if (!searchInput || !courseGrid) return;

    /* Get all course cards once — they don't change after page load */
    var courseCards = courseGrid.querySelectorAll('.course-card');

    searchInput.addEventListener('input', function () {

        /*
         * Convert search text to lowercase so the comparison is case-insensitive.
         * .trim() removes whitespace from both ends (e.g., "  hello  " → "hello").
         */
        var searchText = this.value.toLowerCase().trim();

        /* Track how many cards are still visible */
        var visibleCount = 0;

        courseCards.forEach(function (card) {

            /*
             * Read the data-title and data-instructor attributes.
             * These were set to lowercase in the Django template using |lower.
             */
            var title = card.dataset.title || '';
            var instructor = card.dataset.instructor || '';

            /* Check if search text appears in the title OR instructor name */
            var isMatch = title.includes(searchText) || instructor.includes(searchText);

            if (isMatch) {
                card.classList.remove('course-card--hidden');
                visibleCount++;
            } else {
                card.classList.add('course-card--hidden');
            }
        });

        /* Show or hide the "no results" message */
        if (noResultsMessage) {
            if (visibleCount === 0 && searchText !== '') {
                noResultsMessage.style.display = 'block';
            } else {
                noResultsMessage.style.display = 'none';
            }
        }
    });

});
