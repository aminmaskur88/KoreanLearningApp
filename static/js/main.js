// Global Functions
function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ko-KR';
        utterance.rate = 0.8;
        window.speechSynthesis.speak(utterance);
    } else {
        showAlert('Info', 'Browser Anda tidak mendukung Text-to-Speech.');
    }
}

async function addXP(amount) {
    try {
        const response = await fetch('/api/update_xp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ xp: amount })
        });
        const result = await response.json();
        fetchUserStats();
        return result;
    } catch (error) {
        console.error('Error updating XP:', error);
    }
}

async function fetchUserStats() {
    try {
        const response = await fetch('/api/user');
        const user = await response.json();
        const streakEl = document.getElementById('streak-count');
        const xpEl = document.getElementById('xp-count');
        
        if (streakEl) streakEl.textContent = user.streak;
        if (xpEl) xpEl.textContent = user.xp;
        
        // Update dashboard elements if they exist
        const levelElement = document.getElementById('user-level');
        if (levelElement) {
            levelElement.textContent = `Level ${user.level}`;
            const xpProgress = document.getElementById('xp-progress-bar');
            if (xpProgress) {
                const progress = user.xp % 100;
                xpProgress.style.width = `${progress}%`;
            }
        }
    } catch (error) {
        console.error('Error fetching user stats:', error);
    }
}

function showAlert(title, message, callback) {
    const modal = document.getElementById('custom-modal');
    if (!modal) {
        alert(message);
        if (callback) callback();
        return;
    }
    const titleEl = document.getElementById('modal-title');
    const msgEl = document.getElementById('modal-message');
    const btn = document.getElementById('modal-action-btn');

    titleEl.textContent = title;
    msgEl.textContent = message;
    modal.style.display = 'flex';

    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    newBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        if (callback) callback();
    });
}

// SPA Navigation Function
async function navigateTo(url, push = true) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');
        
        // Update content
        const currentContent = document.getElementById('app-content');
        const newContent = newDoc.getElementById('app-content');
        if (currentContent && newContent) {
            currentContent.innerHTML = newContent.innerHTML;
        }
        
        // Update Page Title
        document.title = newDoc.title;
        
        // Update URL
        if (push) history.pushState({}, '', url);
        
        // Extract and run scripts
        // Important: We wrap scripts in a block or IIFE to avoid redeclaration errors
        const scripts = newDoc.body.querySelectorAll('script');
        scripts.forEach(oldScript => {
            if (oldScript.src && oldScript.src.includes('main.js')) return;
            
            const newScript = document.createElement('script');
            Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
            
            // Run inline scripts in global scope
            if (!oldScript.src) {
                newScript.appendChild(document.createTextNode(oldScript.innerHTML));
            }
            
            document.body.appendChild(newScript);
            newScript.parentNode.removeChild(newScript);
        });

        // Update active nav state
        document.querySelectorAll('.nav-item').forEach(item => {
            const href = item.getAttribute('href');
            const currentPath = window.location.pathname;
            if (currentPath === href) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        fetchUserStats();
        document.getElementById('custom-modal').style.display = 'none';
        window.scrollTo(0, 0);

    } catch (err) {
        console.error('Navigation failed:', err);
        window.location.href = url;
    }
}

// Initial Setup
document.addEventListener('DOMContentLoaded', () => {
    // Theme logic
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.replace('light-mode', 'dark-mode');
        themeToggle.querySelector('i').classList.replace('fa-moon', 'fa-sun');
    }

    themeToggle.addEventListener('click', () => {
        const icon = themeToggle.querySelector('i');
        if (body.classList.contains('light-mode')) {
            body.classList.replace('light-mode', 'dark-mode');
            icon.classList.replace('fa-moon', 'fa-sun');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.replace('dark-mode', 'light-mode');
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.setItem('theme', 'light');
        }
    });

    // Fullscreen logic
    const fsToggle = document.getElementById('fullscreen-toggle');
    
    function updateFSIcon() {
        const icon = fsToggle.querySelector('i');
        if (document.fullscreenElement) {
            icon.classList.replace('fa-expand', 'fa-compress');
        } else {
            icon.classList.replace('fa-compress', 'fa-expand');
        }
    }

    fsToggle.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error(`Error: ${err.message}`);
            });
            localStorage.setItem('fullscreen', 'true');
        } else {
            document.exitFullscreen();
            localStorage.setItem('fullscreen', 'false');
        }
    });

    document.addEventListener('fullscreenchange', updateFSIcon);

    // SPA Link Interception
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link && link.classList.contains('locked')) return; // Ignore locked links
        
        if (link && link.href && link.href.startsWith(window.location.origin)) {
            // Check if it's a normal link (not target="_blank", etc.)
            if (!link.getAttribute('target') || link.getAttribute('target') === '_self') {
                e.preventDefault();
                navigateTo(link.href);
            }
        }
    });

    window.addEventListener('popstate', () => {
        navigateTo(window.location.href, false);
    });

    // Re-enable FS on first click if preference is saved
    if (localStorage.getItem('fullscreen') === 'true') {
        const reEnableFS = () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(() => {});
            }
            window.removeEventListener('click', reEnableFS);
        };
        window.addEventListener('click', reEnableFS);
    }

    fetchUserStats();
});
