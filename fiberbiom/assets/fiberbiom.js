/**
 * Fiberbiom LP — FAQ smooth open/close animation
 * Uses native <details>/<summary> — this script only adds CSS transition on height.
 * Falls back gracefully if JS disabled (instant open/close).
 */
(function () {
  'use strict';

  const items = document.querySelectorAll('.fiberbiom-faq__item');
  if (!items.length) return;

  items.forEach(function (details) {
    const summary = details.querySelector('summary');
    const answer = details.querySelector('.fiberbiom-faq__answer');
    if (!summary || !answer) return;

    summary.addEventListener('click', function (e) {
      e.preventDefault();

      if (details.open) {
        // Closing
        answer.style.maxHeight = answer.scrollHeight + 'px';
        requestAnimationFrame(function () {
          answer.style.maxHeight = '0';
          answer.style.overflow = 'hidden';
        });
        answer.addEventListener('transitionend', function handler() {
          details.open = false;
          answer.style.maxHeight = '';
          answer.style.overflow = '';
          answer.removeEventListener('transitionend', handler);
        }, { once: true });
      } else {
        // Opening
        details.open = true;
        var height = answer.scrollHeight;
        answer.style.maxHeight = '0';
        answer.style.overflow = 'hidden';
        requestAnimationFrame(function () {
          answer.style.transition = 'max-height 0.25s ease';
          answer.style.maxHeight = height + 'px';
        });
        answer.addEventListener('transitionend', function handler() {
          answer.style.maxHeight = '';
          answer.style.overflow = '';
          answer.style.transition = '';
          answer.removeEventListener('transitionend', handler);
        }, { once: true });
      }
    });
  });
})();
