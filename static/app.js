const API = '/api';
let teamsCache = [];

// ── Navigation ────────────────────────────────────────────────────────

document.querySelectorAll('nav button').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        btn.classList.add('active');
        const section = document.getElementById(btn.dataset.section);
        section.classList.add('active');
        loadSection(btn.dataset.section);
    });
});

function loadSection(name) {
    switch (name) {
        case 'teams': loadTeams(); break;
        case 'players': loadPlayers(); break;
        case 'standings': loadStandings(); break;
        case 'matches': loadMatches(); break;
        case 'news': loadNews(); break;
    }
}

// ── Teams ─────────────────────────────────────────────────────────────

async function loadTeams() {
    const res = await fetch(`${API}/teams`);
    const teams = await res.json();
    teamsCache = teams;
    const grid = document.getElementById('teams-grid');
    if (!teams.length) {
        grid.innerHTML = '<div class="empty-state">No teams yet. Seed the database or add a team.</div>';
        return;
    }
    grid.innerHTML = teams.map(t => `
        <div class="team-card" onclick="viewTeam(${t.id})">
            <h3>${t.name}</h3>
            <div class="meta">
                <span>${t.city}</span>
                <span>${t.stadium}</span>
                <span>Founded: ${t.founded_year || 'N/A'}</span>
                <span>${t.league}</span>
            </div>
        </div>
    `).join('');
}

async function viewTeam(id) {
    const res = await fetch(`${API}/teams/${id}`);
    const team = await res.json();
    const modal = document.getElementById('team-detail-modal');
    document.getElementById('team-detail-content').innerHTML = `
        <h3>${team.name}</h3>
        <p><strong>City:</strong> ${team.city}</p>
        <p><strong>Stadium:</strong> ${team.stadium}</p>
        <p><strong>Founded:</strong> ${team.founded_year || 'N/A'}</p>
        <p><strong>League:</strong> ${team.league}</p>
        <h4 style="margin-top:1rem;margin-bottom:0.5rem;">Squad (${team.players.length} players)</h4>
        ${team.players.length ? `<table>
            <thead><tr><th>#</th><th>Name</th><th>Position</th><th>Nationality</th></tr></thead>
            <tbody>${team.players.map(p => `
                <tr>
                    <td>${p.jersey_number || '-'}</td>
                    <td>${p.full_name}</td>
                    <td><span class="badge badge-${posClass(p.position)}">${p.position || '-'}</span></td>
                    <td>${p.nationality || '-'}</td>
                </tr>
            `).join('')}</tbody>
        </table>` : '<p class="empty-state">No players registered</p>'}
    `;
    modal.classList.add('active');
}

function posClass(pos) {
    if (!pos) return 'mid';
    const p = pos.toLowerCase();
    if (p.includes('goal')) return 'gk';
    if (p.includes('def')) return 'def';
    if (p.includes('mid')) return 'mid';
    return 'fwd';
}

// ── Add Team Modal ────────────────────────────────────────────────────

function showAddTeam() {
    document.getElementById('add-team-modal').classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

async function submitTeam(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    if (data.founded_year) data.founded_year = parseInt(data.founded_year);
    await fetch(`${API}/teams`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    form.reset();
    closeModal('add-team-modal');
    loadTeams();
}

// ── Players ───────────────────────────────────────────────────────────

async function loadPlayers() {
    await ensureTeamsCache();
    populateTeamFilter();

    const params = new URLSearchParams();
    const teamFilter = document.getElementById('player-team-filter')?.value;
    const posFilter = document.getElementById('player-pos-filter')?.value;
    if (teamFilter) params.set('team_id', teamFilter);
    if (posFilter) params.set('position', posFilter);

    const res = await fetch(`${API}/players?${params}`);
    const players = await res.json();
    const tbody = document.getElementById('players-tbody');
    if (!players.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No players found</td></tr>';
        return;
    }
    tbody.innerHTML = players.map(p => `
        <tr>
            <td>${p.jersey_number || '-'}</td>
            <td><strong>${p.full_name}</strong></td>
            <td><span class="badge badge-${posClass(p.position)}">${p.position || '-'}</span></td>
            <td>${p.team_name || '-'}</td>
            <td>${p.nationality || '-'}</td>
            <td>${p.height_cm ? p.height_cm + ' cm' : '-'}</td>
        </tr>
    `).join('');
}

async function ensureTeamsCache() {
    if (!teamsCache.length) {
        const res = await fetch(`${API}/teams`);
        teamsCache = await res.json();
    }
}

function populateTeamFilter() {
    const sel = document.getElementById('player-team-filter');
    if (sel.options.length > 1) return;
    teamsCache.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = t.name;
        sel.appendChild(opt);
    });
    const addSel = document.getElementById('player-team-id');
    if (addSel && addSel.options.length <= 1) {
        teamsCache.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.name;
            addSel.appendChild(opt);
        });
    }
}

function showAddPlayer() {
    ensureTeamsCache().then(populateTeamFilter);
    document.getElementById('add-player-modal').classList.add('active');
}

async function submitPlayer(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    if (data.jersey_number) data.jersey_number = parseInt(data.jersey_number);
    if (data.height_cm) data.height_cm = parseInt(data.height_cm);
    if (data.team_id) data.team_id = parseInt(data.team_id);
    else delete data.team_id;
    await fetch(`${API}/players`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    form.reset();
    closeModal('add-player-modal');
    loadPlayers();
}

// ── Standings ─────────────────────────────────────────────────────────

async function loadStandings() {
    const res = await fetch(`${API}/standings`);
    const standings = await res.json();
    const tbody = document.getElementById('standings-tbody');
    if (!standings.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No standings data</td></tr>';
        return;
    }
    tbody.innerHTML = standings.map((s, i) => `
        <tr>
            <td><span class="position-badge">${i + 1}</span></td>
            <td><strong>${s.team?.name || '-'}</strong></td>
            <td>${s.played}</td>
            <td>${s.won}</td>
            <td>${s.drawn}</td>
            <td>${s.lost}</td>
            <td>${s.goals_for}:${s.goals_against}</td>
            <td>${s.goal_difference > 0 ? '+' : ''}${s.goal_difference}</td>
            <td><strong>${s.points}</strong></td>
        </tr>
    `).join('');
}

// ── Matches ───────────────────────────────────────────────────────────

async function loadMatches() {
    const res = await fetch(`${API}/matches`);
    const matches = await res.json();
    const list = document.getElementById('matches-list');
    if (!matches.length) {
        list.innerHTML = '<div class="empty-state">No matches recorded</div>';
        return;
    }
    list.innerHTML = matches.map(m => `
        <div class="match-card">
            <div class="home">${m.home_team?.name || '?'}</div>
            <div class="score">${m.home_score ?? '-'} : ${m.away_score ?? '-'}</div>
            <div class="away">${m.away_team?.name || '?'}</div>
            <div class="match-meta">
                Round ${m.round || '-'} &middot; ${m.match_date || ''} &middot; ${m.venue || ''} &middot;
                <em>${m.status}</em>
            </div>
        </div>
    `).join('');
}

// ── Seed Database ─────────────────────────────────────────────────────

async function seedDatabase() {
    const btn = document.getElementById('seed-btn');
    btn.disabled = true;
    btn.textContent = 'Seeding...';
    await fetch(`${API}/seed`, { method: 'POST' });
    btn.disabled = false;
    btn.textContent = 'Seed Database';
    loadSection(document.querySelector('nav button.active').dataset.section);
}

// ── News ──────────────────────────────────────────────────────────────

async function loadNews() {
    await ensureTeamsCache();
    populateNewsTeamFilter();
    loadStoredNews();
}

function populateNewsTeamFilter() {
    const sel = document.getElementById('news-team-filter');
    if (!sel || sel.options.length > 1) return;
    teamsCache.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.name;
        opt.textContent = t.name;
        sel.appendChild(opt);
    });
}

async function scanNews() {
    const btn = document.getElementById('scan-btn');
    const teamFilter = document.getElementById('news-team-filter')?.value;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Scanning...';

    const body = {};
    if (teamFilter) body.team = teamFilter;

    try {
        const res = await fetch(`${API}/news/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        renderRawNews(data.articles || []);
    } catch (e) {
        document.getElementById('news-list').innerHTML =
            `<div class="empty-state">Error scanning news: ${e.message}</div>`;
    }

    btn.disabled = false;
    btn.textContent = 'Scan News';
}

async function analyzeNews() {
    const btn = document.getElementById('analyze-btn');
    const teamFilter = document.getElementById('news-team-filter')?.value;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Analyzing...';

    const body = {};
    if (teamFilter) body.team = teamFilter;

    try {
        const res = await fetch(`${API}/news/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();

        if (data.error) {
            document.getElementById('ai-analysis').style.display = 'block';
            document.getElementById('ai-summary').innerHTML =
                `<p style="color:var(--accent)"><strong>Error:</strong> ${data.error}</p>
                 <p style="margin-top:0.5rem;color:var(--text-muted)">Set the <code>ANTHROPIC_API_KEY</code> environment variable to enable AI analysis.</p>`;
            document.getElementById('ai-highlights').innerHTML = '';
            document.getElementById('ai-transfers').innerHTML = '';
            document.getElementById('ai-injuries').innerHTML = '';
        } else {
            renderAIAnalysis(data);
            if (data.articles) renderAnalyzedArticles(data.articles);
        }
    } catch (e) {
        document.getElementById('ai-analysis').style.display = 'block';
        document.getElementById('ai-summary').innerHTML =
            `<div class="empty-state">Error: ${e.message}</div>`;
    }

    btn.disabled = false;
    btn.textContent = 'Analyze with AI';
}

function renderRawNews(articles) {
    const list = document.getElementById('news-list');
    if (!articles.length) {
        list.innerHTML = '<div class="empty-state">No news articles found. Try scanning without a team filter.</div>';
        return;
    }
    list.innerHTML = articles.map(a => `
        <div class="news-article">
            <h4>${a.link ? `<a href="${a.link}" target="_blank">${a.title}</a>` : a.title}</h4>
            <div class="news-meta">
                <span>${a.source_name || 'Unknown source'}</span>
                <span>${a.pub_date || ''}</span>
            </div>
            <p class="news-summary">${a.description || ''}</p>
        </div>
    `).join('');
}

function renderAIAnalysis(data) {
    const panel = document.getElementById('ai-analysis');
    panel.style.display = 'block';
    panel.className = 'ai-panel';

    document.getElementById('ai-summary').innerHTML = `<p>${data.summary || ''}</p>`;

    const highlights = data.key_highlights || [];
    document.getElementById('ai-highlights').innerHTML = highlights.length ? `
        <h4 style="margin-bottom:0.5rem;">Key Highlights</h4>
        <ul class="highlight-list">${highlights.map(h => `<li>${h}</li>`).join('')}</ul>
    ` : '';

    const transfers = data.transfer_rumors || [];
    document.getElementById('ai-transfers').innerHTML = transfers.length ? `
        <h4 style="margin-bottom:0.5rem;">Transfer News</h4>
        <ul class="highlight-list">${transfers.map(t => `<li>${t}</li>`).join('')}</ul>
    ` : '';

    const injuries = data.injury_updates || [];
    document.getElementById('ai-injuries').innerHTML = injuries.length ? `
        <h4 style="margin-bottom:0.5rem;">Injury Updates</h4>
        <ul class="highlight-list">${injuries.map(i => `<li>${i}</li>`).join('')}</ul>
    ` : '';
}

function renderAnalyzedArticles(articles) {
    const list = document.getElementById('news-list');
    if (!articles.length) return;

    list.innerHTML = articles
        .sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0))
        .map(a => `
        <div class="news-article">
            <h4>${a.title}</h4>
            <p class="news-summary">${a.summary || ''}</p>
            <div class="news-tags">
                ${a.sentiment ? `<span class="badge badge-sentiment-${a.sentiment}">${a.sentiment}</span>` : ''}
                ${a.category ? `<span class="badge badge-category">${a.category}</span>` : ''}
                ${a.relevance_score ? `<span class="badge" style="background:#f3f4f6;color:#374151;">Score: ${a.relevance_score}/10</span>` : ''}
                ${(a.teams_mentioned || []).map(t => `<span class="badge badge-team-tag">${t}</span>`).join('')}
                ${(a.players_mentioned || []).map(p => `<span class="badge badge-player-tag">${p}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

async function loadStoredNews() {
    const params = new URLSearchParams();
    const team = document.getElementById('news-team-filter')?.value;
    const category = document.getElementById('news-category-filter')?.value;
    if (team) params.set('team', team);
    if (category) params.set('category', category);

    try {
        const res = await fetch(`${API}/news?${params}`);
        const articles = await res.json();
        const container = document.getElementById('stored-news');
        if (!articles.length) {
            container.innerHTML = '<div class="empty-state">No stored news yet. Click "Scan News" to fetch articles or "Analyze with AI" for intelligent analysis.</div>';
            return;
        }
        container.innerHTML = `<h3 style="color:var(--primary);margin-bottom:1rem;">Previously Analyzed</h3>` +
            articles.map(a => `
            <div class="news-article">
                <h4>${a.link ? `<a href="${a.link}" target="_blank">${a.title}</a>` : a.title}</h4>
                <div class="news-meta">
                    <span>${a.source_name || ''}</span>
                    <span>${a.pub_date || ''}</span>
                </div>
                ${a.llm_summary ? `<p class="news-summary">${a.llm_summary}</p>` : (a.description ? `<p class="news-summary">${a.description}</p>` : '')}
                <div class="news-tags">
                    ${a.sentiment ? `<span class="badge badge-sentiment-${a.sentiment}">${a.sentiment}</span>` : ''}
                    ${a.category ? `<span class="badge badge-category">${a.category}</span>` : ''}
                    ${(a.teams_mentioned || []).map(t => `<span class="badge badge-team-tag">${t}</span>`).join('')}
                    ${(a.players_mentioned || []).map(p => `<span class="badge badge-player-tag">${p}</span>`).join('')}
                </div>
            </div>
        `).join('');
    } catch (e) {
        // Silently fail for stored news
    }
}

// ── Init ──────────────────────────────────────────────────────────────

loadTeams();
