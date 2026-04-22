(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    /* ── 1. Mobile Nav Toggle ─────────────────────────────── */
    var toggle = document.querySelector('.menu-toggle');
    var nav    = document.querySelector('.main-nav');

    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      });

      // Close nav when clicking outside the header
      document.addEventListener('click', function (e) {
        if (!e.target.closest('.site-header') && !e.target.closest('.main-nav')) {
          nav.classList.remove('is-open');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.setAttribute('aria-label', 'Open menu');
        }
      });
    }

    /* ── 2. Dropdown Keyboard Accessibility ──────────────── */
    var dropdownTriggers = document.querySelectorAll('.has-dropdown > a');

    dropdownTriggers.forEach(function (trigger) {
      trigger.addEventListener('keydown', function (e) {
        var parent = trigger.closest('.has-dropdown');

        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          var isOpen = parent.classList.toggle('is-open');
          trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }

        if (e.key === 'Escape') {
          parent.classList.remove('is-open');
          trigger.setAttribute('aria-expanded', 'false');
          trigger.focus();
        }
      });
    });

    // Close open dropdowns when focus moves away from the whole nav
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        document.querySelectorAll('.has-dropdown.is-open').forEach(function (el) {
          el.classList.remove('is-open');
          var t = el.querySelector(':scope > a');
          if (t) t.setAttribute('aria-expanded', 'false');
        });
      }
    });

    /* ── 3. Skip Link Focus Management ───────────────────── */
    var skipLink = document.querySelector('.skip-link');
    var mainContent = document.getElementById('main-content');

    if (skipLink && mainContent) {
      skipLink.addEventListener('click', function (e) {
        e.preventDefault();
        mainContent.setAttribute('tabindex', '-1');
        mainContent.focus();
      });
    }

    /* ── 3b. Scroll Fade-Up (IntersectionObserver) ───────── */
    var reduceMotion = window.matchMedia &&
                       window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var fadeTargets = document.querySelectorAll('.fade-up');

    if (fadeTargets.length && !reduceMotion && 'IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

      fadeTargets.forEach(function (el) { observer.observe(el); });
    } else {
      // Reveal immediately if observer unavailable or motion reduced
      fadeTargets.forEach(function (el) { el.classList.add('is-visible'); });
    }

    /* ── 3c. Phone Input Formatter ───────────────────────── */
    var phoneInput = document.querySelector('input[type="tel"]');
    if (phoneInput) {
      phoneInput.addEventListener('input', function () {
        var digits = phoneInput.value.replace(/\D/g, '').slice(0, 10);
        var formatted = digits;
        if (digits.length > 6) {
          formatted = '(' + digits.slice(0, 3) + ') ' + digits.slice(3, 6) + '-' + digits.slice(6);
        } else if (digits.length > 3) {
          formatted = '(' + digits.slice(0, 3) + ') ' + digits.slice(3);
        } else if (digits.length > 0) {
          formatted = '(' + digits;
        }
        phoneInput.value = formatted;
      });
    }

    /* ── 4. Contact Form Validation ──────────────────────── */
    var form = document.getElementById('contact-form');
    if (!form) return;

    var submitting = false;

    function showError(input, show) {
      var errorEl = document.getElementById(input.id + '-error');
      if (show) {
        input.classList.add('is-error');
        if (errorEl) errorEl.classList.add('visible');
      } else {
        input.classList.remove('is-error');
        if (errorEl) errorEl.classList.remove('visible');
      }
    }

    function validateField(input) {
      var val = input.value.trim();

      // Honeypot — never validate, keep invisible
      if (input.name === 'honeypot-field') return true;

      // Required check
      if (input.required && val === '') {
        showError(input, true);
        return false;
      }

      // Email format
      if (input.type === 'email' && val !== '') {
        var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRe.test(val)) { showError(input, true); return false; }
      }

      // Phone format (at least 10 digits-ish)
      if (input.type === 'tel' && val !== '') {
        var phoneRe = /^[\d\s\(\)\-\+\.]{10,}$/;
        if (!phoneRe.test(val)) { showError(input, true); return false; }
      }

      showError(input, false);
      return true;
    }

    // Inline validation on blur
    form.querySelectorAll('input, select, textarea').forEach(function (input) {
      input.addEventListener('blur', function () { validateField(input); });
      input.addEventListener('input', function () {
        if (input.classList.contains('is-error')) validateField(input);
      });
    });

    // Submit handler
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (submitting) return;

      // Honeypot check — silently discard if filled
      var honeypot = form.querySelector('[name="honeypot-field"]');
      if (honeypot && honeypot.value.trim() !== '') return;

      // Validate all required fields
      var fields = form.querySelectorAll('input[required], select[required], textarea[required]');
      var allValid = true;
      fields.forEach(function (f) { if (!validateField(f)) allValid = false; });
      if (!allValid) {
        // Focus first error field
        var firstError = form.querySelector('.is-error');
        if (firstError) firstError.focus();
        return;
      }

      // Loading state
      submitting = true;
      var btn = form.querySelector('[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Sending…';
      }

      // Demo: show success message after a short delay (no real endpoint)
      setTimeout(function () {
        form.innerHTML = '<p class="form-success">✓ Thank you! We\'ll be in touch within 1 business day. For urgent needs, call <a href="tel:4097294822">(409) 729-4822</a>.</p>';
      }, 1200);
    });

  });

}());
