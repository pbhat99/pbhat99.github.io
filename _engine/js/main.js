import { initAllBeforeAfter } from './before-after.js';
import { initLightbox } from './lightbox.js';
import { initAccordions } from './accordion.js';
import { initAllMultiPass } from './multi-pass.js';

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Nav Toggle
  const mobileToggle = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const isOpen = navLinks.classList.contains('active');
      mobileToggle.setAttribute('aria-expanded', isOpen);
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Portfolio Tag Filtering
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');
  const companySections = document.querySelectorAll('.company-section');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');
      const companyFilter = btn.getAttribute('data-company');

      projectCards.forEach(card => {
        const category = card.getAttribute('data-category');
        const cardCompany = card.getAttribute('data-company');

        let match = false;
        if (companyFilter) {
          match = (cardCompany === companyFilter);
        } else if (filter === 'all' || category === filter) {
          match = true;
        }

        if (match) {
          card.style.display = 'flex';
          setTimeout(() => { card.style.opacity = '1'; }, 10);
        } else {
          card.style.opacity = '0';
          setTimeout(() => { card.style.display = 'none'; }, 200);
        }
      });

      // Update company sections visibility based on visible project cards
      setTimeout(() => {
        companySections.forEach(section => {
          const visibleCards = section.querySelectorAll('.project-card:not([style*="display: none"])');
          if (visibleCards.length === 0) {
            section.style.display = 'none';
          } else {
            section.style.display = 'block';
            section.style.opacity = '1';
          }
        });
      }, 220);
    });
  });

  // Showreel Timestamp Jumpers
  const reelBadges = document.querySelectorAll('.reel-time-badge');
  const reelIframe = document.querySelector('.hero-reel-card iframe');

  reelBadges.forEach(badge => {
    badge.addEventListener('click', () => {
      const seconds = badge.getAttribute('data-seconds');
      if (reelIframe && seconds) {
        // Post message to Vimeo player or jump URL
        const currentSrc = reelIframe.src.split('#')[0];
        reelIframe.src = `${currentSrc}#t=${seconds}s`;
      }
    });
  });

  // Initialize all interactive modules
  initAllBeforeAfter();
  initLightbox();
  initAccordions();
  initAllMultiPass();
});

