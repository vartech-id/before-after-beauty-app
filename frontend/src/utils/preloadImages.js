const cache = new Set();

/**
 * Preload image URLs so navigation feels instant.
 * Uses a small cache to avoid re-fetching the same asset.
 * @param {string[]} urls
 */
export function preloadImages(urls = []) {
  urls.forEach((src) => {
    if (!src || cache.has(src)) return;

    const img = new Image();
    img.src = src;
    cache.add(src);
  });
}
