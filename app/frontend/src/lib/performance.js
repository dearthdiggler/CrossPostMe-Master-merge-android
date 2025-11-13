/**
 * Performance utilities for frontend optimization
 * Includes: lazy loading, image optimization, resource prefetching
 */

/**
 * Prefetch resources for faster subsequent navigation
 * @param {string} href - URL to prefetch
 */
export const prefetchLink = (href) => {
  if (typeof window === 'undefined') return;
  
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = href;
  link.as = 'fetch';
  link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
};

/**
 * Preload critical resources
 * @param {string} href - URL to preload
 * @param {string} as - Resource type (script, style, image, font)
 */
export const preloadResource = (href, as = 'script') => {
  if (typeof window === 'undefined') return;
  
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = href;
  link.as = as;
  if (as === 'font') {
    link.crossOrigin = 'anonymous';
  }
  document.head.appendChild(link);
};

/**
 * Optimize image loading with lazy loading
 * @param {HTMLImageElement} img - Image element
 * @param {string} src - Image source URL
 */
export const optimizeImageLoading = (img, src) => {
  if (typeof window === 'undefined') return;
  
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading supported
    img.loading = 'lazy';
    img.src = src;
  } else {
    // Fallback with IntersectionObserver
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = src;
          observer.unobserve(img);
        }
      });
    });
    observer.observe(img);
  }
};

/**
 * Defer non-critical script execution
 * Executes callback after main thread is idle
 */
export const deferExecution = (callback, timeout = 2000) => {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    window.requestIdleCallback(callback);
  } else {
    setTimeout(callback, timeout);
  }
};

/**
 * Cache API responses in localStorage
 * @param {string} key - Cache key
 * @param {any} data - Data to cache
 * @param {number} ttl - Time to live in milliseconds
 */
export const cacheData = (key, data, ttl = 3600000) => {
  const cacheEntry = {
    data,
    timestamp: Date.now(),
    ttl,
  };
  try {
    localStorage.setItem(`cache_${key}`, JSON.stringify(cacheEntry));
  } catch (e) {
    console.warn('LocalStorage cache failed:', e);
  }
};

/**
 * Retrieve cached data
 * @param {string} key - Cache key
 * @returns {any|null} - Cached data or null if expired/missing
 */
export const getCachedData = (key) => {
  try {
    const cacheEntry = JSON.parse(localStorage.getItem(`cache_${key}`));
    if (!cacheEntry) return null;
    
    const isExpired = Date.now() - cacheEntry.timestamp > cacheEntry.ttl;
    if (isExpired) {
      localStorage.removeItem(`cache_${key}`);
      return null;
    }
    
    return cacheEntry.data;
  } catch (e) {
    console.warn('LocalStorage retrieval failed:', e);
    return null;
  }
};

/**
 * Monitor Web Vitals for performance tracking
 */
export const reportWebVitals = (metric) => {
  if (metric.name === 'CLS') {
    console.log('Cumulative Layout Shift:', metric.value);
  }
  if (metric.name === 'FID') {
    console.log('First Input Delay:', metric.value);
  }
  if (metric.name === 'LCP') {
    console.log('Largest Contentful Paint:', metric.value);
  }
  if (metric.name === 'FCP') {
    console.log('First Contentful Paint:', metric.value);
  }
  if (metric.name === 'TTFB') {
    console.log('Time to First Byte:', metric.value);
  }
};

/**
 * Optimize bundle size by lazy loading on route change
 */
export const prefetchRoute = (pathname) => {
  const routePrefetchMap = {
    '/pricing': () => import('../pages/Pricing'),
    '/company': () => import('../pages/Company'),
    '/marketplace/dashboard': () => import('../pages/Dashboard'),
    '/marketplace/my-ads': () => import('../pages/MyAds'),
  };
  
  if (routePrefetchMap[pathname]) {
    deferExecution(() => {
      routePrefetchMap[pathname]();
    }, 500);
  }
};
