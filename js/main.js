/* ============================================================
   FEUERHAUS KALINA – GRILLWELT
   main.js – Navigation, Cookie-Banner, FAQ, Formular
   ============================================================ */

(function () {
  'use strict';

  /* =============================================
     COOKIE BANNER
  ============================================= */
  const COOKIE_KEY = 'fk_consent';

  function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + '=' + value + ';expires=' + d.toUTCString() + ';path=/;SameSite=Lax';
  }

  function getCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  function initCookieBanner() {
    const banner = document.getElementById('cookie-banner');
    if (!banner) return;

    const consent = getCookie(COOKIE_KEY);
    if (!consent) {
      setTimeout(() => banner.classList.add('show'), 600);
    }

    const btnAccept = document.getElementById('cookie-accept');
    const btnDecline = document.getElementById('cookie-decline');

    if (btnAccept) {
      btnAccept.addEventListener('click', function () {
        setCookie(COOKIE_KEY, 'accepted', 365);
        banner.classList.remove('show');
        // Optionally load analytics here
      });
    }

    if (btnDecline) {
      btnDecline.addEventListener('click', function () {
        setCookie(COOKIE_KEY, 'declined', 30);
        banner.classList.remove('show');
      });
    }
  }

  /* =============================================
     MOBILE NAVIGATION
  ============================================= */
  function initNavigation() {
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (!toggle || !navLinks) return;

    toggle.addEventListener('click', function () {
      const isOpen = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen);
      // Animate burger → X
      const spans = toggle.querySelectorAll('span');
      if (isOpen) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        const spans = toggle.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    // Highlight active nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(function (a) {
      const href = a.getAttribute('href');
      if (href && currentPath.includes(href) && href !== '/') {
        a.classList.add('active');
      }
    });
  }

  /* =============================================
     FAQ ACCORDION
  ============================================= */
  function initFAQ() {
    document.querySelectorAll('.faq-item').forEach(function (item) {
      const btn = item.querySelector('.faq-question');
      if (!btn) return;

      btn.addEventListener('click', function () {
        const isOpen = item.classList.contains('open');
        // Close all
        document.querySelectorAll('.faq-item.open').forEach(function (i) {
          i.classList.remove('open');
        });
        // Open clicked (if was closed)
        if (!isOpen) item.classList.add('open');
      });
    });
  }

  /* =============================================
     STICKY NAV SHADOW
  ============================================= */
  function initStickyNav() {
    const nav = document.querySelector('.site-nav');
    if (!nav) return;
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        nav.style.boxShadow = '0 2px 16px rgba(0,0,0,.08)';
      } else {
        nav.style.boxShadow = '';
      }
    }, { passive: true });
  }

  /* =============================================
     CONTACT FORM – CLIENT SIDE
  ============================================= */
  function initContactForm() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearErrors();

      // Basic validation
      let valid = true;

      const name = form.querySelector('[name="name"]');
      const email = form.querySelector('[name="email"]');
      const message = form.querySelector('[name="message"]');
      const dsgvo = form.querySelector('[name="dsgvo"]');

      if (name && name.value.trim().length < 2) {
        showError(name, 'Bitte geben Sie Ihren Namen ein.');
        valid = false;
      }
      if (email && !isValidEmail(email.value)) {
        showError(email, 'Bitte geben Sie eine gültige E-Mail-Adresse ein.');
        valid = false;
      }
      if (message && message.value.trim().length < 10) {
        showError(message, 'Bitte schreiben Sie mindestens eine kurze Nachricht.');
        valid = false;
      }
      if (dsgvo && !dsgvo.checked) {
        showError(dsgvo, 'Bitte stimmen Sie der Datenschutzerklärung zu.');
        valid = false;
      }

      if (!valid) return;

      // Submit via AJAX
      const submitBtn = form.querySelector('.form-submit');
      const originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Wird gesendet ...';

      const data = new FormData(form);

      fetch(form.getAttribute('action'), {
        method: 'POST',
        body: data
      })
      .then(function (res) { return res.json(); })
      .then(function (res) {
        if (res.success) {
          form.reset();
          showFormSuccess('Vielen Dank! Ihre Nachricht wurde gesendet. Wir melden uns schnellstmöglich bei Ihnen.');
        } else {
          showFormError(res.message || 'Es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.');
        }
      })
      .catch(function () {
        showFormError('Verbindungsfehler. Bitte versuchen Sie es erneut oder rufen Sie uns direkt an.');
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      });
    });
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function showError(field, msg) {
    field.style.borderColor = '#c0392b';
    const err = document.createElement('span');
    err.className = 'form-error';
    err.textContent = msg;
    field.parentNode.appendChild(err);
  }

  function clearErrors() {
    document.querySelectorAll('.form-error').forEach(function (e) { e.remove(); });
    document.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(function (f) {
      f.style.borderColor = '';
    });
    const existing = document.querySelector('.form-success, .form-error-msg');
    if (existing) existing.remove();
  }

  function showFormSuccess(msg) {
    const el = document.createElement('div');
    el.className = 'form-success';
    el.textContent = msg;
    document.getElementById('contact-form').appendChild(el);
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function showFormError(msg) {
    const el = document.createElement('div');
    el.className = 'form-error-msg';
    el.textContent = msg;
    document.getElementById('contact-form').appendChild(el);
  }

  /* =============================================
     SMOOTH SCROLL für Anker-Links
  ============================================= */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          const navH = document.querySelector('.site-nav')?.offsetHeight || 80;
          const top = target.getBoundingClientRect().top + window.scrollY - navH - 16;
          window.scrollTo({ top, behavior: 'smooth' });
        }
      });
    });
  }

  /* =============================================
     LAZY LOADING IMAGES
  ============================================= */
  function initLazyImages() {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            observer.unobserve(img);
          }
        });
      }, { rootMargin: '200px' });

      document.querySelectorAll('img[data-src]').forEach(function (img) {
        observer.observe(img);
      });
    } else {
      // Fallback: load all
      document.querySelectorAll('img[data-src]').forEach(function (img) {
        img.src = img.dataset.src;
      });
    }
  }

  /* =============================================
     INIT
  ============================================= */
  document.addEventListener('DOMContentLoaded', function () {
    initCookieBanner();
    initNavigation();
    initFAQ();
    initStickyNav();
    initContactForm();
    initSmoothScroll();
    initLazyImages();
  });

}());
