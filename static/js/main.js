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

  // Search
  const searchBtn = document.getElementById('search-btn');
  searchBtn?.addEventListener('click', async () => {
    const q = document.getElementById('search-input').value;
    const type = document.getElementById('search-type').value;
    const resultsDiv = document.getElementById('search-results');
    if (!q) {
      resultsDiv.innerHTML = '<p class="text-red-400">Enter a search term.</p>';
      return;
    }
    resultsDiv.innerHTML = '<p>Searching...</p>';
    try {
      const data = await api(`/search?q=${encodeURIComponent(q)}&type=${type}`);
      const items = type === 'track' ? data.tracks.items : data.artists.items;
      if (!items.length) {
        resultsDiv.innerHTML = '<p>No results found.</p>';
        return;
      }
      resultsDiv.innerHTML = items.map(item => `
        <div class="flex items-center space-x-3 bg-gray-700 p-2 rounded">
          <img src="${type==='artist' ? item.images[0]?.url : item.album.images[0]?.url}" class="w-10 h-10 rounded-full" />
          <span>${item.name}</span>
        </div>`).join('');
    } catch (err) {
      resultsDiv.innerHTML = `<p class="text-red-400">${err.message}</p>`;
    }
  });
});
