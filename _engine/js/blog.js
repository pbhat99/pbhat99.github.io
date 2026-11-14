/**
 * Blog Engine JavaScript
 * Tree Navigation, 3-Tile Grid Filtering, Clickable Tags & Categories,
 * Pagination, Full Post Reader Modal with 100% Zoomable Image Lightbox,
 * Fixed Landscape Flank Preview Tiles, and Collapsible Code Blocks
 */

(function () {
  'use strict';

  let allPosts = [];
  let filteredPosts = [];
  let currentPage = 1;
  const postsPerPage = 6;
  let currentActivePostIndex = -1;

  // Initialize Blog
  function initBlog() {
    const dataEl = document.getElementById('blogPostsData');
    if (!dataEl) return;

    try {
      allPosts = JSON.parse(dataEl.textContent);
    } catch (e) {
      console.error('Failed to parse blogPostsData:', e);
      return;
    }

    filteredPosts = [...allPosts];
    renderGrid();
    renderPagination();

    // Check URL Hash for deep link (e.g. #camera-projections-in-nuke)
    const hash = window.location.hash.replace('#', '').trim();
    if (hash) {
      const targetPost = allPosts.find(p => p.id === hash || p.slug === hash);
      if (targetPost) {
        openPostModal(targetPost.id);
      }
    }

    // Keyboard navigation
    window.addEventListener('keydown', function (e) {
      const overlay = document.getElementById('blogReaderOverlay');
      if (overlay && overlay.classList.contains('active')) {
        // If GLightbox is currently open, let GLightbox handle Escape and arrows
        const isLightboxOpen = document.body.classList.contains('glightbox-open') ||
                               document.querySelector('.glightbox-container:not(.inactive)');
        if (isLightboxOpen) return;

        if (e.key === 'Escape') {
          closePostModal();
        } else if (e.key === 'ArrowLeft') {
          navigatePost(-1);
        } else if (e.key === 'ArrowRight') {
          navigatePost(1);
        }
      }
    });

    // Close on overlay backdrop click & scroll listener for floating top button
    const overlay = document.getElementById('blogReaderOverlay');
    const scrollContainer = document.getElementById('blogReaderScroll');

    if (scrollContainer) {
      scrollContainer.addEventListener('click', function (e) {
        if (e.target === scrollContainer) {
          closePostModal();
        }
      });

      scrollContainer.addEventListener('scroll', function () {
        const topBtn = document.getElementById('readerBackToTop');
        if (topBtn) {
          if (scrollContainer.scrollTop > 240) {
            topBtn.classList.add('visible');
          } else {
            topBtn.classList.remove('visible');
          }
        }
      }, { passive: true });
    }
  }

  // Render Grid for Current Page
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

    let html = '';
    pagePosts.forEach(post => {
      const tagsHtml = (post.tags || []).slice(0, 3).map(t => 
        `<span class="blog-tag-pill" onclick="event.stopPropagation(); filterByTag('${escapeHtml(t)}');" title="Filter by tag: ${escapeHtml(t)}">${escapeHtml(t)}</span>`
      ).join('');
      
      html += `
      <article class="blog-card" data-post-id="${post.id}">
        <div class="tile-circling-border" aria-hidden="true"></div>
        <div class="tile-inner blog-card-inner">
          <div class="blog-card-media" onclick="openPostModal('${post.id}')">
            <img src="${post.thumbnail}" alt="${escapeHtml(post.title)}" class="blog-card-img" loading="lazy">
            <span class="blog-category-badge" onclick="event.stopPropagation(); filterByCategory('${escapeHtml(post.category)}');" title="Filter by category: ${escapeHtml(post.category)}">${escapeHtml(post.category)}</span>
          </div>
          <div class="blog-card-body">
            <div class="blog-meta-strip">
              <span class="blog-date">${post.date}</span>
              <span class="blog-meta-dot">&bull;</span>
              <span class="blog-read-time">${escapeHtml(post.readTime || '5 min read')}</span>
            </div>
            <h2 class="blog-card-title" onclick="openPostModal('${post.id}')">${escapeHtml(post.title)}</h2>
            <p class="blog-card-excerpt">${escapeHtml(post.subheading || '')}</p>
            <div class="blog-card-tags">
              ${tagsHtml}
            </div>
          </div>
          <div class="blog-card-footer">
            <button type="button" class="btn-blog-more" onclick="openPostModal('${post.id}')">
              <span>More...</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>
      </article>`;
    });

    gridEl.innerHTML = html;
  }

  // Render Pagination
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

    if (prevBtn) prevBtn.disabled = (currentPage === 1);
    if (nextBtn) nextBtn.disabled = (currentPage === totalPages);

    let numHtml = '';
    for (let i = 1; i <= totalPages; i++) {
      const activeClass = (i === currentPage) ? 'active' : '';
      numHtml += `<button type="button" class="page-number-btn ${activeClass}" onclick="goToPage(${i})">${i}</button>`;
    }
    if (numbersWrap) numbersWrap.innerHTML = numHtml;
  }

  // Pagination Handlers
  window.changePage = function (delta) {
    const totalPages = Math.ceil(filteredPosts.length / postsPerPage) || 1;
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
      currentPage = newPage;
      renderGrid();
      renderPagination();
      scrollToGridTop();
    }
  };

  window.goToPage = function (pageNum) {
    currentPage = pageNum;
    renderGrid();
    renderPagination();
    scrollToGridTop();
  };

  function scrollToGridTop() {
    const target = document.getElementById('blogGrid');
    if (target) {
      const yOffset = -90;
      const y = target.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  }

  // --------------------------------------------------------------------------
  // Tree, Category & Tag Filters
  // --------------------------------------------------------------------------
  window.toggleTreeNode = function (nodeEl, year) {
    const item = nodeEl.closest('.tree-item');
    if (item) {
      item.classList.toggle('open');
    }
  };

  window.filterByTree = function (type) {
    clearActiveTreeSelection();
    const allItem = document.querySelector('.tree-all');
    if (allItem) allItem.classList.add('active');

    filteredPosts = [...allPosts];
    currentPage = 1;
    renderGrid();
    renderPagination();
  };

  window.filterByYear = function (year) {
    clearActiveTreeSelection();
    const yearItem = document.querySelector(`.tree-year[data-year="${year}"]`);
    if (yearItem) yearItem.classList.add('active-year');

    filteredPosts = allPosts.filter(p => p.year === String(year) || p.date.startsWith(String(year)));
    currentPage = 1;
    renderGrid();
    renderPagination();
  };

  window.filterByMonth = function (year, monthName) {
    clearActiveTreeSelection();
    const monthEl = document.querySelector(`.tree-month[data-year="${year}"][data-month="${monthName}"]`);
    if (monthEl) monthEl.classList.add('active');

    filteredPosts = allPosts.filter(p => (p.year === String(year) || p.date.startsWith(String(year))) && p.month_name === monthName);
    currentPage = 1;
    renderGrid();
    renderPagination();
  };

  window.filterByCategory = function (category) {
    clearActiveTreeSelection();
    const catLower = (category || 'all').toLowerCase();

    // Highlight matching category pill in sidebar
    document.querySelectorAll('.filter-pill').forEach(btn => {
      const text = btn.textContent.trim().toLowerCase();
      if ((catLower === 'all' && text === 'all') || text === catLower) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    if (!category || catLower === 'all') {
      filteredPosts = [...allPosts];
    } else {
      filteredPosts = allPosts.filter(p => (p.category || '').toLowerCase() === catLower);
    }

    currentPage = 1;
    renderGrid();
    renderPagination();
    scrollToGridTop();
  };

  window.filterByTag = function (tagName) {
    if (!tagName) return;
    const tagLower = tagName.trim().toLowerCase();

    // Clear sidebar active highlights
    clearActiveTreeSelection();
    document.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));

    filteredPosts = allPosts.filter(p => 
      (p.tags || []).some(t => t.toLowerCase() === tagLower)
    );

    currentPage = 1;
    renderGrid();
    renderPagination();
    scrollToGridTop();
  };

  window.filterByCategoryFromReader = function (category) {
    closePostModal();
    filterByCategory(category);
  };

  window.filterByTagFromReader = function (tagName) {
    closePostModal();
    filterByTag(tagName);
  };

  window.resetBlogFilter = function () {
    clearActiveTreeSelection();
    const allItem = document.querySelector('.tree-all');
    if (allItem) allItem.classList.add('active');
    document.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));
    const firstPill = document.querySelector('.filter-pill');
    if (firstPill) firstPill.classList.add('active');

    filteredPosts = [...allPosts];
    currentPage = 1;
    renderGrid();
    renderPagination();
    scrollToGridTop();
  };

  function clearActiveTreeSelection() {
    document.querySelectorAll('.tree-all, .tree-month').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tree-year').forEach(el => el.classList.remove('active-year'));
  }

  // --------------------------------------------------------------------------
  // Full Post Reader Modal
  // --------------------------------------------------------------------------
  window.openPostModal = function (postId) {
    const postIdx = allPosts.findIndex(p => p.id === postId || p.slug === postId);
    if (postIdx === -1) return;

    currentActivePostIndex = postIdx;
    const post = allPosts[postIdx];

    const overlay = document.getElementById('blogReaderOverlay');
    if (!overlay) return;

    // Header Info
    const catEl = document.getElementById('readerCategory');
    if (catEl) {
      catEl.textContent = post.category || 'Article';
      catEl.onclick = function () {
        filterByCategoryFromReader(post.category || 'all');
      };
    }

    document.getElementById('readerTitle').textContent = post.title || '';
    document.getElementById('readerSubheading').textContent = post.subheading || '';
    document.getElementById('readerDate').textContent = post.date || '';
    document.getElementById('readerReadTime').textContent = post.readTime || '5 min read';
    document.getElementById('readerAuthor').textContent = post.author || 'Prasannakumar T Bhat';

    // Clickable Tag Pills in Reader Header
    const tagsEl = document.getElementById('readerTags');
    if (tagsEl) {
      tagsEl.innerHTML = (post.tags || []).map(t => 
        `<span class="blog-tag-pill" onclick="filterByTagFromReader('${escapeHtml(t)}')" title="Filter by tag: ${escapeHtml(t)}">${escapeHtml(t)}</span>`
      ).join('');
    }

    // Hero Image
    const heroWrap = document.getElementById('readerHeroWrap');
    const heroImg = document.getElementById('readerHeroImg');
    if (post.thumbnail && heroImg) {
      heroImg.src = post.thumbnail;
      heroImg.alt = post.title;
      heroWrap.style.display = 'block';
    } else if (heroWrap) {
      heroWrap.style.display = 'none';
    }

    // Body content
    const bodyEl = document.getElementById('readerBody');
    if (bodyEl) {
      bodyEl.innerHTML = post.rendered_html || '';
      // Trigger Prism highlighting on code elements
      if (window.Prism) {
        window.Prism.highlightAllUnder(bodyEl);
      }
    }

    // Attach 100% Zoomable Fullscreen Lightbox to ALL Images in Post
    setupPostImagesLightbox(post);

    // Update Bottom Prev/Next Buttons & Fixed Flank Tiles
    updateReaderNavButtons();

    // Show modal & set URL hash
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    window.location.hash = '#' + (post.slug || post.id);

    // Scroll reader container to top immediately
    const scrollContainer = document.getElementById('blogReaderScroll');
    if (scrollContainer) {
      scrollContainer.scrollTop = 0;
      scrollContainer.scrollTo({ top: 0, behavior: 'auto' });
    }

    const readerBackToTop = document.getElementById('readerBackToTop');
    if (readerBackToTop) readerBackToTop.classList.remove('visible');
  };

  window.scrollReaderToTop = function () {
    const scrollContainer = document.getElementById('blogReaderScroll');
    if (scrollContainer) {
      scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  window.closePostModal = function () {
    const overlay = document.getElementById('blogReaderOverlay');
    if (overlay) {
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    }
    // Remove hash without scrolling
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, null, window.location.pathname + window.location.search);
    }
  };

  window.navigatePost = function (delta) {
    if (currentActivePostIndex === -1) return;
    const newIdx = currentActivePostIndex + delta;
    if (newIdx >= 0 && newIdx < allPosts.length) {
      openPostModal(allPosts[newIdx].id);
      const scrollContainer = document.getElementById('blogReaderScroll');
      if (scrollContainer) {
        scrollContainer.scrollTop = 0;
        scrollContainer.scrollTo({ top: 0, behavior: 'auto' });
      }
    }
  };

  // --------------------------------------------------------------------------
  // Attach 100% Zoomable Fullscreen Lightbox to Post Images
  // --------------------------------------------------------------------------
  function setupPostImagesLightbox(post) {
    const postImages = [];

    // 1. Hero image
    const heroImg = document.getElementById('readerHeroImg');
    const heroWrap = document.getElementById('readerHeroWrap');
    if (heroImg && heroWrap && heroWrap.style.display !== 'none' && heroImg.src) {
      postImages.push({
        el: heroImg,
        src: heroImg.src,
        caption: heroImg.alt || post.title || 'Cover image'
      });
    }

    // 2. All images in markdown body
    const bodyImgs = document.querySelectorAll('#readerBody img');
    bodyImgs.forEach((img, i) => {
      postImages.push({
        el: img,
        src: img.src,
        caption: img.alt || img.title || (post.title + ' - Image ' + (i + 1))
      });
    });

    // Make each image clickable with zoom-in cursor
    postImages.forEach((item, idx) => {
      item.el.style.cursor = 'zoom-in';
      item.el.title = 'Click to open in zoomable lightbox';
      item.el.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (typeof window.openLightbox === 'function') {
          window.openLightbox(postImages.map(p => ({ src: p.src, caption: p.caption })), idx);
        } else if (typeof GLightbox !== 'undefined') {
          GLightbox({
            elements: postImages.map(p => ({ href: p.src, type: 'image', title: p.caption })),
            startAt: idx,
            zoomable: true,
            touchNavigation: true
          }).openAt(idx);
        }
      };
    });
  }

  // --------------------------------------------------------------------------
  // Update Bottom Nav Buttons & Fixed Flank Preview Tiles
  // --------------------------------------------------------------------------
  function updateReaderNavButtons() {
    const prevBtn = document.getElementById('readerPrevBtn');
    const nextBtn = document.getElementById('readerNextBtn');
    const prevTitle = document.getElementById('readerPrevTitle');
    const nextTitle = document.getElementById('readerNextTitle');

    // Bottom Footer Prev Button
    if (currentActivePostIndex > 0) {
      const prevPost = allPosts[currentActivePostIndex - 1];
      if (prevBtn) {
        prevBtn.style.display = 'flex';
        prevBtn.disabled = false;
      }
      if (prevTitle) prevTitle.textContent = prevPost.title;
    } else {
      if (prevBtn) {
        prevBtn.style.display = 'none';
        prevBtn.disabled = true;
      }
    }

    // Bottom Footer Next Button
    if (currentActivePostIndex < allPosts.length - 1) {
      const nextPost = allPosts[currentActivePostIndex + 1];
      if (nextBtn) {
        nextBtn.style.display = 'flex';
        nextBtn.disabled = false;
      }
      if (nextTitle) nextTitle.textContent = nextPost.title;
    } else {
      if (nextBtn) {
        nextBtn.style.display = 'none';
        nextBtn.disabled = true;
      }
    }
  }

  // --------------------------------------------------------------------------
  // Collapsible Code Blocks & Copy Button
  // --------------------------------------------------------------------------
  window.toggleCodeBlock = function (btn) {
    const card = btn.closest('.code-block-card');
    if (!card) return;
    card.classList.toggle('is-collapsed');
    btn.textContent = card.classList.contains('is-collapsed') ? 'Expand' : 'Collapse';
  };

  window.copyCodeBlock = function (btn) {
    const card = btn.closest('.code-block-card');
    if (!card) return;
    const codeEl = card.querySelector('pre code');
    if (!codeEl) return;

    const text = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const origText = btn.textContent;
      btn.textContent = 'Copied!';
      btn.style.color = 'var(--accent-primary)';
      setTimeout(() => {
        btn.textContent = origText;
        btn.style.color = '';
      }, 2000);
    }).catch(err => {
      console.error('Could not copy code:', err);
    });
  };

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBlog);
  } else {
    initBlog();
  }

})();
