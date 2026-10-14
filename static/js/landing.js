/**
 * Grand Luxe Hotel ERP — Scroll-Driven Motion & Interactive Reveals
 * Features:
 * - Intersection Observer reveal pipeline
 * - Hero entrance staggering
 * - Dashboard preview scroll-scaling with smooth dampening
 * - Respects prefers-reduced-motion
 * - Zero external animation libraries
 */

(function () {
  'use strict';

  // Check if user prefers reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.addEventListener('DOMContentLoaded', () => {
    initHeroAnimations();
    initScrollRevealObserver();
    if (!prefersReducedMotion) {
      initPreviewScrollScale();
    }
  });

  /**
   * 1. Hero entrance sequence on page load
   */
  function initHeroAnimations() {
    const heroElements = document.querySelectorAll('.landing-hero .reveal-init');
    heroElements.forEach((el, index) => {
      setTimeout(() => {
        el.classList.add('reveal-visible');
      }, 100 + index * 140);
    });
  }

  /**
   * 2. IntersectionObserver for scroll-driven section storytelling
   */
  function initScrollRevealObserver() {
    const targets = document.querySelectorAll('.reveal-init:not(.landing-hero .reveal-init), .scale-reveal-init');

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      targets.forEach(el => {
        el.classList.add('reveal-visible');
        el.classList.add('scale-reveal-visible');
      });
      return;
    }

    const observerOptions = {
      root: null,
      rootMargin: '0px 0px -60px 0px',
      threshold: 0.12
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          if (entry.target.classList.contains('scale-reveal-init')) {
            entry.target.classList.add('scale-reveal-visible');
          } else {
            entry.target.classList.add('reveal-visible');
          }
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    targets.forEach(el => revealObserver.observe(el));
  }

  /**
   * 3. Subtle depth scaling of the dashboard preview relative to scroll position
   */
  function initPreviewScrollScale() {
    const preview = document.getElementById('preview-frame');
    if (!preview) return;

    let ticking = false;

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const rect = preview.getBoundingClientRect();
          const windowHeight = window.innerHeight;

          // Only compute when near or in viewport
          if (rect.top < windowHeight && rect.bottom > 0) {
            const progress = Math.min(Math.max((windowHeight - rect.top) / (windowHeight + rect.height * 0.5), 0), 1);
            const scale = 0.94 + 0.06 * progress;
            const translateY = (1 - progress) * 25;
            preview.style.transform = `scale(${scale.toFixed(3)}) translateY(${translateY.toFixed(1)}px)`;
            
            // Subtle 3D shadow depth calculation
            const shadowIntensity = 0.15 + 0.15 * progress;
            preview.style.boxShadow = `0 ${20 + 20 * progress}px ${60 + 20 * progress}px -10px rgba(145, 128, 232, ${shadowIntensity.toFixed(2)})`;
          }

          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

})();
