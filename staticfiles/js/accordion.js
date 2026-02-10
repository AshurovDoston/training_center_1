/**
 * accordion.js — Collapsible module sections
 *
 * Used on the course detail page to show/hide lessons within each module.
 * Each module starts collapsed. Clicking the header smoothly reveals the lessons.
 *
 * HOW IT WORKS:
 * - Each module has a <button class="accordion-header"> and a <div class="accordion-panel">
 * - The panel's CSS sets max-height: 0 and overflow: hidden (collapsed)
 * - When the header is clicked, this script:
 *   1. Reads the panel's scrollHeight (the full height of its content)
 *   2. Sets max-height to that value (CSS transition makes it animate)
 *   3. Updates aria-expanded for screen readers
 *   4. Changes the icon text from + to −
 *
 * === KEY CONCEPTS ===
 *
 * element.scrollHeight:
 *   A read-only property that gives the total height of an element's content,
 *   INCLUDING content hidden by overflow: hidden. This lets us know how tall
 *   the panel would be if fully expanded.
 *
 * max-height + CSS transition:
 *   CSS can't animate height from 0 to "auto". But we CAN animate max-height
 *   from 0 to a specific pixel value. The CSS transition on .accordion-panel
 *   makes this change smooth (0.3s ease-in-out).
 *
 * aria-expanded:
 *   An accessibility attribute that tells screen readers whether a section
 *   is currently expanded or collapsed. "true" = open, "false" = closed.
 *
 * getAttribute() / setAttribute():
 *   Read or write any HTML attribute. Used here for aria-expanded and data-target.
 */

document.addEventListener('DOMContentLoaded', function () {

    /* Find all accordion header buttons on the page */
    var headers = document.querySelectorAll('.accordion-header');

    headers.forEach(function (header) {
        header.addEventListener('click', function () {

            /*
             * data-target contains the ID of the panel to toggle.
             * For example, data-target="module-1" → panel id="module-1"
             */
            var targetId = this.getAttribute('data-target');
            var panel = document.getElementById(targetId);

            if (!panel) return;

            /* Check if this panel is currently open */
            var isOpen = this.getAttribute('aria-expanded') === 'true';

            if (isOpen) {
                /* CLOSE the panel — set max-height back to 0 */
                panel.style.maxHeight = '0';
                this.setAttribute('aria-expanded', 'false');

                /* Change icon back to + */
                var icon = this.querySelector('.accordion-icon');
                if (icon) icon.textContent = '+';
            } else {
                /* OPEN the panel — set max-height to the full content height */
                panel.style.maxHeight = panel.scrollHeight + 'px';
                this.setAttribute('aria-expanded', 'true');

                /* Change icon to − (Unicode minus sign) */
                var icon = this.querySelector('.accordion-icon');
                if (icon) icon.textContent = '\u2212';
            }
        });
    });

});
