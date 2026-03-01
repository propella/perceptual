const DATA_URL = 'data/exhibitions.json';

let exhibitions = [];
let activeTag = null;

async function init() {
    try {
        const response = await fetch(DATA_URL);
        const data = await response.json();
        exhibitions = data.exhibitions;

        renderTags();
        renderExhibitions();
        renderLastUpdated(data.lastUpdated);

        document.getElementById('sort-select').addEventListener('change', renderExhibitions);
    } catch (error) {
        console.error('Failed to load exhibitions:', error);
        document.getElementById('exhibitions').innerHTML =
            '<p>データの読み込みに失敗しました。</p>';
    }
}

function renderTags() {
    const allTags = new Set();
    exhibitions.forEach(e => {
        (e.tags || []).forEach(tag => allTags.add(tag));
    });

    const container = document.getElementById('filter-tags');

    const allButton = document.createElement('button');
    allButton.className = 'filter-tag active';
    allButton.textContent = 'すべて';
    allButton.addEventListener('click', () => {
        activeTag = null;
        updateActiveTag();
        renderExhibitions();
    });
    container.appendChild(allButton);

    allTags.forEach(tag => {
        const button = document.createElement('button');
        button.className = 'filter-tag';
        button.textContent = tag;
        button.addEventListener('click', () => {
            activeTag = tag;
            updateActiveTag();
            renderExhibitions();
        });
        container.appendChild(button);
    });
}

function updateActiveTag() {
    document.querySelectorAll('.filter-tag').forEach(btn => {
        if (activeTag === null && btn.textContent === 'すべて') {
            btn.classList.add('active');
        } else if (btn.textContent === activeTag) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function renderExhibitions() {
    const sortBy = document.getElementById('sort-select').value;

    let filtered = exhibitions;
    if (activeTag) {
        filtered = exhibitions.filter(e => (e.tags || []).includes(activeTag));
    }

    const sorted = [...filtered].sort((a, b) => {
        if (sortBy === 'title') {
            return a.title.localeCompare(b.title, 'ja');
        }
        return a[sortBy].localeCompare(b[sortBy]);
    });

    const container = document.getElementById('exhibitions');
    container.innerHTML = sorted.map(e => createCard(e)).join('');
}

function createCard(exhibition) {
    const imageHtml = exhibition.imageUrl
        ? `<img class="exhibition-image" src="${escapeHtml(exhibition.imageUrl)}" alt="" loading="lazy">`
        : '<div class="exhibition-image no-image">No Image</div>';

    const tagsHtml = (exhibition.tags || [])
        .map(tag => `<span class="exhibition-tag">${escapeHtml(tag)}</span>`)
        .join('');

    const startDate = formatDate(exhibition.startDate);
    const endDate = formatDate(exhibition.endDate);

    return `
        <article class="exhibition-card">
            <a href="${escapeHtml(exhibition.sourceUrl)}" target="_blank" rel="noopener">
                ${imageHtml}
                <div class="exhibition-content">
                    <h2 class="exhibition-title">${escapeHtml(exhibition.title)}</h2>
                    <p class="exhibition-venue">${escapeHtml(exhibition.venue)}</p>
                    <p class="exhibition-dates">${startDate} - ${endDate}</p>
                    ${tagsHtml ? `<div class="exhibition-tags">${tagsHtml}</div>` : ''}
                    <p class="exhibition-source">${escapeHtml(exhibition.source)}</p>
                </div>
            </a>
        </article>
    `;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
}

function renderLastUpdated(timestamp) {
    const date = new Date(timestamp);
    const formatted = date.toLocaleString('ja-JP');
    document.getElementById('last-updated').textContent = `最終更新: ${formatted}`;
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

init();
