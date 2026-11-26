/**
 * Blog Engine JavaScript
 * Tree Archive Navigation, Multi-Filter State, Pagination,
 * Modal Reader with Zoomable GLightbox Images, and Collapsible Code Blocks
 */

(function () {
  'use strict';

  let allPosts = [];
  let filteredPosts = [];
  let currentPage = 1;
  const postsPerPage = 6;
  let currentActivePostIndex = -1;

  const selectedCategories = new Set();
  const selectedTags = new Set();
  let activeDateFilter = null; // { type: 'year', year } | { type: 'month', year, month }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function initBlog() {
    const dataEl = document.getElementById('blogPostsData');
    if (!dataEl) return;

    try {
      allPosts = JSON.parse(dataEl.textContent);
    } catch (e) {
      console.error('Failed to parse blogPostsData:', e);
      return;
    }

    applyFilters();

    const hash = window.location.hash.replace('#', '').trim();
    if (hash) {
      const targetPost = allPosts.find((p) => p.id === hash || p.slug === hash);
      if (targetPost) openPostModal(targetPost.id);
    }

    window.addEventListener('keydown', (e) => {
      const overlay = document.getElementById('blogReaderOverlay');
      if (!overlay || !overlay.classList.contains('active')) return;

      const isLightboxOpen = document.body.classList.contains('glightbox-open') ||
                             document.querySelector('.glightbox-container:not(.inactive)');
      if (isLightboxOpen) return;

      if (e.key === 'Escape') closePostModal();
      else if (e.key === 'ArrowLeft') navigatePost(-1);
      else if (e.key === 'ArrowRight') navigatePost(1);
    });

    const scrollContainer = document.getElementById('blogReaderScroll');
    if (scrollContainer) {
      scrollContainer.addEventListener('click', (e) => {
        if (e.target === scrollContainer) closePostModal();
      });

      scrollContainer.addEventListener('scroll', () => {
        const topBtn = document.getElementById('readerBackToTop');
        if (topBtn) topBtn.classList.toggle('visible', scrollContainer.scrollTop > 240);
      }, { passive: true });
    }

    // Delegated click handlers on grid cards (avoids inline onclick string quoting issues)
    const gridEl = document.getElementById('blogGrid');
    if (gridEl) {
      gridEl.addEventListener('click', (e) => {
        const catBadge = e.target.closest('.blog-category-badge[data-category]');
        if (catBadge) {
          e.stopPropagation();
          filterByCategory(catBadge.getAttribute('data-category'));
          return;
        }

        const tagPill = e.target.closest('.blog-tag-pill[data-tag]');
        if (tagPill) {
          e.stopPropagation();
          filterByTag(tagPill.getAttribute('data-tag'));
          return;
        }

        const openTrigger = e.target.closest('.blog-card-media, .blog-card-title');
        if (openTrigger) {
          const card = openTrigger.closest('.blog-card[data-post-id]');
          if (card) openPostModal(card.getAttribute('data-post-id'));
        }
      });
    }

    // Delegated click handlers inside reader modal tags
    const readerTags = document.getElementById('readerTags');
    if (readerTags) {
      readerTags.addEventListener('click', (e) => {
        const pill = e.target.closest('.blog-tag-pill[data-tag]');
        if (pill) filterByTagFromReader(pill.getAttribute('data-tag'));
      });
    }

    // Clear pointer/touch focus on reader buttons so they never stay highlighted after tap/click
    const readerControls = document.querySelector('#blogReaderOverlay .reader-bottom-controls');
    if (readerControls) {
      readerControls.addEventListener('pointerup', (e) => {
        const btn = e.target.closest('button');
        if (btn) setTimeout(() => btn.blur(), 0);
      });
    }
  }

  function renderGrid() {
    const gridEl = document.getElementById('blogGrid');
    if (!gridEl) return;

    if (filteredPosts.length === 0) {
      gridEl.innerHTML = `
        <div class="blog-empty-state">
          <h3>No posts found</h3>
          <p>No articles match your current tag, category, or archive filter.</p>
          <button type="button" class="btn btn-primary" onclick="resetBlogFilter()" style="margin-top: 16px;">View All Posts</button>
        </div>`;
      return;
    }

    const startIdx = (currentPage - 1) * postsPerPage;
    const pagePosts = filteredPosts.slice(startIdx, startIdx + postsPerPage);

    gridEl.innerHTML = pagePosts.map((post) => {
      const pCat = (post.category || '').toLowerCase();
      const isCatActive = selectedCategories.has(pCat) ? 'active' : '';
      const catEsc = escapeHtml(post.category || '');

      const tagsHtml = (post.tags || []).map((t) => {
        const tEsc = escapeHtml(t);
        const isTagActive = selectedTags.has(t.toLowerCase()) ? 'active' : '';
        return `<span class="blog-tag-pill ${isTagActive}" data-tag="${tEsc}" title="Filter by tag: ${tEsc}">${tEsc}</span>`;
      }).join('');

      return `
      <article class="blog-card" data-post-id="${escapeHtml(post.id)}">
        <div class="tile-circling-border" aria-hidden="true"></div>
        <div class="tile-inner blog-card-inner">
          <div class="blog-card-media">
            <img src="${escapeHtml(post.thumbnail)}" alt="${escapeHtml(post.title)}" class="blog-card-img" loading="lazy" decoding="async">
            <span class="blog-category-badge ${isCatActive}" data-category="${catEsc}" title="Filter by category: ${catEsc}">${catEsc}</span>
          </div>
          <div class="blog-card-body">
            <div class="blog-meta-strip">
              <span class="blog-date">${escapeHtml(post.date)}</span>
              <span class="blog-meta-dot">&bull;</span>
              <span class="blog-read-time">${escapeHtml(post.readTime || '5 min read')}</span>
            </div>
            <h2 class="blog-card-title">${escapeHtml(post.title)}</h2>
            <p class="blog-card-excerpt">${escapeHtml(post.subheading || '')}</p>
            <div class="blog-card-tags">${tagsHtml}</div>
          </div>
        </div>
      </article>`;
    }).join('');
  }

  function renderPagination() {
    const paginationEl = document.getElementById('blogPagination');
    if (!paginationEl) return;

    const totalPages = Math.ceil(filteredPosts.length / postsPerPage) || 1;
    if (totalPages <= 1) {
      paginationEl.style.display = 'none';
      return;
    }
    paginationEl.style.display = 'flex';

    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    const numbersWrap = document.getElementById('pageNumbers');

    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage === totalPages;

    if (numbersWrap) {
      let numHtml = '';
      for (let i = 1; i <= totalPages; i++) {
        numHtml += `<button type="button" class="page-number-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
      }
      numbersWrap.innerHTML = numHtml;
    }
  }

  function scrollToGridTop() {
    const target = document.getElementById('blogGrid');
    if (target) {
      const y = target.getBoundingClientRect().top + window.scrollY - 90;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  }

  window.changePage = function (delta) {
    const totalPages = Math.ceil(filteredPosts.length / postsPerPage) || 1;
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
      goToPage(newPage);
    }
  };

  window.goToPage = function (pageNum) {
    currentPage = pageNum;
    renderGrid();
    renderPagination();
    scrollToGridTop();
  };

  function applyFilters() {
    filteredPosts = allPosts.filter((post) => {
      if (activeDateFilter) {
        const postYear = String(post.year || (post.date ? post.date.split('-')[0] : ''));
        if (postYear !== String(activeDateFilter.year)) return false;
        if (activeDateFilter.type === 'month' && post.month_name !== activeDateFilter.month) return false;
      }

      if (selectedCategories.size > 0 && !selectedCategories.has((post.category || '').toLowerCase())) {
        return false;
      }

      if (selectedTags.size > 0) {
        const pTags = (post.tags || []).map((t) => t.toLowerCase());
        if (!pTags.some((t) => selectedTags.has(t))) return false;
      }

      return true;
    });

    currentPage = 1;
    renderGrid();
    renderPagination();
    updateFilterUI();
  }

  function updateFilterUI() {
    const isCatAll = selectedCategories.size === 0;
    const isTagAll = selectedTags.size === 0;
    const isDateAll = !activeDateFilter;

    document.querySelectorAll('.category-filter-pill').forEach((btn) => {
      const val = (btn.dataset.category || btn.textContent).trim().toLowerCase();
      btn.classList.toggle('active', val === 'all' ? isCatAll : selectedCategories.has(val));
    });

    document.querySelectorAll('.tag-filter-pill').forEach((btn) => {
      const val = (btn.dataset.tag || btn.textContent).trim().toLowerCase();
      btn.classList.toggle('active', val === 'all' ? isTagAll : selectedTags.has(val));
    });

    document.querySelectorAll('.date-filter-pill').forEach((btn) => {
      btn.classList.toggle('active', isDateAll);
    });

    document.querySelectorAll('.blog-card').forEach((card) => {
      const catBadge = card.querySelector('.blog-category-badge');
      if (catBadge) {
        catBadge.classList.toggle('active', selectedCategories.has(catBadge.textContent.trim().toLowerCase()));
      }
      card.querySelectorAll('.blog-tag-pill').forEach((tagEl) => {
        tagEl.classList.toggle('active', selectedTags.has(tagEl.textContent.trim().toLowerCase()));
      });
    });
  }

  function clearActiveTreeSelection() {
    document.querySelectorAll('.tree-month').forEach((el) => el.classList.remove('active'));
    document.querySelectorAll('.tree-year').forEach((el) => el.classList.remove('active-year'));
  }

  window.toggleTreeNode = function (nodeEl, year) {
    const item = nodeEl ? (nodeEl.classList.contains('tree-item') ? nodeEl : nodeEl.closest('.tree-item')) : null;
    const yearStr = String(year);

    if (activeDateFilter && activeDateFilter.type === 'year' && activeDateFilter.year === yearStr) {
      if (item) item.classList.remove('open');
      clearActiveTreeSelection();
      activeDateFilter = null;
    } else {
      if (item) item.classList.add('open');
      clearActiveTreeSelection();
      if (item) item.classList.add('active-year');
      activeDateFilter = { type: 'year', year: yearStr };
    }
    applyFilters();
  };

  window.filterByTree = function () {
    clearActiveTreeSelection();
    activeDateFilter = null;
    applyFilters();
  };

  window.filterByMonth = function (year, monthName) {
    const yearStr = String(year);
    if (activeDateFilter && activeDateFilter.type === 'month' && activeDateFilter.year === yearStr && activeDateFilter.month === monthName) {
      clearActiveTreeSelection();
      activeDateFilter = null;
    } else {
      clearActiveTreeSelection();
      const monthEl = document.querySelector(`.tree-month[data-year="${yearStr}"][data-month="${monthName}"]`);
      if (monthEl) monthEl.classList.add('active');
      const yearItem = document.querySelector(`.tree-year[data-year="${yearStr}"]`);
      if (yearItem) yearItem.classList.add('open');
      activeDateFilter = { type: 'month', year: yearStr, month: monthName };
    }
    applyFilters();
  };

  function toggleFilterSet(set, rawVal, defaultVal) {
    const lower = (rawVal || defaultVal).trim().toLowerCase();
    if (lower === 'all') {
      set.clear();
    } else if (set.has(lower)) {
      set.delete(lower);
    } else {
      set.add(lower);
    }
    applyFilters();
    scrollToGridTop();
  }

  window.filterByCategory = (category) => toggleFilterSet(selectedCategories, category, 'all');
  window.filterByTag = (tagName) => toggleFilterSet(selectedTags, tagName, 'all');

  window.filterByTagFromReader = function (tagName) {
    closePostModal();
    const lower = (tagName || '').trim().toLowerCase();
    if (lower && !selectedTags.has(lower)) selectedTags.add(lower);
    applyFilters();
    scrollToGridTop();
  };

  window.resetBlogFilter = function () {
    selectedCategories.clear();
    selectedTags.clear();
    activeDateFilter = null;
    clearActiveTreeSelection();
    document.querySelectorAll('.tree-year').forEach((el) => el.classList.remove('open'));
    applyFilters();
    scrollToGridTop();
  };

  // --------------------------------------------------------------------------
  // Full Post Reader Modal
  // --------------------------------------------------------------------------
  window.openPostModal = function (postId) {
    const postIdx = allPosts.findIndex((p) => p.id === postId || p.slug === postId);
    if (postIdx === -1) return;

    currentActivePostIndex = postIdx;
    const post = allPosts[postIdx];
    const overlay = document.getElementById('blogReaderOverlay');
    if (!overlay) return;

    document.getElementById('readerTitle').textContent = post.title || '';
    document.getElementById('readerDate').textContent = post.date || '';
    document.getElementById('readerReadTime').textContent = post.readTime || '5 min read';
    document.getElementById('readerAuthor').textContent = post.author || 'Prasannakumar T Bhat';

    const tagsEl = document.getElementById('readerTags');
    if (tagsEl) {
      tagsEl.innerHTML = (post.tags || []).map((t) => {
        const tEsc = escapeHtml(t);
        return `<span class="blog-tag-pill" data-tag="${tEsc}" title="Filter by tag: ${tEsc}">${tEsc}</span>`;
      }).join('');
    }

    const heroWrap = document.getElementById('readerHeroWrap');
    const heroImg = document.getElementById('readerHeroImg');
    if (post.thumbnail && heroImg && heroWrap) {
      heroImg.src = post.thumbnail;
      heroImg.alt = post.title;
      heroWrap.style.display = 'block';
    } else if (heroWrap) {
      heroWrap.style.display = 'none';
    }

    const bodyEl = document.getElementById('readerBody');
    if (bodyEl) {
      bodyEl.innerHTML = post.rendered_html || '';
      if (window.Prism) window.Prism.highlightAllUnder(bodyEl);
    }

    setupPostImagesLightbox(post);
    updateReaderNavButtons();

    overlay.classList.add('active');
    overlay.setAttribute('aria-hidden', 'false');
    document.documentElement.classList.add('blog-reader-active');
    document.body.classList.add('blog-reader-active');
    window.location.hash = '#' + (post.slug || post.id);

    const scrollContainer = document.getElementById('blogReaderScroll');
    if (scrollContainer) scrollContainer.scrollTop = 0;

    const readerBackToTop = document.getElementById('readerBackToTop');
    if (readerBackToTop) readerBackToTop.classList.remove('visible');
  };

  window.scrollReaderToTop = function () {
    const scrollContainer = document.getElementById('blogReaderScroll');
    if (scrollContainer) scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
  };

  window.closePostModal = function () {
    const overlay = document.getElementById('blogReaderOverlay');
    if (overlay) {
      overlay.classList.remove('active');
      overlay.setAttribute('aria-hidden', 'true');
      document.documentElement.classList.remove('blog-reader-active');
      document.body.classList.remove('blog-reader-active');
    }
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, null, window.location.pathname + window.location.search);
    }
  };

  window.navigatePost = function (delta) {
    if (currentActivePostIndex === -1) return;
    const newIdx = currentActivePostIndex + delta;
    if (newIdx >= 0 && newIdx < allPosts.length) {
      openPostModal(allPosts[newIdx].id);
    }
  };

  function setupPostImagesLightbox(post) {
    const postImages = [];
    const heroImg = document.getElementById('readerHeroImg');
    const heroWrap = document.getElementById('readerHeroWrap');

    if (heroImg && heroWrap && heroWrap.style.display !== 'none' && heroImg.src) {
      postImages.push({ src: heroImg.src, caption: heroImg.alt || post.title || 'Cover image', el: heroImg });
    }

    document.querySelectorAll('#readerBody img').forEach((img, i) => {
      postImages.push({
        el: img,
        src: img.src,
        caption: img.alt || img.title || `${post.title} - Image ${i + 1}`
      });
    });

    postImages.forEach((item, idx) => {
      item.el.style.cursor = 'zoom-in';
      item.el.title = 'Click to open in zoomable lightbox';
      item.el.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (typeof window.openLightbox === 'function') {
          window.openLightbox(postImages, idx);
        }
      };
    });
  }

  function updateReaderNavButtons() {
    const navConfigs = [
      {
        targetIdx: currentActivePostIndex - 1,
        valid: currentActivePostIndex > 0,
        btnId: 'readerPrevBtn',
        titleId: 'readerPrevTitle',
        sideId: 'readerSidePrev',
        prefix: 'Previous: '
      },
      {
        targetIdx: currentActivePostIndex + 1,
        valid: currentActivePostIndex < allPosts.length - 1,
        btnId: 'readerNextBtn',
        titleId: 'readerNextTitle',
        sideId: 'readerSideNext',
        prefix: 'Next: '
      }
    ];

    navConfigs.forEach(({ targetIdx, valid, btnId, titleId, sideId, prefix }) => {
      const btn = document.getElementById(btnId);
      const titleEl = document.getElementById(titleId);
      const side = document.getElementById(sideId);
      const targetPost = valid ? allPosts[targetIdx] : null;

      if (btn) {
        btn.style.display = targetPost ? 'flex' : 'none';
        btn.disabled = !targetPost;
      }
      if (titleEl && targetPost) titleEl.textContent = targetPost.title;
      if (side) {
        side.classList.toggle('is-unavailable', !targetPost);
        side.disabled = !targetPost;
        if (targetPost) {
          side.title = prefix + targetPost.title;
          side.setAttribute('aria-label', prefix + targetPost.title);
        } else {
          const fallbackLabel = sideId === 'readerSidePrev' ? 'No previous post' : 'No next post';
          side.title = fallbackLabel;
          side.setAttribute('aria-label', fallbackLabel);
        }
      }
    });
  }

  window.toggleCodeBlock = function (btn) {
    const card = btn.closest('.code-block-card');
    if (!card) return;
    card.classList.toggle('is-collapsed');
    btn.textContent = card.classList.contains('is-collapsed') ? 'Expand' : 'Collapse';
  };

  window.copyCodeBlock = function (btn) {
    const card = btn.closest('.code-block-card');
    const codeEl = card && card.querySelector('pre code');
    if (!codeEl) return;

    const text = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const origText = btn.textContent;
      btn.textContent = 'Copied!';
      btn.classList.add('is-copied');
      setTimeout(() => {
        btn.textContent = origText;
        btn.classList.remove('is-copied');
      }, 2000);
    }).catch((err) => {
      console.error('Could not copy code:', err);
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBlog);
  } else {
    initBlog();
  }
})();
