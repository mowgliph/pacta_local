/**
 * Generates user avatar initials from the user's name
 * Looks for an element with id 'userAvatar' and updates it with the initials
 */
function generateUserAvatar() {
    const userName = document.body.getAttribute('data-username') || 'Usuario';
    const userAvatar = document.getElementById('userAvatar');
    
    if (userAvatar && userName) {
        const words = userName.split(' ');
        let initials = '';
        
        if (words.length >= 2) {
            initials = words[0].charAt(0) + words[1].charAt(0);
        } else if (words[0].length >= 2) {
            initials = words[0].charAt(0) + words[0].charAt(1);
        } else {
            initials = words[0].charAt(0);
        }
        
        userAvatar.textContent = initials.toUpperCase();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', generateUserAvatar);
