document.addEventListener('DOMContentLoaded', () => {
  const api = async (url, method='GET') => {
    const res = await fetch(url, { method });
    const data = await res.json();
    if (!data.success) throw new Error(data.error?.message || 'Unknown error');
    return data.data;
  };

  // Player controls
  document.getElementById('play-btn')?.addEventListener('click', () => api('/player/play','POST').catch(alert));
  document.getElementById('pause-btn')?.addEventListener('click', () => api('/player/pause','POST').catch(alert));
  document.getElementById('prev-btn')?.addEventListener('click', () => api('/player/previous','POST').catch(alert));
  document.getElementById('next-btn')?.addEventListener('click', () => api('/player/next','POST').catch(alert));

  // Search functionality
  const searchBtn = document.getElementById('search-btn');
  const searchInput = document.getElementById('search-input');

  // Add enter key support for search
  searchInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  });

  searchBtn?.addEventListener('click', performSearch);

  async function performSearch() {
    const q = document.getElementById('search-input').value;
    const type = document.getElementById('search-type').value;
    const resultsDiv = document.getElementById('search-results');

    if (!q.trim()) {
      resultsDiv.innerHTML = '<p class="text-red-400">Enter a search term.</p>';
      return;
    }

    resultsDiv.innerHTML = '<div class="flex items-center space-x-2"><div class="animate-spin rounded-full h-4 w-4 border-b-2 border-green-400"></div><span>Searching...</span></div>';

    try {
      const data = await api(`/search?q=${encodeURIComponent(q)}&type=${type}`);
      const items = type === 'track' ? data.tracks.items : data.artists.items;

      if (!items.length) {
        resultsDiv.innerHTML = '<p class="text-gray-400">No results found.</p>';
        return;
      }

      resultsDiv.innerHTML = items.map(item => {
        const imageUrl = type === 'artist' ?
          (item.images && item.images[0] ? item.images[0].url : '') :
          (item.album && item.album.images && item.album.images[0] ? item.album.images[0].url : '');

        const subtitle = type === 'track' ?
          (item.artists && item.artists[0] ? item.artists[0].name : 'Unknown Artist') :
          (item.genres && item.genres.length > 0 ? item.genres[0] : 'Artist');

        return `
          <div class="flex items-center space-x-3 bg-gray-700 hover:bg-gray-600 p-2 rounded transition-colors cursor-pointer">
            ${imageUrl ? 
              `<img src="${imageUrl}" alt="${item.name}" class="w-10 h-10 rounded object-cover" />` :
              `<div class="w-10 h-10 bg-gray-600 rounded flex items-center justify-center">
                <i class="fas fa-${type === 'artist' ? 'user' : 'music'} text-gray-400"></i>
              </div>`
            }
            <div class="flex-1 min-w-0">
              <p class="truncate font-medium">${item.name}</p>
              <p class="text-xs text-gray-400 truncate">${subtitle}</p>
            </div>
          </div>`;
      }).join('');
    } catch (err) {
      resultsDiv.innerHTML = `<p class="text-red-400">Error: ${err.message}</p>`;
    }
  }

  // Add smooth scrolling for show more/less functionality
  window.toggleShowMore = function(type) {
    const moreSection = document.getElementById(`more-${type}`);
    const button = document.getElementById(`show-more-${type}`);

    if (moreSection.classList.contains('hidden')) {
      moreSection.classList.remove('hidden');
      button.textContent = 'Show Less';
      // Smooth scroll to show the newly revealed content
      setTimeout(() => {
        moreSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 100);
    } else {
      moreSection.classList.add('hidden');
      // Update button text based on remaining count
      const remainingCount = moreSection.children.length;
      button.textContent = `Show More (${remainingCount} remaining)`;
    }
  };

  // Add loading state management for term changes
  window.changeTerm = function(term) {
    // Show loading state
    const buttons = document.querySelectorAll('.term-btn');
    buttons.forEach(btn => {
      btn.disabled = true;
      if (btn.onclick.toString().includes(term)) {
        btn.innerHTML = '<div class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>Loading...';
      }
    });

    // Update URL with new term parameter and reload
    const url = new URL(window.location);
    url.searchParams.set('term', term);
    window.location.href = url.toString();
  };

  // Add some visual feedback for player controls
  const playerButtons = ['play-btn', 'pause-btn', 'prev-btn', 'next-btn'];
  playerButtons.forEach(btnId => {
    const btn = document.getElementById(btnId);
    if (btn) {
      btn.addEventListener('click', function() {
        // Add visual feedback
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
          this.style.transform = 'scale(1)';
        }, 150);
      });
    }
  });
});