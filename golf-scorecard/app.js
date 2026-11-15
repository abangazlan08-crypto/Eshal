/* Golf Scorecard — offline PWA. All data stays on this device (localStorage + IndexedDB). */
'use strict';

const STORE_KEY = 'golfScorecard.v1';
const APP_VERSION = 1;
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const today = () => new Date().toISOString().slice(0, 10);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = (v) => (v === '' || v == null || isNaN(+v) ? null : +v);
const sum = (a) => a.reduce((s, v) => s + (v || 0), 0);
const fmt1 = (v) => (v == null || isNaN(v) ? '–' : (Math.round(v * 10) / 10).toFixed(1));
const fmtHcp = (v) => (v == null ? '–' : v < 0 ? '+' + fmt1(-v) : fmt1(v));
const fmtDate = (d) => { try { return new Date(d + 'T12:00:00').toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }); } catch { return d; } };
const vsPar = (v) => (v == null ? '–' : v === 0 ? 'E' : v > 0 ? '+' + v : String(v));

/* ---------------- storage ---------------- */
let db = load();
function blankDb() {
  return { version: APP_VERSION, players: [], courses: [], rounds: [], settings: { lastBackup: null, defaultHoles: 18 } };
}
function load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return migrate(JSON.parse(raw));
  } catch (e) { console.warn('load failed', e); }
  return blankDb();
}
function migrate(d) {
  const b = blankDb();
  d = Object.assign(b, d || {});
  d.settings = Object.assign(blankDb().settings, d.settings || {});
  d.players.forEach((p) => { p.history = p.history || []; if (p.autoAdjust == null) p.autoAdjust = true; if (!p.base) p.base = { index: p.index ?? 0, setAt: p.createdAt || 0 }; });
  return d;
}
function save() {
  db.updatedAt = Date.now();
  try { localStorage.setItem(STORE_KEY, JSON.stringify(db)); }
  catch (e) { toast('Could not save — storage full? Make a backup and delete old photos.'); console.error(e); }
  snapshotDaily();
}

// IndexedDB for photos + daily restore points
const idb = {
  _db: null,
  open() {
    if (this._db) return Promise.resolve(this._db);
    return new Promise((res, rej) => {
      const r = indexedDB.open('golfScorecard', 1);
      r.onupgradeneeded = () => { r.result.createObjectStore('photos'); r.result.createObjectStore('snapshots'); };
      r.onsuccess = () => { this._db = r.result; res(r.result); };
      r.onerror = () => rej(r.error);
    });
  },
  async tx(store, mode, fn) {
    const d = await this.open();
    return new Promise((res, rej) => {
      const t = d.transaction(store, mode); const s = t.objectStore(store); const out = fn(s);
      t.oncomplete = () => res(out && 'result' in out ? out.result : out); t.onerror = () => rej(t.error);
    });
  },
  get(store, k) { return this.tx(store, 'readonly', (s) => s.get(k)); },
  put(store, k, v) { return this.tx(store, 'readwrite', (s) => s.put(v, k)); },
  del(store, k) { return this.tx(store, 'readwrite', (s) => s.delete(k)); },
  keys(store) { return this.tx(store, 'readonly', (s) => s.getAllKeys()); },
};
let snapTimer = null;
function snapshotDaily() {
  clearTimeout(snapTimer);
  snapTimer = setTimeout(async () => {
    try {
      await idb.put('snapshots', today(), JSON.stringify(db));
      const keys = (await idb.keys('snapshots')).sort();
      for (const k of keys.slice(0, Math.max(0, keys.length - 10))) await idb.del('snapshots', k);
    } catch (e) { console.warn('snapshot failed', e); }
  }, 1500);
}
const photoUrls = new Map();
async function photoUrl(id) {
  if (photoUrls.has(id)) return photoUrls.get(id);
  const blob = await idb.get('photos', id).catch(() => null);
  if (!blob) return null;
  const u = URL.createObjectURL(blob); photoUrls.set(id, u); return u;
}

/* ---------------- golf maths ---------------- */
// Course handicap (WHS): index × slope/113 + (rating − par). 9-hole rounds use half the index.
function courseHandicap(index, round) {
  if (index == null || isNaN(index)) return 0;
  const n = round.holes;
  const parTot = sum(round.par.slice(0, n));
  const idx = n === 9 ? index / 2 : index;
  const slope = num(round.slope) || 113;
  const rating = num(round.rating) ?? parTot;
  return Math.round(idx * (slope / 113) + (rating - parTot));
}
// Strokes received on each hole from the stroke index.
function strokesPerHole(ch, round) {
  const n = round.holes;
  const si = round.si.slice(0, n).map((v, i) => (num(v) ? +v : 100 + i));
  const order = si.map((v, i) => [v, i]).sort((a, b) => a[0] - b[0]).map((x) => x[1]); // hardest first
  const out = new Array(n).fill(0);
  if (ch >= 0) {
    for (let i = 0; i < n; i++) out[i] = Math.floor(ch / n);
    for (let k = 0; k < ch % n; k++) out[order[k]] += 1;
  } else { // plus handicap gives strokes back on the easiest holes
    const back = -ch;
    for (let i = 0; i < n; i++) out[i] = -Math.floor(back / n);
    for (let k = 0; k < back % n; k++) out[order[n - 1 - k]] -= 1;
  }
  return out;
}
function playerStats(round, rp) {
  const n = round.holes;
  const ch = rp.courseHcp ?? courseHandicap(rp.index, round);
  const strokes = strokesPerHole(ch, round);
  const scores = rp.scores.slice(0, n).map(num);
  const played = scores.filter((s) => s != null).length;
  let gross = 0, parPlayed = 0, pts = 0, ags = 0;
  scores.forEach((s, i) => {
    const par = num(round.par[i]) || 4;
    const netPar = par + strokes[i];
    if (s != null) {
      gross += s; parPlayed += par;
      pts += Math.max(0, 2 + netPar - s);
      ags += Math.min(s, netPar + 2); // net double bogey cap
    } else ags += netPar; // unplayed hole counts as net par
  });
  const half = (a, b) => scores.slice(a, b);
  const out = sum(half(0, 9)), inn = n === 18 ? sum(half(9, 18)) : null;
  const minHoles = n === 18 ? 14 : 7;
  let diff = null;
  if (played >= minHoles) {
    const parTot = sum(round.par.slice(0, n).map((p) => num(p) || 4));
    const slope = num(round.slope) || 113;
    const rating = num(round.rating) ?? parTot;
    diff = (113 / slope) * (ags - rating);
    if (n === 9) diff = diff + (rp.index || 0) / 2; // approx. WHS expected score for the other nine
    diff = Math.round(diff * 10) / 10;
  }
  // drives (F fairway, R rough, H hazard) on par 4/5s, putts and greens in regulation
  const drives = rp.drives || [], putts = rp.putts || [];
  let fw = 0, rough = 0, haz = 0, driveHoles = 0, puttTot = 0, puttHoles = 0, gir = 0, girHoles = 0;
  for (let i = 0; i < n; i++) {
    const par = num(round.par[i]) || 4, d = drives[i], pt = num(putts[i]), sc = scores[i];
    if (par > 3 && d) { driveHoles++; if (d === 'F') fw++; else if (d === 'R') rough++; else if (d === 'H') haz++; }
    if (pt != null) { puttTot += pt; puttHoles++; if (sc != null) { girHoles++; if (sc - pt <= par - 2) gir++; } }
  }
  return { fw, rough, haz, driveHoles, puttTot, puttHoles, gir, girHoles, ch, strokes, played, gross, out, inn, toPar: played ? gross - parPlayed : null, net: played === n ? gross - ch : null, pts, ags, diff };
}
// WHS: best N of the last 20 differentials, with adjustment for short records.
const WHS_TABLE = { 3: [1, -2], 4: [1, -1], 5: [1, 0], 6: [2, -1], 7: [2, 0], 8: [2, 0], 9: [3, 0], 10: [3, 0], 11: [3, 0], 12: [4, 0], 13: [4, 0], 14: [4, 0], 15: [5, 0], 16: [5, 0], 17: [6, 0], 18: [6, 0], 19: [7, 0], 20: [8, 0] };
function playerDifferentials(playerId) {
  const p = db.players.find((x) => x.id === playerId);
  const since = p?.base?.setAt || 0;
  return db.rounds
    .filter((r) => r.finished && (r.createdAt || 0) >= since)
    .map((r) => { const rp = r.players.find((x) => x.playerId === playerId); if (!rp) return null; const s = playerStats(r, rp); return s.diff == null ? null : { date: r.date, created: r.createdAt, diff: s.diff, roundId: r.id }; })
    .filter(Boolean)
    .sort((a, b) => (a.date === b.date ? a.created - b.created : a.date < b.date ? -1 : 1));
}
function computeIndex(p) {
  const diffs = playerDifferentials(p.id).slice(-20).map((d) => d.diff);
  const base = p.base?.index ?? p.index ?? 0;
  if (!diffs.length) return { index: base, method: 'Set manually', used: 0 };
  if (diffs.length < 3) { // blend the starting handicap with the first rounds so it moves straight away
    const v = (base * (3 - diffs.length) + sum(diffs)) / 3;
    return { index: clampIdx(v), method: `Blended: starting handicap + ${diffs.length} round${diffs.length > 1 ? 's' : ''}`, used: diffs.length };
  }
  const [count, adj] = WHS_TABLE[diffs.length];
  const best = [...diffs].sort((a, b) => a - b).slice(0, count);
  return { index: clampIdx(sum(best) / count + adj), method: `WHS: best ${count} of last ${diffs.length}${adj ? ` (${adj})` : ''}`, used: diffs.length };
}
const clampIdx = (v) => Math.max(-10, Math.min(54, Math.round(v * 10) / 10));
function recalcHandicaps(reason) {
  const changes = [];
  db.players.forEach((p) => {
    if (!p.autoAdjust) return;
    const { index } = computeIndex(p);
    if (index !== p.index) {
      changes.push({ name: p.name, from: p.index, to: index });
      p.index = index;
      p.history.push({ date: today(), index, reason: reason || 'Auto-adjusted' });
    }
  });
  return changes;
}

/* ---------------- helpers ---------------- */
function toast(msg, ms = 2600) {
  const t = $('#toast'); t.textContent = msg; t.classList.remove('hidden');
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.add('hidden'), ms);
}
function openModal(html, onMount) {
  $('#sheet').innerHTML = html; $('#modal').classList.remove('hidden');
  onMount && onMount($('#sheet'));
}
function closeModal() { $('#modal').classList.add('hidden'); $('#sheet').innerHTML = ''; }
$('#modal').addEventListener('click', (e) => { if (e.target.id === 'modal') closeModal(); });
function confirmBox(msg) { return Promise.resolve(window.confirm(msg)); }
function defaultPar(n) { return n === 9 ? [4, 4, 3, 5, 4, 4, 3, 4, 5] : [4, 4, 3, 5, 4, 4, 3, 4, 5, 4, 4, 3, 5, 4, 4, 3, 4, 5]; }
function getPlayer(id) { return db.players.find((p) => p.id === id); }
function getCourse(id) { return db.courses.find((c) => c.id === id); }
function download(name, text, type = 'application/json') {
  const blob = new Blob([text], { type });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
  document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}
function sparkline(values) {
  if (values.length < 2) return '';
  const w = 300, h = 48, pad = 4, min = Math.min(...values), max = Math.max(...values), span = max - min || 1;
  const pts = values.map((v, i) => `${pad + (i * (w - 2 * pad)) / (values.length - 1)},${pad + ((v - min) / span) * (h - 2 * pad)}`).join(' ');
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="var(--brand)" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>`;
}

/* ---------------- router ---------------- */
const routes = { home: viewHome, new: viewNewRound, round: viewRound, players: viewPlayers, player: viewPlayer, courses: viewCourses, course: viewCourse, backup: viewBackup };
function render() {
  const [name, arg] = (location.hash.slice(1) || 'home').split('/');
  (routes[name] || viewHome)(arg ? decodeURIComponent(arg) : undefined);
  $$('[data-nav]').forEach((a) => a.classList.toggle('active', a.dataset.nav === name || (name === 'round' && a.dataset.nav === 'home') || (name === 'player' && a.dataset.nav === 'players') || (name === 'course' && a.dataset.nav === 'courses')));
  renderBanner();
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', render);
function go(hash) { if (location.hash === '#' + hash) render(); else location.hash = hash; }
function renderBanner() {
  const last = db.settings.lastBackup;
  const stale = db.rounds.length >= 1 && (!last || Date.now() - last > 14 * 864e5);
  $('#banner').innerHTML = stale && !location.hash.startsWith('#backup') ? `<div class="bar">${last ? 'Last backup over 2 weeks ago.' : 'No backup yet.'} <a href="#backup">Back up now</a></div>` : '';
}

/* ---------------- views: home ---------------- */
function viewHome() {
  const rounds = [...db.rounds].sort((a, b) => (a.date === b.date ? b.createdAt - a.createdAt : a.date < b.date ? 1 : -1));
  const playersHtml = db.players.length
    ? db.players.map((p) => `<a class="list-item" href="#player/${p.id}"><span><span class="title">${esc(p.name)}</span><br><span class="muted small">${p.autoAdjust ? 'Auto-adjusting' : 'Manual'} handicap</span></span><span class="pill">HCP ${fmtHcp(p.index)}</span></a>`).join('')
    : '';
  $('#app').innerHTML = `
    <div class="row spread"><h1>Rounds</h1><a class="btn primary" href="#new">＋ New round</a></div>
    ${playersHtml ? `<div class="grid2" style="margin-bottom:8px">${playersHtml}</div>` : ''}
    ${rounds.length ? rounds.map((r) => {
      const line = r.players.map((rp) => { const s = playerStats(r, rp); return `${esc(rp.name)} ${s.played ? s.gross : '–'}`; }).join(' · ');
      return `<a class="list-item" href="#round/${r.id}"><span><span class="title">${esc(r.courseName || 'Unnamed course')}</span><br><span class="muted small">${fmtDate(r.date)} · ${r.holes} holes · ${line}</span></span>${r.finished ? '<span class="pill">Done</span>' : '<span class="pill warn">In play</span>'}</a>`;
    }).join('') : `<div class="empty card"><p style="font-size:2rem;margin:0">⛳</p><p>No rounds yet.</p><p>Start a round, then snap the paper scorecard or type the scores in.</p><a class="btn primary" href="#new">Start your first round</a></div>`}`;
}

/* ---------------- views: new round ---------------- */
function viewNewRound() {
  const courses = [...db.courses].sort((a, b) => a.name.localeCompare(b.name));
  const lastRound = [...db.rounds].sort((a, b) => b.createdAt - a.createdAt)[0];
  const preselect = new Set(lastRound ? lastRound.players.map((p) => p.playerId) : db.players.slice(0, 4).map((p) => p.id));
  $('#app').innerHTML = `
    <h1>New round</h1>
    <div class="card stack">
      <label class="field">Course
        <select id="nr-course"><option value="">＋ New course…</option>${courses.map((c) => `<option value="${c.id}">${esc(c.name)}${c.tee ? ' — ' + esc(c.tee) : ''}</option>`).join('')}</select>
      </label>
      <div id="nr-newcourse" class="stack">
        <label class="field">Course name<input type="text" id="nr-cname" placeholder="e.g. Kelab Golf Sultan Abdul Aziz Shah"></label>
        <div class="grid3">
          <label class="field">Holes<select id="nr-holes"><option>18</option><option>9</option></select></label>
          <label class="field">Tee (optional)<input type="text" id="nr-tee" placeholder="Blue"></label>
          <label class="field">&nbsp;<span class="muted small">Par &amp; hole handicap can be set on the card or read from the photo.</span></label>
        </div>
      </div>
      <div id="nr-coursehint" class="muted small"></div>
      <label class="field">Date<input type="date" id="nr-date" value="${today()}"></label>
    </div>
    <h2>Players &amp; handicap for this game</h2>
    <p class="muted small">Handicap is filled in from each player's record. Change it if you want a different handicap for this game.</p>
    <div id="nr-players"></div>
    <div class="card row">
      <input type="text" id="nr-newname" class="grow" placeholder="Add player name" style="width:auto">
      <input type="number" id="nr-newhcp" placeholder="HCP" step="0.1" style="width:90px">
      <button class="btn" id="nr-add">Add</button>
    </div>
    <button class="btn primary block" id="nr-start">Start round</button>`;

  const sel = $('#nr-course');
  const onCourse = () => {
    const c = getCourse(sel.value);
    $('#nr-newcourse').style.display = c ? 'none' : '';
    $('#nr-coursehint').textContent = c ? `${c.holes} holes · par ${sum(c.par.slice(0, c.holes))}${c.rating ? ` · rating ${c.rating} / slope ${c.slope || 113}` : ''}` : '';
  };
  sel.addEventListener('change', onCourse);
  if (lastRound && getCourse(lastRound.courseId)) sel.value = lastRound.courseId;
  onCourse();

  const renderPlayers = () => {
    $('#nr-players').innerHTML = db.players.length ? db.players.map((p) => `
      <div class="card row" data-pid="${p.id}">
        <label class="check grow"><input type="checkbox" class="nr-on" ${preselect.has(p.id) ? 'checked' : ''}> <strong>${esc(p.name)}</strong></label>
        <label class="field" style="width:110px">Handicap<input type="number" step="0.1" class="nr-hcp" value="${p.index ?? ''}" placeholder="${fmtHcp(p.index)}"></label>
        <label class="check small" style="flex-basis:100%"><input type="checkbox" class="nr-savehcp"> Also save this as ${esc(p.name)}'s handicap from now on</label>
      </div>`).join('') : '<p class="muted">No players yet — add yourselves below.</p>';
  };
  renderPlayers();
  $('#nr-add').onclick = () => {
    const name = $('#nr-newname').value.trim(); if (!name) return;
    const idx = num($('#nr-newhcp').value) ?? 28;
    const p = newPlayer(name, idx); preselect.add(p.id); save(); renderPlayers();
    $('#nr-newname').value = ''; $('#nr-newhcp').value = '';
  };
  $('#nr-start').onclick = () => {
    let course = getCourse(sel.value);
    if (!course) {
      const name = $('#nr-cname').value.trim();
      if (!name) { toast('Enter the course name'); $('#nr-cname').focus(); return; }
      const holes = +$('#nr-holes').value;
      course = db.courses.find((c) => c.name.toLowerCase() === name.toLowerCase() && c.holes === holes);
      if (!course) { course = { id: uid(), name, tee: $('#nr-tee').value.trim(), holes, par: defaultPar(holes), si: [], rating: null, slope: null, createdAt: Date.now() }; db.courses.push(course); }
    }
    const chosen = $$('#nr-players [data-pid]').filter((el) => $('.nr-on', el).checked);
    if (!chosen.length) { toast('Pick at least one player'); return; }
    const round = { id: uid(), date: $('#nr-date').value || today(), courseId: course.id, courseName: course.name, tee: course.tee || '', holes: course.holes, par: [...course.par], si: [...(course.si || [])], rating: course.rating, slope: course.slope, players: [], photoIds: [], notes: '', finished: false, createdAt: Date.now() };
    chosen.forEach((el) => {
      const p = getPlayer(el.dataset.pid);
      const idx = num($('.nr-hcp', el).value) ?? p.index ?? 0;
      if ($('.nr-savehcp', el).checked) setManualHandicap(p, idx, 'Set before round');
      round.players.push({ playerId: p.id, name: p.name, index: idx, scores: [] });
    });
    round.players.forEach((rp) => (rp.courseHcp = courseHandicap(rp.index, round)));
    db.rounds.push(round); save(); go('round/' + round.id);
  };
}
function newPlayer(name, index) {
  const p = { id: uid(), name, index: clampIdx(index), autoAdjust: true, base: { index: clampIdx(index), setAt: Date.now() }, history: [{ date: today(), index: clampIdx(index), reason: 'Starting handicap' }], createdAt: Date.now() };
  db.players.push(p); return p;
}
function setManualHandicap(p, index, reason) {
  index = clampIdx(index);
  p.index = index; p.base = { index, setAt: Date.now() };
  p.history.push({ date: today(), index, reason: reason || 'Set manually' });
}

/* ---------------- views: round / scorecard ---------------- */
let ocrCells = new Set();
function viewRound(id) {
  const r = db.rounds.find((x) => x.id === id);
  if (!r) { $('#app').innerHTML = '<div class="empty">Round not found. <a href="#home">Back</a></div>'; return; }
  const n = r.holes;
  $('#app').innerHTML = `
    <div class="row spread"><a href="#home" class="muted small">‹ Rounds</a>${r.finished ? '<span class="pill">Finished</span>' : '<span class="pill warn">In play</span>'}</div>
    <div class="card stack">
      <label class="field">Course name<input type="text" id="r-cname" value="${esc(r.courseName)}"></label>
      <div class="grid3">
        <label class="field">Date<input type="date" id="r-date" value="${esc(r.date)}"></label>
        <label class="field">Course rating<input type="number" step="0.1" id="r-rating" value="${r.rating ?? ''}" placeholder="${sum(r.par.slice(0, n).map((p) => num(p) || 4))}"></label>
        <label class="field">Slope<input type="number" id="r-slope" value="${r.slope ?? ''}" placeholder="113"></label>
      </div>
      <p class="muted small" style="margin:0">Rating &amp; slope are printed on most scorecards for each tee. Leave blank to use par / 113.</p>
    </div>

    <div class="card">
      <div class="row spread"><h3 style="margin:0">Scorecard photo</h3>
        <span class="row"><label class="btn small primary">📷 Take photo<input type="file" class="r-photo" accept="image/*" capture="environment" hidden></label><label class="btn small">🖼️ From gallery<input type="file" class="r-photo" accept="image/*" hidden></label></span></div>
      <div class="photos" id="r-photos" style="margin-top:8px"></div>
      <div id="r-photodock"></div>
    </div>

    <div class="card">
      <div class="row spread"><h3 style="margin:0">Virtual scorecard</h3><span class="muted small">Tap any box to edit</span></div>
      <label class="check small" style="margin:6px 0"><input type="checkbox" id="r-track" ${db.settings.trackShots !== false ? 'checked' : ''}> Track drives &amp; putts</label>
      <div id="r-card"></div>
      <p class="muted small" id="r-legend">Drive: tap the box to switch <b class="drv-F lg">F</b> fairway → <b class="drv-R lg">R</b> rough → <b class="drv-H lg">H</b> hazard → empty. Par 3s are skipped.</p>
      <p class="muted small" id="r-ocrnote" style="display:none">Yellow boxes were read from the photo — check them against the card.</p>
    </div>

    <div class="card"><h3 style="margin-top:0">Results</h3><div id="r-summary"></div></div>

    <div class="card stack">
      <h3 style="margin:0">Handicap used in this game</h3>
      <div id="r-hcps"></div>
    </div>

    <div class="card"><label class="field">Notes<textarea id="r-notes" rows="2" placeholder="Weather, partners, best shot…">${esc(r.notes)}</textarea></label></div>

    <div class="row">
      <button class="btn primary grow" id="r-finish">${r.finished ? 'Save changes & update handicaps' : 'Finish round & update handicaps'}</button>
      <button class="btn danger" id="r-delete">Delete</button>
    </div>
    <p class="muted small">Course par, hole handicap, rating and slope are remembered for “${esc(r.courseName)}” next time.</p>`;

  const persistCourse = () => {
    let c = getCourse(r.courseId);
    if (!c) { c = { id: r.courseId || uid(), createdAt: Date.now() }; r.courseId = c.id; db.courses.push(c); }
    Object.assign(c, { name: r.courseName, tee: r.tee || c.tee || '', holes: r.holes, par: [...r.par], si: [...r.si], rating: r.rating, slope: r.slope });
  };
  const touch = () => { r.updatedAt = Date.now(); persistCourse(); save(); };

  $('#r-cname').onchange = (e) => { r.courseName = e.target.value.trim() || 'Unnamed course'; touch(); };
  $('#r-date').onchange = (e) => { r.date = e.target.value; touch(); };
  $('#r-rating').onchange = (e) => { r.rating = num(e.target.value); refreshHcps(); touch(); };
  $('#r-slope').onchange = (e) => { r.slope = num(e.target.value); refreshHcps(); touch(); };
  $('#r-track').onchange = (e) => { db.settings.trackShots = e.target.checked; save(); renderCard(); renderSummary(); };
  $('#r-notes').onchange = (e) => { r.notes = e.target.value; touch(); };

  function refreshHcps(force) {
    r.players.forEach((rp) => { if (force || !rp.hcpLocked) rp.courseHcp = courseHandicap(rp.index, r); });
    renderHcps(); renderCard(); renderSummary();
  }
  function renderHcps() {
    $('#r-hcps').innerHTML = r.players.map((rp, i) => `
      <div class="grid3" data-i="${i}">
        <label class="field">${esc(rp.name)} — handicap<input type="number" step="0.1" class="h-idx" value="${rp.index ?? ''}"></label>
        <label class="field">Course handicap<input type="number" class="h-ch" value="${rp.courseHcp ?? ''}"></label>
        <label class="field">&nbsp;<span class="muted small">Record: ${fmtHcp(getPlayer(rp.playerId)?.index)}</span></label>
      </div>`).join('') + `<p class="muted small" style="margin:0">Changing the handicap here only affects this game. To change a player's saved handicap, go to Players. The Handicap row on the card is each hole's difficulty (1 = hardest), which sets where handicap strokes fall.</p>`;
    $$('#r-hcps [data-i]').forEach((el) => {
      const rp = r.players[+el.dataset.i];
      $('.h-idx', el).onchange = (e) => { rp.index = num(e.target.value) ?? 0; rp.hcpLocked = false; rp.courseHcp = courseHandicap(rp.index, r); touch(); renderHcps(); renderCard(); renderSummary(); };
      $('.h-ch', el).onchange = (e) => { rp.courseHcp = num(e.target.value) ?? 0; rp.hcpLocked = true; touch(); renderCard(); renderSummary(); };
    });
  }

  function renderCard() {
    const halves = n === 18 ? [[0, 9, 'Out'], [9, 18, 'In']] : [[0, 9, 'Tot']];
    const strokes = r.players.map((rp) => playerStats(r, rp).strokes);
    const track = db.settings.trackShots !== false;
    $('#r-card').innerHTML = halves.map(([a, b, label]) => {
      const holes = [...Array(b - a)].map((_, k) => a + k);
      const cell = (row, i, val, cls = '', extra = '') => `<td class="${ocrCells.has(row + ':' + i) ? 'ocr' : ''}">${extra}<input inputmode="numeric" pattern="[0-9]*" type="number" data-row="${row}" data-i="${i}" value="${val ?? ''}" class="${cls}"></td>`;
      const playerRows = r.players.map((rp, pi) => {
        const sc = holes.map((i) => {
          const s = num(rp.scores[i]); const par = num(r.par[i]) || 4; let cls = '';
          if (s != null) { const d = s - par; cls = d <= -2 ? 'eagle' : d === -1 ? 'birdie' : d >= 2 ? 'bogey2' : ''; }
          const st = strokes[pi][i]; const dots = st > 0 ? `<span class="dots">${'•'.repeat(Math.min(st, 3))}</span>` : '';
          return cell('p' + pi, i, rp.scores[i], cls, dots);
        }).join('');
        const tot = sum(holes.map((i) => num(rp.scores[i])));
        const totAll = sum(rp.scores.slice(0, n).map(num));
        let html = `<tr class="prow"><td class="name" title="${esc(rp.name)}">${esc(rp.name)}</td>${sc}<td class="tot">${tot || ''}</td>${n === 18 && b === 18 ? `<td class="tot">${totAll || ''}</td>` : ''}</tr>`;
        if (track) {
          rp.drives = rp.drives || []; rp.putts = rp.putts || [];
          const all = [...Array(n).keys()];
          const fwStr = (list) => { const e = list.filter((i) => (num(r.par[i]) || 4) > 3 && rp.drives[i]); return e.length ? `${e.filter((i) => rp.drives[i] === 'F').length}/${e.length}` : ''; };
          const drv = holes.map((i) => ((num(r.par[i]) || 4) > 3
            ? `<td><button type="button" class="drv drv-${rp.drives[i] || 'x'}" data-p="${pi}" data-i="${i}" aria-label="Drive hole ${i + 1}">${rp.drives[i] || '·'}</button></td>`
            : '<td class="na">–</td>')).join('');
          const pts = holes.map((i) => cell('u' + pi, i, rp.putts[i], 'putt')).join('');
          const pSum = (list) => sum(list.map((i) => num(rp.putts[i]))) || '';
          html += `<tr class="sub"><td class="name muted">↳ Drive</td>${drv}<td class="tot small">${fwStr(holes)}</td>${n === 18 && b === 18 ? `<td class="tot small">${fwStr(all)}</td>` : ''}</tr>`;
          html += `<tr class="sub"><td class="name muted">↳ Putts</td>${pts}<td class="tot">${pSum(holes)}</td>${n === 18 && b === 18 ? `<td class="tot">${pSum(all)}</td>` : ''}</tr>`;
        }
        return html;
      }).join('');
      const parTot = sum(holes.map((i) => num(r.par[i])));
      return `<div class="sc-wrap" style="margin-bottom:10px"><table class="sc">
        <tr><th class="name">Hole</th>${holes.map((i) => `<th>${i + 1}</th>`).join('')}<th>${label}</th>${n === 18 && b === 18 ? '<th>Tot</th>' : ''}</tr>
        <tr class="meta"><td class="name muted">Par</td>${holes.map((i) => cell('par', i, r.par[i])).join('')}<td class="tot">${parTot || ''}</td>${n === 18 && b === 18 ? `<td class="tot">${sum(r.par.slice(0, 18).map(num)) || ''}</td>` : ''}</tr>
        <tr class="meta"><td class="name muted">Handicap</td>${holes.map((i) => cell('si', i, r.si[i])).join('')}<td class="tot"></td>${n === 18 && b === 18 ? '<td class="tot"></td>' : ''}</tr>
        ${playerRows}
      </table></div>`;
    }).join('');
    $('#r-ocrnote').style.display = ocrCells.size ? '' : 'none';
    $('#r-legend').style.display = track ? '' : 'none';
    $$('#r-card .drv').forEach((btn) => (btn.onclick = () => {
      const rp = r.players[+btn.dataset.p]; const i = +btn.dataset.i; rp.drives = rp.drives || [];
      const cycle = ['', 'F', 'R', 'H']; rp.drives[i] = cycle[(cycle.indexOf(rp.drives[i] || '') + 1) % cycle.length] || null;
      touch(); renderCard(); renderSummary();
    }));
    $$('#r-card input').forEach((inp) => {
      inp.addEventListener('change', onCellChange);
      inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); focusNext(inp); } });
      inp.addEventListener('focus', () => inp.select());
    });
  }
  function focusNext(inp) {
    const all = $$('#r-card input'); const row = inp.dataset.row; const i = +inp.dataset.i;
    const next = all.find((x) => x.dataset.row === row && +x.dataset.i === i + 1);
    (next || all[all.indexOf(inp) + 1])?.focus();
  }
  function onCellChange(e) {
    const { row, i } = e.target.dataset; const v = num(e.target.value);
    if (row === 'par') r.par[+i] = v; else if (row === 'si') r.si[+i] = v;
    else if (row.startsWith('u')) { const rp = r.players[+row.slice(1)]; (rp.putts = rp.putts || [])[+i] = v; }
    else r.players[+row.slice(1)].scores[+i] = v;
    ocrCells.delete(row + ':' + i);
    if (row === 'par') refreshHcps(); // par total changes course handicap when no rating is set
    touch(); renderCard(); renderSummary();
    // keep the flow: jump to the next box after typing a score
    const nxt = $(`#r-card input[data-row="${row}"][data-i="${+i + 1}"]`); if (nxt && v != null && /^[pu]/.test(row)) nxt.focus();
  }

  function renderSummary() {
    $('#r-summary').innerHTML = `<div class="sc-wrap"><table class="summary"><tr><th>Player</th><th>Gross</th><th>To par</th><th>Hcp</th><th>Net</th><th>Pts</th><th>Diff</th></tr>
      ${r.players.map((rp) => { const s = playerStats(r, rp); return `<tr><td><strong>${esc(rp.name)}</strong><br><span class="muted small">${s.played}/${n} holes</span></td><td>${s.played ? s.gross : '–'}${n === 18 && s.played ? `<br><span class="muted small">${s.out || '–'}/${s.inn || '–'}</span>` : ''}</td><td>${vsPar(s.toPar)}</td><td>${s.ch}</td><td>${s.net ?? '–'}</td><td>${s.played ? s.pts : '–'}</td><td>${s.diff == null ? '–' : fmt1(s.diff)}</td></tr>`; }).join('')}
    </table></div>
    ${db.settings.trackShots !== false ? `<div class="sc-wrap" style="margin-top:10px"><table class="summary"><tr><th>Player</th><th>Fairway</th><th>Rough</th><th>Hazard</th><th>Putts</th><th>GIR</th></tr>
      ${r.players.map((rp) => { const s = playerStats(r, rp); const pc = (a, b) => (b ? `${a}/${b}` : '–'); return `<tr><td><strong>${esc(rp.name)}</strong></td><td>${pc(s.fw, s.driveHoles)}</td><td>${s.driveHoles ? s.rough : '–'}</td><td>${s.driveHoles ? s.haz : '–'}</td><td>${s.puttHoles ? s.puttTot : '–'}${s.puttHoles ? `<br><span class="muted small">${(s.puttTot / s.puttHoles).toFixed(1)}/hole</span>` : ''}</td><td>${pc(s.gir, s.girHoles)}</td></tr>`; }).join('')}
    </table></div>` : ''}<p class="muted small">GIR = green in regulation (worked out from score − putts). Pts = Stableford. Diff = WHS score differential (net double bogey cap) — used to adjust handicaps when the round is finished. Dots on a box = handicap strokes on that hole.</p>`;
  }

  async function renderPhotos() {
    const box = $('#r-photos');
    if (!r.photoIds.length) { box.innerHTML = '<span class="muted small">Take a photo of the paper scorecard, or pick one from your gallery, and the app will read it into the card below.</span>'; $('#r-photodock').innerHTML = ''; return; }
    const urls = await Promise.all(r.photoIds.map(photoUrl));
    box.innerHTML = urls.map((u, k) => (u ? `<img src="${u}" data-k="${k}" alt="Scorecard photo ${k + 1}">` : '')).join('');
    $$('img', box).forEach((img) => (img.onclick = () => showDock(+img.dataset.k)));
    showDock(r._dock ?? 0);
  }
  async function showDock(k) {
    const id = r.photoIds[k]; if (!id) return; r._dock = k;
    const u = await photoUrl(id);
    $('#r-photodock').innerHTML = `
      <div class="photo-view" id="pv" style="margin-top:8px"><img src="${u}" id="pv-img" alt="Scorecard"></div>
      <div class="row" style="margin-top:8px">
        <button class="btn small primary" id="pv-ocr">🔍 Read scores from photo</button>
        <button class="btn small" id="pv-zoom">Zoom</button>
        <button class="btn small" id="pv-pin">Pin while editing</button>
        <button class="btn small danger" id="pv-del">Remove photo</button>
      </div>`;
    let z = 1; $('#pv-zoom').onclick = () => { z = z >= 3 ? 1 : z + 1; $('#pv-img').style.width = z * 100 + '%'; };
    $('#pv-pin').onclick = (e) => { const dock = $('#r-photodock'); dock.classList.toggle('photo-dock'); e.target.textContent = dock.classList.contains('photo-dock') ? 'Unpin' : 'Pin while editing'; };
    $('#pv-del').onclick = async () => {
      if (!(await confirmBox('Remove this photo from the round?'))) return;
      r.photoIds.splice(k, 1); r._dock = 0; await idb.del('photos', id).catch(() => {}); touch(); renderPhotos();
    };
    $('#pv-ocr').onclick = () => runOcr(r, id, () => { renderCard(); renderSummary(); refreshHcps(); touch(); });
  }
  $$('.r-photo').forEach((inp) => (inp.onchange = async (e) => {
    const file = e.target.files[0]; if (!file) return; e.target.value = '';
    try {
      const blob = await compressImage(file, 2000, 0.85);
      const pid = uid(); await idb.put('photos', pid, blob);
      r.photoIds.push(pid); r._dock = r.photoIds.length - 1; touch(); await renderPhotos();
      runOcr(r, pid, () => { renderCard(); renderSummary(); refreshHcps(); touch(); });
    } catch (err) { console.error(err); toast('Could not save photo: ' + err.message); }
  }));

  $('#r-finish').onclick = () => {
    const missing = r.players.filter((rp) => playerStats(r, rp).played < n);
    if (missing.length && !window.confirm(`${missing.map((m) => m.name).join(', ')} ha${missing.length > 1 ? 've' : 's'} empty holes. Finish anyway? (Rounds with fewer than ${n === 18 ? 14 : 7} holes don't count toward handicap.)`)) return;
    r.finished = true; r.finishedAt = r.finishedAt || Date.now(); touch();
    const changes = recalcHandicaps(`After ${r.courseName} (${r.date})`); save();
    openModal(`<h2 style="margin-top:0">Round saved ✅</h2>
      ${r.players.map((rp) => { const s = playerStats(r, rp); return `<p><strong>${esc(rp.name)}</strong>: ${s.gross} gross (${vsPar(s.toPar)}), net ${s.net ?? '–'}, ${s.pts} pts${s.diff != null ? `, differential ${fmt1(s.diff)}` : ''}</p>`; }).join('')}
      <h3>Handicaps</h3>
      ${changes.length ? changes.map((c) => `<p>${esc(c.name)}: ${fmtHcp(c.from)} → <strong>${fmtHcp(c.to)}</strong></p>`).join('') : '<p class="muted">No handicap changes.</p>'}
      <button class="btn primary block" id="m-ok">OK</button>`, (s) => ($('#m-ok', s).onclick = () => { closeModal(); render(); }));
  };
  $('#r-delete').onclick = async () => {
    if (!(await confirmBox('Delete this round and its photos? This cannot be undone (unless you have a backup).'))) return;
    for (const pid of r.photoIds) await idb.del('photos', pid).catch(() => {});
    db.rounds = db.rounds.filter((x) => x !== r); recalcHandicaps('Round deleted'); save(); go('home');
  };

  ocrCells = new Set();
  renderHcps(); renderCard(); renderSummary(); renderPhotos();
}

/* ---------------- photo + OCR ---------------- */
function loadImage(src) {
  return new Promise((res, rej) => { const img = new Image(); img.onload = () => res(img); img.onerror = () => rej(new Error('Could not read image')); img.src = src; });
}
async function compressImage(file, maxSide, quality) {
  const url = URL.createObjectURL(file);
  try {
    const img = await loadImage(url);
    const scale = Math.min(1, maxSide / Math.max(img.naturalWidth, img.naturalHeight));
    const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * scale); c.height = Math.round(img.naturalHeight * scale);
    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
    return await new Promise((res) => c.toBlob(res, 'image/jpeg', quality));
  } finally { URL.revokeObjectURL(url); }
}
// Greyscale + Otsu threshold so pencil/pen marks stand out from the printed grid.
async function preprocess(blob) {
  const url = URL.createObjectURL(blob);
  try {
    const img = await loadImage(url);
    const target = 2200, scale = Math.min(2, target / img.naturalWidth);
    const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * scale); c.height = Math.round(img.naturalHeight * scale);
    const ctx = c.getContext('2d', { willReadFrequently: true }); ctx.drawImage(img, 0, 0, c.width, c.height);
    const d = ctx.getImageData(0, 0, c.width, c.height); const px = d.data; const hist = new Array(256).fill(0);
    for (let i = 0; i < px.length; i += 4) { const g = (px[i] * 0.299 + px[i + 1] * 0.587 + px[i + 2] * 0.114) | 0; px[i] = g; hist[g]++; }
    const total = px.length / 4; let sumAll = 0; for (let t = 0; t < 256; t++) sumAll += t * hist[t];
    let sumB = 0, wB = 0, best = 0, thr = 128;
    for (let t = 0; t < 256; t++) { wB += hist[t]; if (!wB) continue; const wF = total - wB; if (!wF) break; sumB += t * hist[t]; const mB = sumB / wB, mF = (sumAll - sumB) / wF; const between = wB * wF * (mB - mF) ** 2; if (between > best) { best = between; thr = t; } }
    for (let i = 0; i < px.length; i += 4) { const v = px[i] > thr ? 255 : 0; px[i] = px[i + 1] = px[i + 2] = v; }
    ctx.putImageData(d, 0, 0);
    return c;
  } finally { URL.revokeObjectURL(url); }
}
// Whiten long straight dark runs (the printed grid) so digits are not glued to cell borders.
function removeLines(px, w, h) {
  const dark = (x, y) => px[(y * w + x) * 4] === 0;
  const kill = [];
  const minH = Math.max(60, w / 10), minV = Math.max(60, h / 8);
  for (let y = 0; y < h; y++) { let run = 0; for (let x = 0; x <= w; x++) { if (x < w && dark(x, y)) run++; else { if (run >= minH) kill.push([x - run, y, run, 0]); run = 0; } } }
  for (let x = 0; x < w; x++) { let run = 0; for (let y = 0; y <= h; y++) { if (y < h && dark(x, y)) run++; else { if (run >= minV) kill.push([x, y - run, run, 1]); run = 0; } } }
  for (const [x0, y0, len, vert] of kill) for (let k = 0; k < len; k++) { const i = ((vert ? y0 + k : y0) * w + (vert ? x0 : x0 + k)) * 4; px[i] = px[i + 1] = px[i + 2] = 255; }
}
// ---- grid-based reading: straighten, find the printed grid, read every box on its own ----
function binData(c) { return c.getContext('2d', { willReadFrequently: true }).getImageData(0, 0, c.width, c.height); }
function estimateSkew(c) {
  const sc = Math.min(1, 700 / c.width); const s = document.createElement('canvas');
  s.width = Math.round(c.width * sc); s.height = Math.round(c.height * sc);
  s.getContext('2d').drawImage(c, 0, 0, s.width, s.height);
  const { data, width: w, height: h } = binData(s); const pts = [];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (data[(y * w + x) * 4] < 128) pts.push(x, y);
  let best = 0, bestScore = -1;
  for (let a = -8; a <= 8.001; a += 0.25) {
    const r = (a * Math.PI) / 180, sn = Math.sin(r), cs = Math.cos(r), bins = new Float64Array(h * 2 + 10);
    for (let i = 0; i < pts.length; i += 2) { const yy = Math.round(pts[i + 1] * cs - pts[i] * sn + h * 0.5); if (yy >= 0 && yy < bins.length) bins[yy]++; }
    let sc2 = 0; for (const b of bins) sc2 += b * b;
    if (sc2 > bestScore) { bestScore = sc2; best = a; }
  }
  return best;
}
function rotateBinary(c, deg) {
  if (Math.abs(deg) < 0.2) return c;
  const r = (deg * Math.PI) / 180; const out = document.createElement('canvas'); out.width = c.width; out.height = c.height;
  const ctx = out.getContext('2d', { willReadFrequently: true }); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
  ctx.translate(c.width / 2, c.height / 2); ctx.rotate(-r); ctx.drawImage(c, -c.width / 2, -c.height / 2);
  const d = ctx.getImageData(0, 0, c.width, c.height); const px = d.data;
  for (let i = 0; i < px.length; i += 4) { const v = px[i] < 160 ? 0 : 255; px[i] = px[i + 1] = px[i + 2] = v; }
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.putImageData(d, 0, 0); return out;
}
function findLines(profile, thresh, minGap) {
  const lines = []; let start = -1;
  for (let i = 0; i <= profile.length; i++) {
    const on = i < profile.length && profile[i] >= thresh;
    if (on && start < 0) start = i;
    if (!on && start >= 0) { const c = (start + i - 1) / 2; if (!lines.length || c - lines[lines.length - 1] > minGap) lines.push(c); start = -1; }
  }
  return lines;
}
async function gridOcr(bin, worker, status) {
  const c = rotateBinary(bin, estimateSkew(bin));
  const { data, width: w, height: h } = binData(c);
  const dark = (x, y) => data[(y * w + x) * 4] < 128;
  const rowP = new Array(h).fill(0), colP = new Array(w).fill(0);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (dark(x, y)) { rowP[y]++; colP[x]++; }
  const hL = findLines(rowP, Math.max(w * 0.3, Math.max(...rowP) * 0.5), 12);
  const vL = findLines(colP, Math.max(h * 0.15, Math.max(...colP) * 0.5), 12);
  if (hL.length < 3 || vL.length < 6) return null;
  const minCell = 18;
  const rowsB = []; for (let i = 0; i < hL.length - 1; i++) if (hL[i + 1] - hL[i] > minCell) rowsB.push([hL[i], hL[i + 1]]);
  if (rowsB.length) { // cards often have no border above the first / below the last row
    const hs = rowsB.map(([a, b]) => b - a).sort((a, b) => a - b); const medH = hs[hs.length >> 1];
    const last = hL[hL.length - 1], first = hL[0];
    if (last + medH * 0.9 < h) rowsB.push([last, Math.min(h - 1, last + medH)]);
    if (first - medH * 0.9 > 0) rowsB.unshift([Math.max(0, first - medH), first]);
  }
  const colsB = []; for (let j = 0; j < vL.length - 1; j++) if (vL[j + 1] - vL[j] > minCell) colsB.push([vL[j], vL[j + 1]]);
  const widths = colsB.map(([a, b]) => b - a).sort((a, b) => a - b); const medW = widths[widths.length >> 1];
  const cols = colsB.filter(([a, b]) => b - a < medW * 1.7); // skip the wide name column
  await worker.setParameters({ tessedit_pageseg_mode: '7' });
  const cell = document.createElement('canvas'); const cctx = cell.getContext('2d', { willReadFrequently: true });
  const out = []; const total = rowsB.length * cols.length; let done = 0;
  for (const [y0, y1] of rowsB) {
    const vals = [];
    for (const [x0, x1] of cols) {
      done++; if (status && done % 5 === 0) status({ status: `reading boxes ${done}/${total}`, progress: done / total });
      const ix = Math.round((x1 - x0) * 0.12), iy = Math.round((y1 - y0) * 0.12);
      const ax = Math.round(x0) + ix, ay = Math.round(y0) + iy, bx = Math.round(x1) - ix, by = Math.round(y1) - iy;
      let minX = 1e9, minY = 1e9, maxX = -1, maxY = -1, ink = 0;
      for (let y = ay; y < by; y++) for (let x = ax; x < bx; x++) if (dark(x, y)) { ink++; if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y; }
      if (ink < (bx - ax) * (by - ay) * 0.004 || maxY - minY < (by - ay) * 0.18) { vals.push(null); continue; }
      const gw = maxX - minX + 1, gh = maxY - minY + 1, scale = 56 / gh, pad = 24;
      cell.width = Math.round(gw * scale) + pad * 2; cell.height = 56 + pad * 2;
      cctx.fillStyle = '#fff'; cctx.fillRect(0, 0, cell.width, cell.height);
      cctx.drawImage(c, minX, minY, gw, gh, pad, pad, gw * scale, 56);
      let { data: r } = await worker.recognize(cell);
      let t = (r.text || '').replace(/\D/g, '');
      if (!t) { // single small digits are sometimes skipped in line mode — retry as one character
        await worker.setParameters({ tessedit_pageseg_mode: '10' });
        ({ data: r } = await worker.recognize(cell)); t = (r.text || '').replace(/\D/g, '');
        await worker.setParameters({ tessedit_pageseg_mode: '7' });
      }
      vals.push(t ? parseInt(t, 10) : null);
    }
    if (vals.some((v) => v != null)) out.push(vals);
  }
  // drop columns that are empty in most rows (photo edges, gaps between tables)
  const keep = cols.map((_, j) => out.filter((r) => r[j] != null).length > out.length * 0.3);
  return out.map((r) => r.filter((_, j) => keep[j]));
}
// Drop OUT / IN / TOTAL columns: a value equal to the sum of the boxes before it.
function stripTotals(vals) {
  const res = []; let run = 0, cnt = 0;
  for (const v of vals) {
    if (v != null && v > 15 && cnt >= 3 && (v === run || cnt === 9)) { run = 0; cnt = 0; continue; }
    res.push(v); if (v != null) { run += v; } cnt++;
  }
  // trailing grand total
  while (res.length && res[res.length - 1] != null && res[res.length - 1] > 15 && res.length > 9) res.pop();
  return res;
}
// Group recognised words into rows by their vertical position, then read each row left to right.
function wordsToLines(words) {
  const ws = words.filter((w) => /\d/.test(w.text) && w.confidence > 20).map((w) => ({ text: w.text, x: w.bbox.x0, cy: (w.bbox.y0 + w.bbox.y1) / 2, h: w.bbox.y1 - w.bbox.y0 }));
  if (!ws.length) return [];
  const hs = ws.map((w) => w.h).sort((a, b) => a - b); const medH = hs[hs.length >> 1] || 20;
  ws.sort((a, b) => a.cy - b.cy);
  const rows = [];
  for (const w of ws) { const r = rows[rows.length - 1]; if (r && Math.abs(w.cy - r.cy) < medH * 0.6) { r.items.push(w); r.cy = (r.cy * (r.items.length - 1) + w.cy) / r.items.length; } else rows.push({ cy: w.cy, items: [w] }); }
  return rows.map((r) => r.items.sort((a, b) => a.x - b.x).map((w) => w.text).join(' '));
}
let ocrWorker = null;
async function getWorker(onProgress) {
  if (ocrWorker) return ocrWorker;
  if (!window.Tesseract) {
    await new Promise((res, rej) => { const s = document.createElement('script'); s.src = 'vendor/tesseract.min.js'; s.onload = res; s.onerror = () => rej(new Error('OCR engine missing')); document.head.appendChild(s); });
  }
  const base = new URL('vendor/', location.href).href;
  ocrWorker = await Tesseract.createWorker('eng', 1, {
    workerPath: base + 'worker.min.js', corePath: base + 'core', langPath: base + 'lang', gzip: true, workerBlobURL: false,
    logger: (m) => onProgress && onProgress(m),
  });
  await ocrWorker.setParameters({ tessedit_char_whitelist: '0123456789', tessedit_pageseg_mode: '11', preserve_interword_spaces: '1' });
  return ocrWorker;
}
// Turn a line of OCR text into hole values: split merged digits ("453" → 4,5,3) and skip totals.
function parseNumbers(text) {
  const out = [];
  for (const tok of text.split(/\s+/).filter(Boolean)) {
    const v = parseInt(tok, 10); if (isNaN(v)) continue;
    if (v >= 1 && v <= 15) out.push(v);
    else if (v >= 16 && v <= 99) {
      if (out.length && out.length % 9 === 0) continue; // OUT / IN / TOTAL column
      if (!tok.includes('0')) for (const ch of tok) out.push(+ch);
    } else if (v >= 100) { out.push(-1); } // yardage → mark row as yardage
  }
  return out;
}
// Hole-number row? (1,2,3… or 10,11,12… in most positions)
function holeRowStart(vals) {
  for (const base of [1, 10]) {
    const hits = vals.filter((v, j) => v === base + j).length;
    if (hits >= Math.max(4, vals.filter((v) => v != null).length * 0.6)) return base - 1;
  }
  return -1;
}
function guessRows(valRows, round) {
  const n = round.holes;
  const rows = valRows.map((vals) => ({ vals: vals.slice(0, Math.max(n, 9)), nums: vals.filter((v) => v != null) }))
    .filter((r) => r.nums.length >= 3 && r.nums.filter((v) => v >= 100 || v < 0).length < 3)
    .map((r) => ({ ...r, vals: r.vals.map((v) => (v != null && (v < 0 || v >= 100) ? null : v)) }));
  let playerIdx = 0, seen = {}, section = 0, sectionStart = 0;
  rows.forEach((row) => {
    const v = row.vals.filter((x) => x != null);
    const hs = holeRowStart(row.vals);
    if (hs >= 0) { // a new table starts (front nine / back nine)
      row.target = 'ignore'; row.start = 0;
      if (Object.keys(seen).length) { section++; seen = {}; playerIdx = 0; }
      sectionStart = n === 18 ? (hs === 9 || section > 0 ? 9 : 0) : 0;
      return;
    }
    const parLike = v.length >= 5 && v.every((x) => x >= 3 && x <= 5);
    const distinct = v.length >= 5 && new Set(v).size === v.length && v.every((x) => x >= 1 && x <= 18);
    if (parLike && !seen.par) row.target = 'par';
    else if (distinct && !seen.si && v.some((x) => x > 9 || x <= 2)) row.target = 'si';
    else if (playerIdx < round.players.length) row.target = 'p' + playerIdx++;
    else row.target = 'ignore';
    row.start = sectionStart;
    if (row.target !== 'ignore') seen[row.target] = true;
  });
  return rows;
}
async function runOcr(round, photoId, onApplied) {
  openModal(`<h2 style="margin-top:0">Reading scorecard…</h2><p class="muted small" id="o-status">Starting the on-device reader (first time takes a few seconds).</p><div class="progress"><div id="o-bar"></div></div>
    <p class="muted small">Tip: lay the card flat, fill the frame, good light, no shadows. Handwriting is hard for any reader — you'll be able to check and fix everything.</p>
    <button class="btn block" id="o-cancel" style="margin-top:10px">Cancel</button>`);
  let cancelled = false; $('#o-cancel').onclick = () => { cancelled = true; closeModal(); };
  const status = (m) => { const s = $('#o-status'); const b = $('#o-bar'); if (!s) return; s.textContent = m.status ? m.status[0].toUpperCase() + m.status.slice(1) : ''; if (b && m.progress != null) b.style.width = Math.round(m.progress * 100) + '%'; };
  try {
    const blob = await idb.get('photos', photoId);
    const canvas = await preprocess(blob);
    const worker = await getWorker(status);
    if (cancelled) return;
    let grid = null;
    try { grid = await gridOcr(canvas, worker, status); } catch (e) { console.warn('grid read failed', e); }
    if (cancelled) return;
    let rows, raw;
    if (grid && grid.length) {
      rows = guessRows(grid.map(stripTotals), round);
      raw = grid.map((r) => r.map((v) => v ?? '·').join(' ')).join('\n');
    } else { // no clear grid: read the whole page
      const d = binData(canvas); removeLines(d.data, canvas.width, canvas.height); canvas.getContext('2d').putImageData(d, 0, 0);
      await worker.setParameters({ tessedit_pageseg_mode: '6' });
      const { data } = await worker.recognize(canvas);
      const lines = (data.lines || []).map((l) => l.text.trim()).filter(Boolean);
      rows = guessRows(lines.map(parseNumbers), round); raw = lines.join('\n');
    }
    window.__ocrDebug = { raw, rows };
    if (cancelled) return;
    showOcrReview(round, rows, onApplied, raw);
  } catch (err) {
    console.error(err);
    openModal(`<h2 style="margin-top:0">Couldn't read the photo</h2><p>${esc(err.message || err)}</p><p class="muted">The photo is saved — you can type the scores into the card while looking at it.</p><button class="btn primary block" id="o-ok">OK</button>`, (s) => ($('#o-ok', s).onclick = closeModal));
  }
}
function showOcrReview(round, rows, onApplied, rawText) {
  const n = round.holes;
  const targetOpts = (sel) => [['ignore', 'Ignore this row'], ['par', 'Par'], ['si', 'Handicap (hole)'], ...round.players.map((p, i) => ['p' + i, p.name]), ...round.players.map((p, i) => ['u' + i, p.name + ' — putts'])]
    .map(([v, l]) => `<option value="${v}" ${v === sel ? 'selected' : ''}>${esc(l)}</option>`).join('');
  const startOpts = (sel) => (n === 18 ? `<select class="o-start" style="width:auto"><option value="0" ${sel === 0 ? 'selected' : ''}>from hole 1</option><option value="9" ${sel === 9 ? 'selected' : ''}>from hole 10</option></select>` : '');
  openModal(`<h2 style="margin-top:0">Check what was read</h2>
    ${rows.length ? `<p class="muted small">Each row found on the card is below. Choose what each row is, then fix any wrong numbers. A dot (·) is an empty box.</p>
    ${rows.map((r, k) => `<div class="ocr-row" data-k="${k}">
      <div class="row"><select class="o-target grow" style="width:auto">${targetOpts(r.target)}</select>${startOpts(r.start)}</div>
      <input type="text" class="o-vals" value="${r.vals.map((v) => v ?? '·').join(' ')}" inputmode="numeric" style="margin-top:6px;letter-spacing:1px">
    </div>`).join('')}` : `<p>No rows of numbers were found. Try a sharper, flatter photo — or type the scores in while looking at the photo.</p>`}
    <details><summary class="small muted">Raw text read</summary><pre class="small" style="white-space:pre-wrap">${esc(rawText || '')}</pre></details>
    <div class="row" style="margin-top:12px"><button class="btn grow" id="o-close">Cancel</button>${rows.length ? '<button class="btn primary grow" id="o-apply">Fill scorecard</button>' : ''}</div>`, (s) => {
    $('#o-close', s).onclick = closeModal;
    const apply = $('#o-apply', s);
    if (apply) apply.onclick = () => {
      let filled = 0;
      $$('.ocr-row', s).forEach((el) => {
        const target = $('.o-target', el).value; if (target === 'ignore') return;
        const start = +($('.o-start', el)?.value || 0);
        const vals = $('.o-vals', el).value.trim().split(/[\s,]+/).map((x) => parseInt(x, 10));
        vals.forEach((v, j) => {
          const i = start + j; if (i >= n || isNaN(v)) return;
          if (target === 'par') round.par[i] = v; else if (target === 'si') round.si[i] = v;
          else if (target[0] === 'u') { const rp = round.players[+target.slice(1)]; (rp.putts = rp.putts || [])[i] = v; }
          else round.players[+target.slice(1)].scores[i] = v;
          ocrCells.add(target + ':' + i); filled++;
        });
      });
      closeModal(); toast(`Filled ${filled} boxes — please check the yellow ones.`); onApplied();
    };
  });
}

/* ---------------- players ---------------- */
function viewPlayers() {
  $('#app').innerHTML = `<h1>Players</h1>
    ${db.players.map((p) => { const c = computeIndex(p); return `<a class="list-item" href="#player/${p.id}"><span><span class="title">${esc(p.name)}</span><br><span class="muted small">${p.autoAdjust ? c.method : 'Manual handicap'}</span></span><span class="pill">HCP ${fmtHcp(p.index)}</span></a>`; }).join('') || '<p class="muted">No players yet.</p>'}
    <div class="card"><h3 style="margin-top:0">Add player</h3><div class="row"><input type="text" id="pl-name" class="grow" placeholder="Name" style="width:auto"><input type="number" step="0.1" id="pl-hcp" placeholder="Handicap" style="width:110px"><button class="btn primary" id="pl-add">Add</button></div></div>`;
  $('#pl-add').onclick = () => { const name = $('#pl-name').value.trim(); if (!name) return; newPlayer(name, num($('#pl-hcp').value) ?? 28); save(); render(); };
}
function viewPlayer(id) {
  const p = getPlayer(id); if (!p) return go('players');
  const c = computeIndex(p); const diffs = playerDifferentials(p.id);
  const rounds = db.rounds.filter((r) => r.players.some((rp) => rp.playerId === p.id)).sort((a, b) => (a.date < b.date ? 1 : -1));
  const stats = rounds.map((r) => playerStats(r, r.players.find((rp) => rp.playerId === p.id))).filter((s) => s.played === s.strokes.length);
  const grosses18 = rounds.filter((r) => r.holes === 18).map((r) => playerStats(r, r.players.find((rp) => rp.playerId === p.id))).filter((s) => s.played === 18).map((s) => s.gross);
  const best = new Set([...diffs.slice(-20)].sort((a, b) => a.diff - b.diff).slice(0, (WHS_TABLE[Math.min(20, diffs.length)] || [0])[0]).map((d) => d.roundId));
  $('#app').innerHTML = `<a href="#players" class="muted small">‹ Players</a>
    <div class="card stack">
      <label class="field">Name<input type="text" id="pp-name" value="${esc(p.name)}"></label>
      <div class="row spread"><div><div class="muted small">Current handicap</div><div style="font-size:2rem;font-weight:700">${fmtHcp(p.index)}</div><div class="muted small">${p.autoAdjust ? esc(c.method) : 'Manual — not auto-adjusted'}</div></div>
      <div class="stack" style="width:170px"><label class="field">Set handicap<input type="number" step="0.1" id="pp-set" placeholder="${fmtHcp(p.index)}"></label><button class="btn small" id="pp-setbtn">Save handicap</button></div></div>
      <label class="check"><input type="checkbox" id="pp-auto" ${p.autoAdjust ? 'checked' : ''}> Adjust handicap automatically from my scores</label>
      <p class="muted small" style="margin:0">Setting a handicap manually restarts the auto-adjustment from that number; earlier rounds stay in your record but no longer count.</p>
    </div>
    <div class="card"><h3 style="margin-top:0">Stats</h3>
      <div class="grid3"><div><div class="muted small">Rounds</div><strong>${rounds.length}</strong></div><div><div class="muted small">Avg 18-hole gross</div><strong>${grosses18.length ? (sum(grosses18) / grosses18.length).toFixed(1) : '–'}</strong></div><div><div class="muted small">Best 18-hole gross</div><strong>${grosses18.length ? Math.min(...grosses18) : '–'}</strong></div></div>
      ${(() => { const all = rounds.map((r) => playerStats(r, r.players.find((rp) => rp.playerId === p.id)));
        const dh = sum(all.map((x) => x.driveHoles)), ph = sum(all.map((x) => x.puttHoles)), gh = sum(all.map((x) => x.girHoles));
        const pct = (a, b) => (b ? Math.round((100 * a) / b) + '%' : '–');
        const three = sum(rounds.map((r) => (r.players.find((rp) => rp.playerId === p.id).putts || []).filter((v) => num(v) >= 3).length));
        return `<div class="grid3" style="margin-top:10px"><div><div class="muted small">Fairways hit</div><strong>${pct(sum(all.map((x) => x.fw)), dh)}</strong></div><div><div class="muted small">Rough / hazard</div><strong>${pct(sum(all.map((x) => x.rough)), dh)} / ${pct(sum(all.map((x) => x.haz)), dh)}</strong></div><div><div class="muted small">Putts per 18</div><strong>${ph ? ((18 * sum(all.map((x) => x.puttTot))) / ph).toFixed(1) : '–'}</strong></div><div><div class="muted small">Greens in reg.</div><strong>${pct(sum(all.map((x) => x.gir)), gh)}</strong></div><div><div class="muted small">3-putt holes</div><strong>${three}</strong></div></div>`; })()}
      <h3>Handicap trend</h3>${sparkline(p.history.map((h) => -h.index)) || '<p class="muted small">Play a few rounds to see a trend.</p>'}
    </div>
    <div class="card"><h3 style="margin-top:0">Score differentials (counting rounds)</h3>
      ${diffs.length ? `<table class="summary"><tr><th>Date</th><th>Course</th><th>Diff</th></tr>${[...diffs].reverse().map((d) => { const r = db.rounds.find((x) => x.id === d.roundId); return `<tr><td>${fmtDate(d.date)}</td><td><a href="#round/${d.roundId}">${esc(r?.courseName)}</a></td><td>${best.has(d.roundId) && diffs.length >= 3 ? '<strong>' + fmt1(d.diff) + '*</strong>' : fmt1(d.diff)}</td></tr>`; }).join('')}</table><p class="muted small">* used in the current handicap.</p>` : '<p class="muted small">No finished rounds since the handicap was last set.</p>'}
    </div>
    <div class="card"><h3 style="margin-top:0">Handicap history</h3>
      <table class="summary"><tr><th>Date</th><th>Reason</th><th>HCP</th></tr>${[...p.history].reverse().map((h) => `<tr><td>${fmtDate(h.date)}</td><td class="small">${esc(h.reason)}</td><td>${fmtHcp(h.index)}</td></tr>`).join('')}</table>
    </div>
    <button class="btn danger" id="pp-del">Delete player</button>`;
  $('#pp-name').onchange = (e) => { const v = e.target.value.trim(); if (!v) return; p.name = v; db.rounds.forEach((r) => r.players.forEach((rp) => { if (rp.playerId === p.id) rp.name = v; })); save(); };
  $('#pp-setbtn').onclick = () => { const v = num($('#pp-set').value); if (v == null) return toast('Enter a handicap'); setManualHandicap(p, v); save(); render(); toast('Handicap saved'); };
  $('#pp-auto').onchange = (e) => { p.autoAdjust = e.target.checked; if (p.autoAdjust) recalcHandicaps('Auto-adjust turned on'); save(); render(); };
  $('#pp-del').onclick = async () => {
    if (rounds.length && !(await confirmBox(`${p.name} is in ${rounds.length} round(s). Delete the player? Their scores stay in those rounds.`))) return;
    db.players = db.players.filter((x) => x !== p); save(); go('players');
  };
}

/* ---------------- courses ---------------- */
function viewCourses() {
  $('#app').innerHTML = `<h1>Courses</h1>
    ${[...db.courses].sort((a, b) => a.name.localeCompare(b.name)).map((c) => `<a class="list-item" href="#course/${c.id}"><span><span class="title">${esc(c.name)}</span><br><span class="muted small">${c.tee ? esc(c.tee) + ' · ' : ''}${c.holes} holes · par ${sum(c.par.slice(0, c.holes).map(num))}${c.rating ? ` · ${c.rating}/${c.slope || 113}` : ''}</span></span><span class="muted small">${db.rounds.filter((r) => r.courseId === c.id).length} rounds</span></a>`).join('') || '<p class="muted">Courses are saved automatically when you start a round.</p>'}
    <button class="btn" id="co-add">＋ Add course</button>`;
  $('#co-add').onclick = () => { const c = { id: uid(), name: 'New course', tee: '', holes: 18, par: defaultPar(18), si: [], rating: null, slope: null, createdAt: Date.now() }; db.courses.push(c); save(); go('course/' + c.id); };
}
function viewCourse(id) {
  const c = getCourse(id); if (!c) return go('courses');
  const cols = [...Array(c.holes)].map((_, i) => i);
  $('#app').innerHTML = `<a href="#courses" class="muted small">‹ Courses</a>
    <div class="card stack">
      <label class="field">Course name<input type="text" id="c-name" value="${esc(c.name)}"></label>
      <div class="grid2"><label class="field">Tee<input type="text" id="c-tee" value="${esc(c.tee)}"></label><label class="field">Holes<select id="c-holes"><option ${c.holes === 18 ? 'selected' : ''}>18</option><option ${c.holes === 9 ? 'selected' : ''}>9</option></select></label></div>
      <div class="grid2"><label class="field">Course rating<input type="number" step="0.1" id="c-rating" value="${c.rating ?? ''}"></label><label class="field">Slope<input type="number" id="c-slope" value="${c.slope ?? ''}" placeholder="113"></label></div>
    </div>
    <div class="card"><div class="sc-wrap"><table class="sc">
      <tr><th class="name">Hole</th>${cols.map((i) => `<th>${i + 1}</th>`).join('')}</tr>
      <tr><td class="name">Par</td>${cols.map((i) => `<td><input type="number" inputmode="numeric" data-k="par" data-i="${i}" value="${c.par[i] ?? ''}"></td>`).join('')}</tr>
      <tr><td class="name">Handicap</td>${cols.map((i) => `<td><input type="number" inputmode="numeric" data-k="si" data-i="${i}" value="${c.si[i] ?? ''}"></td>`).join('')}</tr>
    </table></div><p class="muted small">Par ${sum(c.par.slice(0, c.holes).map(num))}. New rounds at this course start with these values.</p></div>
    <button class="btn danger" id="c-del">Delete course</button>`;
  const upd = (f) => (e) => { f(e.target.value); save(); };
  $('#c-name').onchange = upd((v) => (c.name = v.trim() || c.name));
  $('#c-tee').onchange = upd((v) => (c.tee = v.trim()));
  $('#c-rating').onchange = upd((v) => (c.rating = num(v)));
  $('#c-slope').onchange = upd((v) => (c.slope = num(v)));
  $('#c-holes').onchange = (e) => { c.holes = +e.target.value; if (c.par.length < c.holes) c.par = c.par.concat(defaultPar(18).slice(c.par.length, c.holes)); save(); render(); };
  $$('table.sc input').forEach((inp) => (inp.onchange = () => { c[inp.dataset.k][+inp.dataset.i] = num(inp.value); save(); }));
  $('#c-del').onclick = async () => { if (await confirmBox('Delete this course? Rounds played here are kept.')) { db.courses = db.courses.filter((x) => x !== c); save(); go('courses'); } };
}

/* ---------------- backup ---------------- */
function blobToDataUrl(b) { return new Promise((res) => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(b); }); }
async function dataUrlToBlob(u) { return (await fetch(u)).blob(); }
async function buildBackup(withPhotos) {
  const out = { app: 'golf-scorecard', exportedAt: new Date().toISOString(), data: db, photos: {} };
  if (withPhotos) for (const r of db.rounds) for (const pid of r.photoIds) { const b = await idb.get('photos', pid).catch(() => null); if (b) out.photos[pid] = await blobToDataUrl(b); }
  return JSON.stringify(out);
}
async function viewBackup() {
  const last = db.settings.lastBackup;
  let snaps = []; try { snaps = (await idb.keys('snapshots')).sort().reverse(); } catch {}
  let used = ''; try { const e = await navigator.storage?.estimate?.(); if (e) used = `${(e.usage / 1048576).toFixed(1)} MB used on this device.`; } catch {}
  let persisted = false; try { persisted = await navigator.storage?.persisted?.(); } catch {}
  $('#app').innerHTML = `<h1>Backup</h1>
    <div class="card stack">
      <p style="margin:0">Everything is stored only on this phone. Save a backup file to Files / iCloud / Google Drive, or send it to yourself, so you never lose your record.</p>
      <p class="muted small" style="margin:0">Last backup: <strong>${last ? new Date(last).toLocaleString() : 'never'}</strong>. ${db.rounds.length} rounds, ${db.players.length} players, ${db.courses.length} courses. ${used}</p>
      <label class="check"><input type="checkbox" id="b-photos" checked> Include scorecard photos (bigger file)</label>
      <div class="row"><button class="btn primary grow" id="b-save">⬇︎ Save backup file</button><button class="btn grow" id="b-share">Share…</button></div>
    </div>
    <div class="card stack">
      <h3 style="margin:0">Restore</h3>
      <p class="muted small" style="margin:0">Open a backup file. <strong>Merge</strong> adds rounds you don't have (good for combining two phones). <strong>Replace</strong> makes this phone exactly like the backup.</p>
      <label class="btn">📂 Open backup file<input type="file" id="b-file" accept=".json,application/json" hidden></label>
    </div>
    <div class="card stack">
      <h3 style="margin:0">Automatic restore points</h3>
      <p class="muted small" style="margin:0">The app keeps a copy of your data from each of the last 10 days you used it (on this device only).</p>
      ${snaps.length ? snaps.map((k) => `<div class="row spread"><span>${fmtDate(k)}</span><button class="btn small" data-snap="${k}">Restore</button></div>`).join('') : '<p class="muted small">None yet.</p>'}
    </div>
    <div class="card stack">
      <h3 style="margin:0">Storage</h3>
      <p class="muted small" style="margin:0">${persisted ? '✅ This browser has agreed to keep the app data permanently.' : 'Ask the browser to keep data permanently (helps stop it being cleared when the phone is low on space). Adding the app to your home screen also helps.'}</p>
      ${persisted ? '' : '<button class="btn small" id="b-persist">Keep my data</button>'}
      <button class="btn small danger" id="b-wipe">Erase everything on this device</button>
    </div>`;
  const fname = () => `golf-scorecard-backup-${today()}.json`;
  const markDone = () => { db.settings.lastBackup = Date.now(); save(); };
  $('#b-save').onclick = async () => { download(fname(), await buildBackup($('#b-photos').checked)); markDone(); toast('Backup saved'); setTimeout(render, 300); };
  $('#b-share').onclick = async () => {
    const text = await buildBackup($('#b-photos').checked);
    const file = new File([text], fname(), { type: 'application/json' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try { await navigator.share({ files: [file], title: 'Golf scorecard backup' }); markDone(); render(); } catch (e) { if (e.name !== 'AbortError') toast('Share failed'); }
    } else { download(fname(), text); markDone(); toast('Sharing not supported here — file downloaded instead'); }
  };
  $('#b-file').onchange = async (e) => {
    const f = e.target.files[0]; if (!f) return; e.target.value = '';
    let parsed; try { parsed = JSON.parse(await f.text()); } catch { return toast('That file is not a valid backup'); }
    if (parsed?.app !== 'golf-scorecard' || !parsed.data) return toast('That file is not a Golf Scorecard backup');
    const d = parsed.data;
    openModal(`<h2 style="margin-top:0">Restore backup</h2><p>From ${esc(new Date(parsed.exportedAt).toLocaleString())}: ${d.rounds?.length || 0} rounds, ${d.players?.length || 0} players, ${d.courses?.length || 0} courses${Object.keys(parsed.photos || {}).length ? `, ${Object.keys(parsed.photos).length} photos` : ''}.</p>
      <div class="stack"><button class="btn primary block" id="m-merge">Merge into this phone</button><button class="btn block danger" id="m-replace">Replace everything on this phone</button><button class="btn block" id="m-cancel">Cancel</button></div>`, (s) => {
      $('#m-cancel', s).onclick = closeModal;
      const finish = async (mode) => {
        for (const [pid, u] of Object.entries(parsed.photos || {})) { try { await idb.put('photos', pid, await dataUrlToBlob(u)); } catch {} }
        if (mode === 'replace') db = migrate(d);
        else {
          const merged = migrate(JSON.parse(JSON.stringify(db))); const inc = migrate(d);
          for (const key of ['players', 'courses', 'rounds']) {
            const ids = new Map(merged[key].map((x) => [x.id, x]));
            inc[key].forEach((x) => { const mine = ids.get(x.id); if (!mine) merged[key].push(x); else if ((x.updatedAt || 0) > (mine.updatedAt || 0) && key === 'rounds') Object.assign(mine, x); });
          }
          db = merged; recalcHandicaps('Merged backup');
        }
        save(); closeModal(); toast('Backup restored'); go('home');
      };
      $('#m-merge', s).onclick = () => finish('merge');
      $('#m-replace', s).onclick = async () => { if (await confirmBox('Replace ALL data on this phone with the backup?')) finish('replace'); };
    });
  };
  $$('[data-snap]').forEach((b) => (b.onclick = async () => {
    if (!(await confirmBox(`Restore your data to how it was on ${fmtDate(b.dataset.snap)}? Make a backup first if unsure.`))) return;
    const raw = await idb.get('snapshots', b.dataset.snap); if (!raw) return; db = migrate(JSON.parse(raw)); save(); toast('Restored'); go('home');
  }));
  const pb = $('#b-persist'); if (pb) pb.onclick = async () => { const ok = await navigator.storage?.persist?.(); toast(ok ? 'Data will be kept' : 'The browser said no — add the app to your home screen and try again'); render(); };
  $('#b-wipe').onclick = async () => {
    if (!(await confirmBox('Erase ALL rounds, players, courses and photos on this device?'))) return;
    if (!(await confirmBox('Really erase everything? Only a backup file can bring it back.'))) return;
    for (const k of await idb.keys('photos')) await idb.del('photos', k);
    db = blankDb(); save(); go('home');
  };
}

/* ---------------- boot ---------------- */
if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
  navigator.serviceWorker.register('sw.js').catch((e) => console.warn('SW failed', e));
}
try { navigator.storage?.persist?.(); } catch {}
render();
