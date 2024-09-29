import { Ripple, initMDB } from "mdb-ui-kit";

initMDB({ Ripple });
// Navbar toggler for mobile view
const toggler = document.getElementById('navbar-toggler');
const navbarCollapse = document.getElementById('navbar-collapse');

toggler.addEventListener('click', function() {
    navbarCollapse.classList.toggle('show');
});

// Genre dropdown functionality
const genreDropdown = document.getElementById('genreDropdown');
const genreDropdownContent = document.getElementById('genreDropdownContent');

genreDropdown.addEventListener('click', function() {
    genreDropdownContent.style.display = genreDropdownContent.style.display === 'block' ? 'none' : 'block';
});

// Avatar dropdown functionality
const avatarDropdown = document.getElementById('avatarDropdown');
const avatarDropdownContent = document.getElementById('avatarDropdownContent');

avatarDropdown.addEventListener('click', function() {
    avatarDropdownContent.style.display = avatarDropdownContent.style.display === 'block' ? 'none' : 'block';
});

// Close dropdowns if clicked outside
window.onclick = function(event) {
    if (!event.target.matches('.nav-link')) {
        if (genreDropdownContent.style.display === 'block') {
            genreDropdownContent.style.display = 'none';
        }
        if (avatarDropdownContent.style.display === 'block') {
            avatarDropdownContent.style.display = 'none';
        }
    }
}