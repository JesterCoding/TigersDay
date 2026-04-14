const statusBar      = document.getElementById('status-bar');
const gameStatePanel = document.getElementById('game-state-panel');
let ws = null;
let lastState = null;
const SVG_NS = 'http://www.w3.org/2000/svg';

const tooltip   = document.getElementById('tooltip');
const infoPanel = document.getElementById('info-panel');
const actionBtns = document.getElementById('action-buttons');
let selectedTerritoryName = null;
let selectedSource = null;
let currentBitString = ""; 

var NODES = {
  Bombay:        { x:110, y: 74,  owner:'british', armyType:'active',  key:true,  coast:true,  labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Hyderabad:     { x:515, y:100,  owner:'british', armyType:'active',  key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Madras:        { x:618, y:322,  owner:'british', armyType:'active',  key:true,  coast:true,  labelAnchor:{anchor:'end',    dx:-18, dy:-24} },
  Seringapatam:  { x:230, y:480,  owner:'mysore',  armyType:'fort',    key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Coimbatore:    { x:305, y:600,  owner:'mysore',  armyType:'fort',    key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Satara:        { x:255, y:128,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Poona:         { x:345, y:70,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Raichur:        { x:390, y:178,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Masulipatam:   { x:656, y:162,  owner:'empty',   armyType:'empty',   key:false, coast:true,  labelAnchor:{anchor:'end',   dx:-12, dy:-16} },
  Goa:           { x: 94, y:262,  owner:'empty',   armyType:'empty',   key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Darwar:        { x:232, y:232,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Anantapur:     { x:470, y:228,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Chitaldoorg:       { x:250, y:350,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Mangalore:     { x:118, y:398,  owner:'mysore',  armyType:'fort',    key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Bangalore:     { x:350, y:400,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Vellore:       { x:460, y:340,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  'Mahé':        { x:145, y:586,  owner:'mysore',  armyType:'fort',    key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Pondicherry:   { x:610, y:446,  owner:'empty',   armyType:'empty',   key:false, coast:true,  labelAnchor:{anchor:'end',   dx:-12, dy:-16} },
  Erode:         { x:405, y:515,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Trichy:        { x:506, y:580,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Alwaye:        { x:225, y:720,  owner:'mysore',  armyType:'empty',    key:false, coast:false },
  Dindigul:      { x:415, y:670,  owner:'empty',   armyType:'fort',   key:false, coast:false },
  Ramnad:        { x:415, y:770,  owner:'empty',   armyType:'empty',   key:false, coast:true },
  Travancore:    { x:260, y:830,  owner:'british', armyType:'active',  key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Ceylon:        { x:540, y:800,  owner:'empty',   armyType:'empty',   key:false, coast:true  },
};

const EDGES = [
  ['Bombay', 'Satara'],
  ['Bombay', 'Goa', {curve: -0.2}],
  ['Hyderabad', 'Raichur'],
  ['Hyderabad', 'Masulipatam'],
  ['Hyderabad', 'Anantapur'],
  ['Madras', 'Masulipatam', {curve: -0.2}],
  ['Madras', 'Anantapur'],
  ['Madras', 'Vellore'],
  ['Madras', 'Pondicherry'],
  ['Seringapatam', 'Mangalore'],
  ['Seringapatam', 'Bangalore'],
  ['Seringapatam', 'Mahé'],
  ['Seringapatam', 'Erode'],
  ['Coimbatore', 'Mahé'],
  ['Coimbatore', 'Erode'],
  ['Coimbatore', 'Alwaye'],
  ['Coimbatore', 'Dindigul'],
  ['Satara', 'Raichur'],
  ['Satara', 'Darwar'],
  ['Poona', 'Satara'],
  ['Poona', 'Hyderabad'],
  ['Poona', 'Bombay'],
  ['Raichur', 'Anantapur'],
  ['Raichur', 'Chitaldoorg'],
  ['Goa', 'Darwar'],
  ['Goa', 'Mangalore', {curve: -0.2}],
  ['Darwar', 'Chitaldoorg'],
  ['Anantapur', 'Vellore'],
  ['Chitaldoorg', 'Mangalore'],
  ['Chitaldoorg', 'Bangalore'],
  ['Bangalore', 'Vellore'],
  ['Vellore', 'Erode'],
  ['Pondicherry', 'Erode'],
  ['Pondicherry', 'Trichy'],
  ['Erode', 'Trichy'],
  ['Trichy', 'Dindigul'],
  ['Trichy', 'Ceylon', {curve: -0.2}],
  ['Alwaye', 'Travancore'],
  ['Alwaye', 'Ramnad'],
  ['Dindigul', 'Ramnad'],
  ['Ramnad', 'Ceylon'],
  ['Ramnad', 'Travancore'],
  ['Travancore', 'Ceylon']
];

const adjacency = {};
for (const [a, b] of EDGES) {
  (adjacency[a] = adjacency[a] || []).push(b);
  (adjacency[b] = adjacency[b] || []).push(a);
}
for (const k of Object.keys(adjacency)) adjacency[k] = [...new Set(adjacency[k])];

const BRITISH_CARD_DATA = [
  { name: 'Wall Breach (3)',      icon: '💥',  desc: 'Powerful' },
  { name: 'Highlanders (2)',      icon: '🟥',  desc: 'Deploy a Fresh Army on Coast' },
  { name: 'Royal Navy (2)',       icon: '⚓',  desc: 'Move an Army to any Coast' },
  { name: 'Divide and Rule (1)',  icon: '🤝',  desc: 'Move a Fort not in a Key' },
  { name: 'Force March (1)',      icon: '🥾',  desc: 'Move a Tired Army' },
  { name: 'Princely States (1)',  icon: '🏰',  desc: 'Deploy a Tired Army in a Key' },
];

const MYSORE_CARD_DATA = [
  { name: 'Iron Rockets (3)',     icon: '🚀',  desc: 'Powerful' },
  { name: 'Sepoy Mutiny (2)',     icon: '⚔️',  desc: 'Remove an Army not in a Key' },
  { name: 'French Alliance (2)',  icon: '💠',  desc: 'Deploy a Fort adjacent to another' },
  { name: 'Monsoon (1)',          icon: '🌧️',  desc: 'Flip a Fresh Army to Tired' },
  { name: 'Cavalry Raid (1)',     icon: '🏇',  desc: 'British discard' },
  { name: 'Sea Trade (1)',        icon: '🪙',  desc: 'Move a Fort from Coast to any' },
];



function splineControlPoint(ax, ay, bx, by, f=0.18) {
  const mx=(ax+bx)/2, my=(ay+by)/2, dx=bx-ax, dy=by-ay;
  const len=Math.sqrt(dx*dx+dy*dy);
  return { cx: mx+(-dy/len)*len*f, cy: my+(dx/len)*len*f };
}

function renderEdges() {
  const layer = document.getElementById('edge-layer');
  layer.innerHTML = '';
  for (const edge of EDGES) {
    const [aName, bName, opts={}] = edge;
    const a=NODES[aName], b=NODES[bName];
    if (!a||!b) continue;
    const {cx,cy} = splineControlPoint(a.x,a.y,b.x,b.y, opts.curve||0.15);
    const path = document.createElementNS(SVG_NS,'path');
    path.setAttribute('d',`M ${a.x},${a.y} Q ${cx},${cy} ${b.x},${b.y}`);
    path.setAttribute('fill','none');
    path.setAttribute('stroke','#6a4c1e');
    path.setAttribute('stroke-width','1.6');
    path.setAttribute('stroke-linecap','round');
    if (opts.sea) { path.setAttribute('stroke-dasharray','5,4'); path.setAttribute('opacity','0.55'); }
    else          { path.setAttribute('opacity','0.68'); }
    layer.appendChild(path);
  }
}

window.updateCombatInfo = function(turnNum, whoMove, attacker, defender, strength) {
    document.getElementById('ui-turn-number').innerText = turnNum;
    document.getElementById('ui-who-move').innerText = whoMove;
    document.getElementById('ui-attacker').innerText = attacker;
    document.getElementById('ui-defender').innerText = defender;
    document.getElementById('ui-combat-strength').innerText = strength;
};

window.renderNodes = function renderNodes() {
  const layer = document.getElementById('node-layer');
  layer.innerHTML = '';
  for (const [name, data] of Object.entries(window.NODES)) {
    const {x, y, owner, key, coast} = data;
    const armyType = data.armyType || 'empty';
    const la = data.labelAnchor || {anchor:'middle', dx:0, dy: key?-24:-16};
    const anchor = la.anchor||'middle', ldx=la.dx||0, ldy=la.dy||(key?-24:-16);

    const g = document.createElementNS(SVG_NS,'g');
    g.setAttribute('class','node-group');
    g.setAttribute('transform',`translate(${x},${y})`);
    g.dataset.name=name; g.dataset.owner=owner;
    g.dataset.armyType=armyType;
    g.dataset.key=String(key); g.dataset.coast=String(coast);
    g.addEventListener('click', ()=>handleNodeClick(g));
    g.addEventListener('mousemove', tooltipShow);
    g.addEventListener('mouseleave', tooltipHide);

    const ring = document.createElementNS(SVG_NS,'circle');
    ring.setAttribute('class','sel-ring');
    ring.setAttribute('r', key?'22':'15');
    ring.setAttribute('fill','none'); ring.setAttribute('stroke','#d4a030');
    ring.setAttribute('stroke-width','2'); ring.setAttribute('opacity','0');
    g.appendChild(ring);

    if (key) {
      const sq = document.createElementNS(SVG_NS,'rect');
      sq.setAttribute('x','-18'); sq.setAttribute('y','-18');
      sq.setAttribute('width','36'); sq.setAttribute('height','36');
      sq.setAttribute('fill','#1c1814'); sq.setAttribute('stroke','#999');
      sq.setAttribute('stroke-width','1.5');
      g.appendChild(sq);
    } else {
      const circ=document.createElementNS(SVG_NS,'circle');
      circ.setAttribute('r','10'); circ.setAttribute('fill','#2a2420');
      circ.setAttribute('stroke','#b0a080'); circ.setAttribute('stroke-width','1.4');
      g.appendChild(circ);
    }

    if (armyType === 'fort') {
      const p = document.createElementNS(SVG_NS,'polygon');
      p.setAttribute('points','0,-22 22,0 0,22 -22,0');
      p.setAttribute('fill','#2e7a2e');
      p.setAttribute('filter','url(#nshadow)');
      g.appendChild(p);

    } else if (armyType === 'active' || armyType === 'tired') {
      const isTired = armyType === 'tired';
      const opacity = isTired ? '0.55' : '1';

      if (owner === 'british') {
        const p = document.createElementNS(SVG_NS,'rect');
        p.setAttribute('x','-18'); p.setAttribute('y','-18');
        p.setAttribute('width','36'); p.setAttribute('height','36');
        p.setAttribute('fill','#c0281a');
        p.setAttribute('opacity', opacity);
        p.setAttribute('filter','url(#nshadow)');
        g.appendChild(p);
      } else if (owner === 'mysore') {
        const p = document.createElementNS(SVG_NS,'polygon');
        p.setAttribute('points','0,-25 25,0 0,25 -25,0');
        p.setAttribute('fill','#2e7a2e');
        p.setAttribute('opacity', opacity);
        p.setAttribute('filter','url(#nshadow)');
        g.appendChild(p);
      }

      if (isTired) {
        const slash = document.createElementNS(SVG_NS,'line');
        slash.setAttribute('x1','-13'); slash.setAttribute('y1','-13');
        slash.setAttribute('x2','13'); slash.setAttribute('y2','13');
        slash.setAttribute('stroke','rgba(255,255,255,0.85)');
        slash.setAttribute('stroke-width','3');
        slash.setAttribute('stroke-linecap','round');
        g.appendChild(slash);
      }
    }

    const makeLabel = isHalo => {
      const t=document.createElementNS(SVG_NS,'text');
      t.setAttribute('dy',String(ldy)); t.setAttribute('dx',String(ldx));
      t.setAttribute('text-anchor',anchor);
      t.setAttribute('font-family', key?'Cinzel,serif':'Cormorant Garamond,serif');
      t.setAttribute('font-size', key?'22':'20'); t.setAttribute('font-weight','700');
      if (key) t.setAttribute('letter-spacing','.06em');
      if (isHalo) {
        t.setAttribute('stroke','rgba(228,213,155,0.92)'); t.setAttribute('stroke-width','4');
        t.setAttribute('stroke-linejoin','round'); t.setAttribute('fill','none');
        t.setAttribute('paint-order','stroke');
      } else { t.setAttribute('fill','#1a1208'); }
      t.textContent = name;
      return t;
    };
    g.appendChild(makeLabel(true));
    g.appendChild(makeLabel(false));
    layer.appendChild(g);
  }
}

window.renderCards = function renderCards(britishAvail, mysoreAvail) {
  const bList = document.getElementById('british-cards-list');
  const mList = document.getElementById('mysore-cards-list');
  bList.innerHTML = '';
  mList.innerHTML = '';

  BRITISH_CARD_DATA.forEach((card, i) => {
    const div = document.createElement('div');
    const usable = britishAvail[i];
    div.className = 'player-card british-card' + (usable ? '' : ' used');
    div.innerHTML = `<span class="used-badge">USED</span><span class="card-icon">${card.icon}</span><div class="card-name">${card.name}</div><div class="card-desc">${card.desc}</div>`;
    if (usable) { div.title = 'Click to play this card'; div.addEventListener('click', () => playCard('british', i)); }
    bList.appendChild(div);
  });

  MYSORE_CARD_DATA.forEach((card, i) => {
    const div = document.createElement('div');
    const usable = mysoreAvail[i];
    div.className = 'player-card mysore-card' + (usable ? '' : ' used');
    div.innerHTML = `<span class="used-badge">USED</span><span class="card-icon">${card.icon}</span><div class="card-name">${card.name}</div><div class="card-desc">${card.desc}</div>`;
    if (usable) { div.title = 'Click to play this card'; div.addEventListener('click', () => playCard('mysore', i)); }
    mList.appendChild(div);
  });
}

function updateInfoPanel(name, owner, armyType, key, coast) {
  selectedTerritoryName = name;
  const adj = (adjacency[name]||[]).join(', ') || '—';
  const ownerColor = { british:'#c0281a', mysore:'#2e7a2e', empty:'#666' };
  const col = ownerColor[owner]||'#666';
  const label = owner==='empty' ? 'Unoccupied' : owner.charAt(0).toUpperCase()+owner.slice(1);
  const armyLabel = { active:'⚔ Fresh Army', tired:'😴 Tired Army', fort:'🏰 Fort', empty:'—' };
  infoPanel.innerHTML = `
    <strong style="font-family:Cinzel,serif;font-size:.82rem">${name}</strong><br>
    <span style="color:${col}">${label}</span>
    &nbsp;<em style="font-size:.78rem">${armyLabel[armyType]||''}</em>
    ${key==='true'  ? '<br><em style="font-size:.78rem">⬛ Key City</em>' : ''}
    ${coast==='true'? '<br><em style="font-size:.78rem">🌊 Coastal</em>'  : ''}
    <br><span style="color:#8a6830;font-size:.76rem;letter-spacing:.04em">ADJACENT:</span><br>
    <span style="font-size:.8rem">${adj}</span>
  `;
  const hasArmy = armyType === 'active' || armyType === 'tired';
  actionBtns.style.display = hasArmy ? 'flex' : 'none';
}

function tooltipShow(e) {
  const g=e.currentTarget;
  const armyType = g.dataset.armyType || 'empty';
  const owner = g.dataset.owner==='empty' ? 'Unoccupied' : g.dataset.owner;
  const armyLabel = { active:' · Fresh', tired:' · Tired', fort:' · Fort', empty:'' };
  tooltip.innerHTML=`<b>${g.dataset.name}</b>${owner}${armyLabel[armyType]||''}`;
  tooltip.classList.add('show');
  tooltip.style.left=(e.clientX+14)+'px'; tooltip.style.top=(e.clientY+14)+'px';
}
function tooltipHide() { tooltip.classList.remove('show'); }

function handleNodeClick(g) {
  const name     = g.dataset.name;
  const owner    = g.dataset.owner;
  const armyType = g.dataset.armyType || 'empty';

  updateInfoPanel(name, owner, armyType, g.dataset.key, g.dataset.coast);
  document.querySelectorAll('.sel-ring').forEach(r => r.setAttribute('opacity','0'));

  if (!selectedSource) {
    selectedSource = name;
    g.querySelector('.sel-ring').setAttribute('opacity','1');
  } else {
    if (selectedSource === name) { selectedSource = null; } 
    else { const from = selectedSource; selectedSource = null; sendMove(from, name); }
  }
}

function handleServerMessage(msg) {
  switch (msg.type) {
    case 'STATE':
      lastState = msg;
      applyBoard(msg.territories);
      renderCards(msg.britishCards, msg.mysoreCards);
      updateGameStatePanel(msg.turn, msg.maxTurns, msg.whoToMove, msg.winner);
      break;
    case 'MOVE_RESULT':
      if (msg.status === 'invalid') { flashStatus('⚠ &nbsp;' + msg.reason, 1800); } 
      else {
        applyBoard(msg.territories);
        renderCards(msg.britishCards || [], msg.mysoreCards || []);
        updateGameStatePanel(msg.turn, msg.maxTurns||4, msg.whoToMove, msg.winner);
        if (msg.winner) showGameOver(msg.winner);
      }
      break;
    case 'GAME_OVER': showGameOver(msg.winner); break;
  }
}

function applyBoard(territories) {
  if (!territories) return;
  for (const t of territories) {
    if (NODES[t.name]) {
      NODES[t.name].owner    = t.owner;
      NODES[t.name].armyType = t.armyType;
    }
  }
  window.renderNodes();
}

function updateGameStatePanel(turn, maxTurns, whoToMove, winner) {
  if (winner) {
    const col = winner === 'british' ? '#c0281a' : '#2e7a2e';
    gameStatePanel.innerHTML = `<strong style="color:${col}">GAME OVER</strong><br><span style="color:${col}">${capitalize(winner)} wins!</span>`;
    return;
  }
  const phaseColor = whoToMove === 'British Move' ? '#c0281a' : whoToMove === 'Mysore Card'  ? '#2e7a2e' : '#c8a030';
  gameStatePanel.innerHTML = `Turn <strong>${turn}</strong> of <strong>${maxTurns}</strong><br><span style="color:${phaseColor};font-weight:700">${whoToMove||'—'}</span>`;
}

function setStatus(cls, html) { statusBar.className = cls; statusBar.innerHTML = html; }
function flashStatus(html, ms) {
  const prev = statusBar.innerHTML, prevCls = statusBar.className;
  setStatus('waiting', html);
  clearTimeout(_flashTimer);
  _flashTimer = setTimeout(() => setStatus(prevCls, prev), ms);
}
function showGameOver(winner) { alert(winner === 1 ? '🟥 The British East India Company has conquered the Deccan.' : '🟩 Mysore has endured.'); }
function capitalize(s) { return s ? s.charAt(0).toUpperCase()+s.slice(1) : ''; }
function toggleSettings() { document.getElementById('settings-menu').classList.toggle('hidden'); }

window.onclick = function(e) {
  const menu = document.getElementById('settings-menu');
  const icon = document.getElementById('settings-icon');
  if (e.target !== icon && !menu.contains(e.target)) menu.classList.add('hidden');
};

window.renderMoveList = function(moves) {
    const list = document.getElementById('move-list');
    const badge = document.getElementById('move-count-badge');
    if (!moves || moves.length === 0) {
        list.innerHTML = '<em style="color:#9a7a3a">No legal moves available.</em>';
        badge.textContent = '';
        return;
    }
    badge.textContent = '(' + moves.length + ')';
    list.innerHTML = moves.map(function(m) {
        return '<div class="move-entry" onclick="highlightMove(' + m.idx + ')" id="move-entry-' + m.idx + '">' +
            '<span class="move-idx">' + m.idx + '</span>' +
            '<span class="move-type">' + m.type + '</span>' +
            '<span class="move-desc">' + m.desc + '</span>' +
            '</div>';
    }).join('');
};

function highlightMove(idx) {
    document.querySelectorAll('.move-entry').forEach(function(e) { e.classList.remove('highlighted'); });
    var el = document.getElementById('move-entry-' + idx);
    if (el) { el.classList.add('highlighted'); el.scrollIntoView({block:'nearest'}); }
    document.getElementById('move-number-input').value = idx;
}

function submitMove() {
    var raw = document.getElementById('move-number-input').value.trim();
    var feedback = document.getElementById('move-feedback');
    if (raw === '') { feedback.textContent = 'Enter a move number first.'; return; }
    var idx = parseInt(raw, 10);
    if (isNaN(idx)) { feedback.textContent = 'Invalid number.'; return; }
    feedback.textContent = 'Processing...';
    window.applyMove(idx);
}

function updateUI(uiState, moves) {
    uiState.nodes.forEach(nodeData => {
        const node = window.NODES[nodeData.name];
        if (!node) return;

        if (nodeData.armyType === 'fresh') {
            node.armyType = 'active';
            node.owner = 'british';
        } else if (nodeData.armyType === 'tired') {
            node.armyType = 'tired';
            node.owner = 'british';
        } else if (nodeData.armyType === 'fort') {
            node.armyType = 'fort';
            node.owner = 'mysore';
        } else {
            node.armyType = 'empty';
            node.owner = 'empty';
        }
    });

    window.renderNodes();

    window.renderCards(uiState.british_cards, uiState.mysore_cards);

    window.updateCombatInfo(
        uiState.turn.toString(), 
        uiState.who_to_move, 
        uiState.attacker, 
        uiState.defender, 
        uiState.card_strength.toString()
    );

    window.renderMoveList(moves);
}


let players = { british: 'human', mysore: 'human' };

function buildPlayerMap(matchMode, humanSide) {
    if (matchMode === 'human') {
        players = { british: 'human', mysore: 'human' };
    } else if (matchMode === 'ai_vs_ai') {
        players = { british: 'ai', mysore: 'ai' };
    } else {
        const human = (humanSide || 'british').toLowerCase();
        players = { british: 'ai', mysore: 'ai' };
        players[human] = 'human';
    }
    console.log('Player map:', players);
}

function currentSideIsAi(uiState) {
    const whoToMove = (uiState.who_to_move || '').toLowerCase();
    if (whoToMove.includes('british')) return players.british === 'ai';
    if (whoToMove.includes('mysore'))  return players.mysore  === 'ai';
    return false;
}

// Central response handler — every API call funnels through here
// ---------------------------------------------------------------------------
function handleServerResponse(data) {
    if (data.error) {
        console.error("Server error:", data.error);
        document.getElementById('move-feedback').innerText = "Error: " + data.error;
        return;
    }

    currentBitString = data.state_str;
    updateUI(data.ui_state, data.moves);
    setStatus('connected', '⬤ &nbsp;CONNECTED');

    if (data.winner !== 0) {
        showGameOver(data.winner);
        return;
    }

    if (currentSideIsAi(data.ui_state)) {
        const delay = players.british === 'ai' && players.mysore === 'ai' ? 800 : 300;
        setTimeout(() => triggerAiMove(data.state_str), delay);
    }
}

async function triggerAiMove(stateStr) {
    console.log("AI is thinking…");
    document.getElementById('move-feedback').innerText = "AI thinking…";

    try {
        const response = await fetch('/api/play-ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state_str: stateStr })
        });
        const data = await response.json();
        document.getElementById('move-feedback').innerText = '';
        handleServerResponse(data);
    } catch (err) {
        console.error("Failed to fetch AI move:", err);
        document.getElementById('move-feedback').innerText = "Error connecting to server.";
    }
}

window.applyMove = async function(moveIdx) {
    const feedback = document.getElementById('move-feedback');
    feedback.textContent = 'Processing…';

    try {
        const response = await fetch('/api/play-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state_str: currentBitString, move_idx: moveIdx })
        });
        const data = await response.json();
        feedback.textContent = data.error ? data.error : `Move ${moveIdx} applied.`;
        handleServerResponse(data);
    } catch (err) {
        console.error("Error applying move:", err);
        feedback.textContent = "Error connecting to server.";
    }
};

document.getElementById('load-state-btn').addEventListener('click', async () => {
    const rawInput = document.getElementById('save-input').value.trim();
    try {
        const response = await fetch('/api/load-state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state_str: rawInput })
        });
        const data = await response.json();
        if (data.error) { window.alert("Error loading state: " + data.error); return; }
        handleServerResponse(data);
        console.log("State loaded.");
    } catch (err) {
        window.alert("Failed to reach the server.");
        console.error(err);
    }
});

function saveState() {
    if (!currentBitString) { alert("No game state to save yet."); return; }
    const binStr = currentBitString;

    const overlay = document.createElement('div');
    overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:2000;display:flex;align-items:center;justify-content:center;";
    const dialog = document.createElement('div');
    dialog.style.cssText = "background:var(--parchment);border:3px solid var(--border);padding:20px;border-radius:5px;text-align:center;max-width:400px;box-shadow:0 8px 40px #000d;";
    dialog.innerHTML = `
        <h3 style="font-family:'Cinzel',serif;margin-bottom:10px;color:var(--ink);">SAVE GAME STATE</h3>
        <p style="font-size:0.8rem;color:#5a3e18;margin-bottom:10px;">Copy this bit-string to restore your position later.</p>
        <textarea readonly style="width:100%;height:60px;font-family:monospace;font-size:0.8rem;margin-bottom:15px;background:#faf4e4;border:1px solid #bc9a6c;padding:5px;resize:none;">${binStr}</textarea>
    `;
    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-btn safe';
    copyBtn.innerText = '📋 Copy to Clipboard';
    copyBtn.onclick = () => {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(binStr).then(() => {
                copyBtn.innerText = '✅ Copied!';
                setTimeout(() => copyBtn.innerText = '📋 Copy to Clipboard', 2000);
            });
        } else {
            const ta = document.createElement('textarea');
            ta.value = binStr; ta.style.position = 'absolute'; ta.style.left = '-9999px';
            document.body.appendChild(ta); ta.select(); document.execCommand('copy');
            document.body.removeChild(ta);
            copyBtn.innerText = '✅ Copied!';
            setTimeout(() => copyBtn.innerText = '📋 Copy to Clipboard', 2000);
        }
    };
    const closeBtn = document.createElement('button');
    closeBtn.className = 'action-btn danger';
    closeBtn.innerText = 'Close';
    closeBtn.style.marginTop = '8px';
    closeBtn.onclick = () => document.body.removeChild(overlay);
    dialog.appendChild(copyBtn);
    dialog.appendChild(closeBtn);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    document.getElementById('settings-menu').classList.add('hidden');
}

function sendReset() {
    if (!confirm('Reset the board to the starting position?')) return;
    initGame();
    document.getElementById('settings-menu').classList.add('hidden');
}

function sendUndo() {
    alert('Undo is not yet supported by the server.');
    document.getElementById('settings-menu').classList.add('hidden');
}

async function initGame() {
    renderEdges();
    window.renderNodes();
    renderCards([true,true,true,true,true,true], [true,true,true,true,true,true]);
    setStatus('waiting', '⬤ &nbsp;CONNECTING…');
    console.log("Fetching initial game state…");
    try {
        const response = await fetch('/api/init');
        const data = await response.json();
        buildPlayerMap(data.match_mode, data.human_side);  
        handleServerResponse(data);
        console.log("Game engine ready.");
    } catch (err) {
        setStatus('disconnected', '⬤ &nbsp;NOT CONNECTED');
        console.error("Failed to reach server:", err);
    }
}

initGame();