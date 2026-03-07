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

// ── Init ──────────────────────────────────────────────────────────────

loadTeams();
