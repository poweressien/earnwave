/* EarnWave Main JavaScript */

// CSRF Token helper
function getCsrf() {
  const c = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return c ? c.trim().split('=')[1] : '';
}

// Toast notification
function showToast(title, message, type = 'info') {
  const container = document.getElementById('toastContainer') || (() => {
    const d = document.createElement('div');
    d.id = 'toastContainer'; d.className = 'ew-toast-container';
    document.body.appendChild(d); return d;
  })();
  const icons = {success:'✅', error:'❌', info:'ℹ️'};
  const toast = document.createElement('div');
  toast.className = `ew-toast ${type}`;
  toast.innerHTML = `<div class="ew-toast-icon">${icons[type]||'ℹ️'}</div><div><div class="ew-toast-title">${title}</div><div class="ew-toast-msg">${message}</div></div><button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--muted);margin-left:auto;cursor:pointer">×</button>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity='0'; toast.style.transform='translateX(100%)'; toast.style.transition='all .4s'; setTimeout(()=>toast.remove(),400); }, 4000);
}

// Points counter animation
function animateCount(el, target, duration = 1000) {
  const start = parseInt(el.textContent.replace(/,/g,'')) || 0;
  const step = (target - start) / (duration / 16);
  let current = start;
  const interval = setInterval(() => {
    current += step;
    if ((step > 0 && current >= target) || (step < 0 && current <= target)) {
      current = target; clearInterval(interval);
    }
    el.textContent = Math.round(current).toLocaleString();
  }, 16);
}

// Intersection observer for animate-on-scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.style.opacity = '1';
  });
}, {threshold: 0.1});
document.querySelectorAll('.animate-fade-up, .animate-fade-up-delay-1, .animate-fade-up-delay-2, .animate-fade-up-delay-3').forEach(el => observer.observe(el));

// Dark mode persistence
document.addEventListener('DOMContentLoaded', () => {
  const dm = localStorage.getItem('darkMode');
  if (dm === 'false') document.body.classList.add('light-mode');
});
