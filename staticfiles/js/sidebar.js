/**
 * sidebar.js — Toggleable lesson sidebar for mobile
 *
 * On desktop, the sidebar is always visible next to the lesson content.
 * On mobile, the sidebar is hidden off-screen to the left (via CSS transform).
 * This script adds a toggle button to show/hide it.
 *
 * HOW IT WORKS:
 * 1. User clicks the "Lessons" toggle button
 * 2. We add .sidebar--open to the sidebar (CSS slides it in with a transition)
 * 3. We show a dark backdrop overlay behind the sidebar
 * 4. User can close by: clicking X, clicking the backdrop, or pressing Escape
 *
 * === KEY CONCEPTS ===
 *
 * document.createElement(tagName):
 *   Creates a new HTML element in memory. It doesn't appear on the page
 *   until you add it with appendChild() or similar.
 *
 * document.body.appendChild(element):
 *   Adds the element as the last child of <body>, making it visible on the page.
 *
 * classList.add() / classList.remove():
 *   Add or remove CSS classes. Unlike classList.toggle(), these are explicit —
 *   add() always adds, remove() always removes.
 *
 * document.body.style.overflow:
 *   Controls whether the page is scrollable. Setting it to 'hidden' prevents
 *   scrolling (useful when a modal/sidebar is open). Setting it to '' (empty
 *   string) restores the default behavior.
 *
 * event.key:
 *   When a keyboard event fires, event.key tells you which key was pressed.
 *   Common values: 'Escape', 'Enter', 'Tab', 'ArrowDown', etc.
 */

document.addEventListener('DOMContentLoaded', function () {

    var sidebar = document.querySelector('#lesson-sidebar');
    var toggleBtn = document.querySelector('#sidebar-toggle');
    var closeBtn = document.querySelector('#sidebar-close');

    if (!sidebar || !toggleBtn) return;

    /*
     * Create the dark backdrop overlay with JavaScript.
     * We create it dynamically because it's only needed when JS is available.
     * If JS is disabled, the sidebar just stays in its CSS default position.
     */
    var backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);

    function openSidebar() {
        sidebar.classList.add('sidebar--open');
        backdrop.classList.add('sidebar-backdrop--visible');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('sidebar--open');
        backdrop.classList.remove('sidebar-backdrop--visible');
        document.body.style.overflow = '';
    }

    /* Open when the toggle button is clicked */
    toggleBtn.addEventListener('click', openSidebar);

    /* Close when the X button is clicked */
    if (closeBtn) {
        closeBtn.addEventListener('click', closeSidebar);
    }

    /* Close when clicking the dark backdrop (area outside the sidebar) */
    backdrop.addEventListener('click', closeSidebar);

    /*
     * Close when pressing the Escape key.
     * 'keydown' fires when any key is pressed down.
     * We check event.key === 'Escape' to only respond to the Escape key.
     * classList.contains() checks if the sidebar is currently open before closing.
     */
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && sidebar.classList.contains('sidebar--open')) {
            closeSidebar();
        }
    });

});
