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
     MOBILE NAV – SCRAPED PAGES (.main-nav)
  ============================================= */
  function initScrapedNav() {
    var toggle = document.querySelector('.nav-menu-toggle');
    var nav = document.querySelector('.main-nav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen);
      var spans = toggle.querySelectorAll('span');
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

    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        var spans = toggle.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    // Mark active link
    var path = window.location.pathname;
    nav.querySelectorAll('a').forEach(function (a) {
      if (a.getAttribute('href') && path.startsWith(a.getAttribute('href')) && a.getAttribute('href') !== '/') {
        a.classList.add('active');
      }
    });
  }

  /* =============================================
     THUMBNAIL GALLERY (modell-cards)
  ============================================= */
  function initThumbnailGalleries() {
    document.querySelectorAll('.modell-card').forEach(function (card) {
      var mainImg = card.querySelector('.modell-img-wrap img');
      var thumbs = card.querySelectorAll('.modell-thumb');
      if (!mainImg || !thumbs.length) return;

      thumbs.forEach(function (thumb, i) {
        thumb.addEventListener('click', function () {
          var src = thumb.querySelector('img').src;
          var dataSrc = thumb.querySelector('img').dataset.src || src;
          mainImg.src = dataSrc || src;
          mainImg.dataset.lightboxSrc = dataSrc || src;
          thumbs.forEach(function (t) { t.classList.remove('active'); });
          thumb.classList.add('active');
        });
      });
    });
  }

  /* =============================================
     LIGHTBOX
  ============================================= */
  function initLightbox() {
    // Create overlay once
    var overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = '<button class="lightbox-close" aria-label="Schließen">&times;</button>' +
      '<button class="lightbox-prev" aria-label="Zurück">&#8249;</button>' +
      '<img src="" alt="Vergrößert">' +
      '<button class="lightbox-next" aria-label="Weiter">&#8250;</button>';
    document.body.appendChild(overlay);

    var overlayImg = overlay.querySelector('img');
    var closeBtn = overlay.querySelector('.lightbox-close');
    var prevBtn = overlay.querySelector('.lightbox-prev');
    var nextBtn = overlay.querySelector('.lightbox-next');
    var currentImages = [];
    var currentIndex = 0;

    function openLightbox(imgs, index) {
      currentImages = imgs;
      currentIndex = index;
      showImage(currentIndex);
      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
      prevBtn.style.display = imgs.length > 1 ? '' : 'none';
      nextBtn.style.display = imgs.length > 1 ? '' : 'none';
    }

    function showImage(i) {
      overlayImg.src = currentImages[i];
    }

    function closeLightbox() {
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    }

    closeBtn.addEventListener('click', closeLightbox);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeLightbox();
    });

    prevBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
      showImage(currentIndex);
    });

    nextBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      currentIndex = (currentIndex + 1) % currentImages.length;
      showImage(currentIndex);
    });

    document.addEventListener('keydown', function (e) {
      if (!overlay.classList.contains('active')) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowLeft') { currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length; showImage(currentIndex); }
      if (e.key === 'ArrowRight') { currentIndex = (currentIndex + 1) % currentImages.length; showImage(currentIndex); }
    });

    // Bind to product-img-wrap (knife/forged/zayiko pages)
    document.querySelectorAll('.product-img-wrap').forEach(function (wrap) {
      wrap.addEventListener('click', function () {
        var img = wrap.querySelector('img');
        var src = img.dataset.src || img.src;
        if (src && !src.includes('placeholder')) {
          // Collect all images in the same product-grid
          var grid = wrap.closest('.product-grid') || document.body;
          var imgs = Array.from(grid.querySelectorAll('.product-img-wrap img')).map(function (i) {
            return i.dataset.src || i.src;
          }).filter(function (s) { return !s.includes('placeholder'); });
          var index = imgs.indexOf(src);
          openLightbox(imgs, index < 0 ? 0 : index);
        }
      });
    });

    // Bind to produkt-img (Forged pages)
    document.querySelectorAll('.produkt-img').forEach(function (pimg) {
      pimg.style.cursor = 'zoom-in';
      pimg.addEventListener('click', function (e) {
        e.stopPropagation();
        // Get real URL: data-src if not yet lazy-loaded, otherwise current src
        var src = pimg.getAttribute('data-src') || pimg.getAttribute('src') || '';
        // Strip protocol+host so all URLs compare consistently
        src = src.replace(/^https?:\/\/[^\/]+/, '');
        if (!src || src.indexOf('placeholder') !== -1) return;

        // Collect all sibling produkt-img sources from the same grid
        var grid = pimg.parentNode;
        while (grid && !grid.classList.contains('produkte-grid')) {
          grid = grid.parentNode;
        }
        var siblings = grid ? grid.querySelectorAll('.produkt-img') : [pimg];
        var imgs = [];
        for (var i = 0; i < siblings.length; i++) {
          var s = siblings[i].getAttribute('data-src') || siblings[i].getAttribute('src') || '';
          s = s.replace(/^https?:\/\/[^\/]+/, '');
          if (s && s.indexOf('placeholder') === -1) imgs.push(s);
        }
        if (!imgs.length) imgs = [src];
        var idx = imgs.indexOf(src);
        openLightbox(imgs, idx < 0 ? 0 : idx);
      });
    });

    // Bind to modell-img-wrap (kamado joe pages)
    document.querySelectorAll('.modell-img-wrap').forEach(function (wrap) {
      wrap.addEventListener('click', function () {
        var img = wrap.querySelector('img');
        var src = img.dataset.lightboxSrc || img.dataset.src || img.src;
        // Collect all thumbs of this card
        var card = wrap.closest('.modell-card');
        var imgs = [];
        if (card) {
          card.querySelectorAll('.modell-thumb img').forEach(function (t) {
            imgs.push(t.dataset.src || t.src);
          });
        }
        if (!imgs.length) imgs = [src];
        openLightbox(imgs, 0);
      });
    });
  }

  /* =============================================
     SUCHE
  ============================================= */
  function initSearch() {
    var index = window.FK_SEARCH_INDEX || [];

    // Always inject search button – independent of whether index loaded
    var navEnd = document.querySelector('.nav-end');
    if (navEnd) {
      var btn = document.createElement('button');
      btn.className = 'nav-search-btn';
      btn.setAttribute('aria-label', 'Suche öffnen');
      btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
      navEnd.insertBefore(btn, navEnd.firstChild);
      btn.addEventListener('click', openSearch);
    }

    // Build modal
    var modal = document.createElement('div');
    modal.className = 'search-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-label', 'Suche');
    modal.innerHTML =
      '<div class="search-box">' +
        '<input class="search-input" type="search" placeholder="Suchen …" autocomplete="off" spellcheck="false">' +
        '<button class="search-clear-btn" aria-label="Eingabe löschen">&times;</button>' +
      '</div>' +
      '<div class="search-results" hidden></div>' +
      '<p class="search-hint">↑ ↓ navigieren &nbsp;·&nbsp; Enter öffnen &nbsp;·&nbsp; Esc schließen</p>';
    document.body.appendChild(modal);

    var input      = modal.querySelector('.search-input');
    var clearBtn   = modal.querySelector('.search-clear-btn');
    var resultsBox = modal.querySelector('.search-results');
    var activeIdx  = -1;
    var lastResults = [];

    function openSearch() {
      modal.classList.add('open');
      setTimeout(function () { input.focus(); }, 50);
    }
    function closeSearch() {
      modal.classList.remove('open');
      input.value = '';
      clearBtn.classList.remove('visible');
      resultsBox.hidden = true;
      resultsBox.innerHTML = '';
      activeIdx = -1;
      lastResults = [];
    }

    // Close on backdrop click
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeSearch();
    });

    // Keyboard: Escape / arrows
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.classList.contains('open')) { closeSearch(); return; }
      if (!modal.classList.contains('open')) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActive(Math.min(activeIdx + 1, lastResults.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActive(Math.max(activeIdx - 1, 0));
      } else if (e.key === 'Enter' && activeIdx >= 0 && lastResults[activeIdx]) {
        e.preventDefault();
        window.location.href = lastResults[activeIdx].url;
      }
    });

    // Global shortcut: / or Ctrl+K
    document.addEventListener('keydown', function (e) {
      if (modal.classList.contains('open')) return;
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
    });

    function setActive(i) {
      activeIdx = i;
      var items = resultsBox.querySelectorAll('.search-result-item');
      items.forEach(function (el, idx) {
        el.classList.toggle('active', idx === i);
      });
    }

    function search(q) {
      q = q.trim().toLowerCase();
      if (q.length < 2) {
        resultsBox.hidden = true;
        lastResults = [];
        return;
      }
      var terms = q.split(/\s+/);
      var scored = [];
      index.forEach(function (item) {
        var haystack = (item.title + ' ' + item.tags + ' ' + item.category).toLowerCase();
        var score = 0;
        terms.forEach(function (t) {
          if (item.title.toLowerCase().includes(t)) score += 3;
          else if (item.category.toLowerCase().includes(t)) score += 2;
          else if (haystack.includes(t)) score += 1;
        });
        if (score > 0) scored.push({ item: item, score: score });
      });
      scored.sort(function (a, b) { return b.score - a.score; });
      lastResults = scored.slice(0, 8).map(function (s) { return s.item; });
      renderResults(lastResults);
    }

    function renderResults(items) {
      activeIdx = -1;
      if (!items.length) {
        resultsBox.innerHTML = '<p class="search-no-results">Keine Ergebnisse gefunden.</p>';
        resultsBox.hidden = false;
        return;
      }
      resultsBox.innerHTML = items.map(function (item) {
        return '<a class="search-result-item" href="' + item.url + '">' +
          '<div class="search-result-category">' + item.category + '</div>' +
          '<div class="search-result-title">' + item.title + '</div>' +
          '</a>';
      }).join('');
      resultsBox.hidden = false;
    }

    input.addEventListener('input', function () {
      var q = input.value;
      clearBtn.classList.toggle('visible', q.length > 0);
      search(q);
    });

    clearBtn.addEventListener('click', function () {
      input.value = '';
      clearBtn.classList.remove('visible');
      resultsBox.hidden = true;
      lastResults = [];
      input.focus();
    });
  }

  /* =============================================
     INIT
  ============================================= */
  document.addEventListener('DOMContentLoaded', function () {
    initCookieBanner();
    initNavigation();
    initScrapedNav();
    initFAQ();
    initStickyNav();
    initContactForm();
    initSmoothScroll();
    initLazyImages();
    initThumbnailGalleries();
    initLightbox();
    initSearch();
  });

}());
