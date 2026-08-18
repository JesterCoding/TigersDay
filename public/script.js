/**
 * The Tiger's Day – Anglo-Mysore Wars
 * Frontend Game Client & Interactive UX Controller
 * 
 * Direct Point-and-Click Engine Interface (Zero Modals / Zero Popups)
 */

// ==========================================================================
// 1. CONSTANTS & GAME MAP GEOMETRY
// ==========================================================================
const SVG_NS = 'http://www.w3.org/2000/svg';

var NODES = {
  Bombay:        { x:110, y: 74,  owner:'british', armyType:'active',  key:true,  coast:true,  labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Hyderabad:     { x:515, y:100,  owner:'british', armyType:'active',  key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Madras:        { x:618, y:322,  owner:'british', armyType:'active',  key:true,  coast:true,  labelAnchor:{anchor:'end',    dx:-18, dy:-24} },
  Seringapatam:  { x:230, y:480,  owner:'mysore',  armyType:'fort',    key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Coimbatore:    { x:305, y:600,  owner:'mysore',  armyType:'fort',    key:true,  coast:false, labelAnchor:{anchor:'middle', dx:0,   dy:-24} },
  Satara:        { x:255, y:128,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Poona:         { x:345, y:70,   owner:'empty',   armyType:'empty',   key:false, coast:false },
  Raichur:       { x:390, y:178,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Masulipatam:   { x:656, y:162,  owner:'empty',   armyType:'empty',   key:false, coast:true,  labelAnchor:{anchor:'end',   dx:-12, dy:-16} },
  Goa:           { x: 94, y:262,  owner:'empty',   armyType:'empty',   key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Darwar:        { x:232, y:232,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Anantapur:     { x:470, y:228,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Chitaldoorg:   { x:250, y:350,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Mangalore:     { x:118, y:398,  owner:'mysore',  armyType:'fort',    key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Bangalore:     { x:350, y:400,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Vellore:       { x:460, y:340,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  'Mahé':        { x:145, y:586,  owner:'mysore',  armyType:'fort',    key:false, coast:true,  labelAnchor:{anchor:'start', dx: 12, dy:-16} },
  Pondicherry:   { x:610, y:446,  owner:'empty',   armyType:'empty',   key:false, coast:true,  labelAnchor:{anchor:'end',   dx:-12, dy:-16} },
  Erode:         { x:405, y:515,  owner:'mysore',  armyType:'fort',    key:false, coast:false },
  Trichy:        { x:506, y:580,  owner:'empty',   armyType:'empty',   key:false, coast:false },
  Alwaye:        { x:225, y:720,  owner:'mysore',  armyType:'empty',   key:false, coast:false },
  Dindigul:      { x:415, y:670,  owner:'empty',   armyType:'fort',    key:false, coast:false },
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
  { name: 'Wall Breach',      strength: 3, icon: '💥', desc: 'Powerful siege breach & battle power' },
  { name: 'Highlanders',      strength: 2, icon: '🟥', desc: 'Deploy a Fresh Army on any Coast' },
  { name: 'Royal Navy',       strength: 2, icon: '⚓', desc: 'Move an Army to any Coastal territory' },
  { name: 'Divide and Rule',  strength: 1, icon: '🤝', desc: 'Relocate a Fort not in a Key City' },
  { name: 'Force March',      strength: 1, icon: '🥾', desc: 'Move a Tired Army to adjacent territory' },
  { name: 'Princely States',  strength: 1, icon: '🏰', desc: 'Deploy a Tired Army in an empty Key City' },
];

const MYSORE_CARD_DATA = [
  { name: 'Iron Rockets',     strength: 3, icon: '🚀', desc: 'Devastating artillery & battle power' },
  { name: 'Sepoy Mutiny',     strength: 2, icon: '⚔️', desc: 'Remove an Army not in a Key City' },
  { name: 'French Alliance',  strength: 2, icon: '💠', desc: 'Deploy a Fort adjacent to another Fort' },
  { name: 'Monsoon',          strength: 1, icon: '🌧️', desc: 'Flip a Fresh Army to Tired' },
  { name: 'Cavalry Raid',     strength: 1, icon: '🏇', desc: 'Force British to discard a random card' },
  { name: 'Sea Trade',        strength: 1, icon: '🪙', desc: 'Move a Fort from Coast to any territory' },
];

const CARD_VALUE = [3, 2, 2, 1, 1, 1];

// ==========================================================================
// 2. RUNTIME STATE MACHINE
// ==========================================================================
let currentBitString = "";
let lastUiState = null;
let currentMoves = [];                 // Array of { idx, type, desc }
let selectedUnit = null;               // Selected territory string on map
let cardTargetingMode = null;          // { cardName, faction, step: 1|2, sourceNode, targetNodes, validSources, allMoves, isTwoStep }
let stagedTradeCard = null;            // { faction, cardIndex, cardName }
let players = { british: 'human', mysore: 'human' };
let currentEvalLoopState = null;

/**
 * Central state reset — clears ALL interactive UI state (unit selection,
 * card targeting highlights, trade staging) and refreshes the map + cards.
 * Call this before starting any new interaction or when receiving new game state.
 */
function clearAllInteractionState() {
  selectedUnit = null;
  cardTargetingMode = null;
  stagedTradeCard = null;
  refreshMapHighlights();
  renderAllCards();
  updateActionButtons();
  updateTurnHeaderInstruction();
}

let settings = {
  showEval: false,
  showDebugMoves: false
};

// ==========================================================================
// 3. SVG MAP RENDERING & INITIALIZATION
// ==========================================================================
function splineControlPoint(ax, ay, bx, by, f = 0.18) {
  const mx = (ax + bx) / 2, my = (ay + by) / 2;
  const dx = bx - ax, dy = by - ay;
  const len = Math.sqrt(dx * dx + dy * dy);
  return { cx: mx + (-dy / len) * len * f, cy: my + (dx / len) * len * f };
}

function renderEdges() {
  const layer = document.getElementById('edge-layer');
  if (!layer) return;
  layer.innerHTML = '';
  for (const edge of EDGES) {
    const [aName, bName, opts = {}] = edge;
    const a = NODES[aName], b = NODES[bName];
    if (!a || !b) continue;
    const { cx, cy } = splineControlPoint(a.x, a.y, b.x, b.y, opts.curve || 0.15);
    const path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', `M ${a.x},${a.y} Q ${cx},${cy} ${b.x},${b.y}`);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#6a4c1e');
    path.setAttribute('stroke-width', '1.8');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('opacity', '0.7');
    layer.appendChild(path);
  }
}

window.renderNodes = function renderNodes() {
  const layer = document.getElementById('node-layer');
  if (!layer) return;
  layer.innerHTML = '';

  for (const [name, data] of Object.entries(window.NODES)) {
    const { x, y, owner, key, coast } = data;
    const armyType = data.armyType || 'empty';
    const la = data.labelAnchor || { anchor: 'middle', dx: 0, dy: key ? -24 : -16 };
    const anchor = la.anchor || 'middle', ldx = la.dx || 0, ldy = la.dy || (key ? -24 : -16);

    const g = document.createElementNS(SVG_NS, 'g');
    g.setAttribute('class', 'node-group');
    g.setAttribute('id', `node-group-${name.replace(/[^a-zA-Z0-9]/g, '_')}`);
    g.setAttribute('transform', `translate(${x},${y})`);
    g.dataset.name = name;
    g.dataset.owner = owner;
    g.dataset.armyType = armyType;
    g.dataset.key = String(key);
    g.dataset.coast = String(coast);

    // Event listeners
    g.addEventListener('click', (e) => {
      e.stopPropagation();
      handleNodeClick(name);
    });
    g.addEventListener('mousemove', (e) => tooltipShow(e, name, data));
    g.addEventListener('mouseleave', tooltipHide);

    // Selection ring
    const ring = document.createElementNS(SVG_NS, 'circle');
    ring.setAttribute('class', 'sel-ring');
    ring.setAttribute('r', key ? '24' : '18');
    ring.setAttribute('fill', 'none');
    ring.setAttribute('stroke', '#d4a030');
    ring.setAttribute('stroke-width', '2.5');
    ring.setAttribute('opacity', '0');
    g.appendChild(ring);

    // Glowing target pulse ring (visible only when node is a valid target)
    const targetRing = document.createElementNS(SVG_NS, 'circle');
    targetRing.setAttribute('class', 'target-glow-ring');
    targetRing.setAttribute('r', '20');
    targetRing.setAttribute('fill', 'none');
    targetRing.setAttribute('stroke', '#ffdd44');
    targetRing.setAttribute('stroke-width', '3');
    targetRing.setAttribute('opacity', '0');
    g.appendChild(targetRing);

    // Territory shape
    if (key) {
      const sq = document.createElementNS(SVG_NS, 'rect');
      sq.setAttribute('x', '-18');
      sq.setAttribute('y', '-18');
      sq.setAttribute('width', '36');
      sq.setAttribute('height', '36');
      sq.setAttribute('fill', '#1c1814');
      sq.setAttribute('stroke', '#e0c896');
      sq.setAttribute('stroke-width', '1.6');
      g.appendChild(sq);
    } else {
      const circ = document.createElementNS(SVG_NS, 'circle');
      circ.setAttribute('r', '10');
      circ.setAttribute('fill', '#2a2420');
      circ.setAttribute('stroke', '#b0a080');
      circ.setAttribute('stroke-width', '1.4');
      g.appendChild(circ);
    }

    // Army / Fort unit overlay
    if (armyType === 'fort') {
      const p = document.createElementNS(SVG_NS, 'polygon');
      p.setAttribute('points', '0,-22 22,0 0,22 -22,0');
      p.setAttribute('fill', '#2e7a2e');
      p.setAttribute('stroke', '#8fe08f');
      p.setAttribute('stroke-width', '1.2');
      p.setAttribute('filter', 'url(#nshadow)');
      g.appendChild(p);
    } else if (armyType === 'active' || armyType === 'tired') {
      const isTired = armyType === 'tired';
      const opacity = isTired ? '0.55' : '1';

      if (owner === 'british') {
        const p = document.createElementNS(SVG_NS, 'rect');
        p.setAttribute('x', '-18');
        p.setAttribute('y', '-18');
        p.setAttribute('width', '36');
        p.setAttribute('height', '36');
        p.setAttribute('fill', '#c0281a');
        p.setAttribute('stroke', '#ff9999');
        p.setAttribute('stroke-width', '1.2');
        p.setAttribute('opacity', opacity);
        p.setAttribute('filter', 'url(#nshadow)');
        g.appendChild(p);
      } else if (owner === 'mysore') {
        const p = document.createElementNS(SVG_NS, 'polygon');
        p.setAttribute('points', '0,-24 24,0 0,24 -24,0');
        p.setAttribute('fill', '#2e7a2e');
        p.setAttribute('stroke', '#8fe08f');
        p.setAttribute('stroke-width', '1.2');
        p.setAttribute('opacity', opacity);
        p.setAttribute('filter', 'url(#nshadow)');
        g.appendChild(p);
      }

      if (isTired) {
        const slash = document.createElementNS(SVG_NS, 'line');
        slash.setAttribute('x1', '-13');
        slash.setAttribute('y1', '-13');
        slash.setAttribute('x2', '13');
        slash.setAttribute('y2', '13');
        slash.setAttribute('stroke', 'rgba(255,255,255,0.9)');
        slash.setAttribute('stroke-width', '3');
        slash.setAttribute('stroke-linecap', 'round');
        g.appendChild(slash);
      }
    }

    // Name label
    const makeLabel = (isHalo) => {
      const t = document.createElementNS(SVG_NS, 'text');
      t.setAttribute('dy', String(ldy));
      t.setAttribute('dx', String(ldx));
      t.setAttribute('text-anchor', anchor);
      t.setAttribute('font-family', key ? 'Cinzel,serif' : 'Cormorant Garamond,serif');
      t.setAttribute('font-size', key ? '21' : '19');
      t.setAttribute('font-weight', '700');
      if (key) t.setAttribute('letter-spacing', '.06em');
      if (isHalo) {
        t.setAttribute('stroke', 'rgba(228,213,155,0.92)');
        t.setAttribute('stroke-width', '4');
        t.setAttribute('stroke-linejoin', 'round');
        t.setAttribute('fill', 'none');
        t.setAttribute('paint-order', 'stroke');
      } else {
        t.setAttribute('fill', '#1a1208');
      }
      t.textContent = name;
      return t;
    };
    g.appendChild(makeLabel(true));
    g.appendChild(makeLabel(false));

    layer.appendChild(g);
  }

  refreshMapHighlights();
};

// ==========================================================================
// 4. MAP HIGHLIGHTS & PULSE MANAGEMENT
// ==========================================================================
function clearMapHighlights() {
  document.querySelectorAll('.node-group').forEach(el => {
    el.classList.remove('selected-unit', 'valid-map-target');
    const ring = el.querySelector('.sel-ring');
    const glowRing = el.querySelector('.target-glow-ring');
    if (ring) ring.setAttribute('opacity', '0');
    if (glowRing) glowRing.setAttribute('opacity', '0');
  });
}

function refreshMapHighlights() {
  clearMapHighlights();

  // Highlight 1: Selected Unit
  if (selectedUnit) {
    const el = getNodeElement(selectedUnit);
    if (el) {
      el.classList.add('selected-unit');
      const ring = el.querySelector('.sel-ring');
      if (ring) ring.setAttribute('opacity', '1');
    }

    // Pulse all valid movement destinations for this unit
    const validDests = getValidMoveDestinations(selectedUnit);
    validDests.forEach(destName => {
      const destEl = getNodeElement(destName);
      if (destEl) {
        destEl.classList.add('valid-map-target');
        const glowRing = destEl.querySelector('.target-glow-ring');
        if (glowRing) glowRing.setAttribute('opacity', '1');
      }
    });
  }

  // Highlight 2: Card Targeting Mode
  if (cardTargetingMode) {
    if (!cardTargetingMode.isTwoStep) {
      // 1-step abilities (Sepoy Mutiny, French Alliance, Monsoon, Highlanders, Princely States)
      cardTargetingMode.targetNodes.forEach(nodeName => {
        const el = getNodeElement(nodeName);
        if (el) {
          el.classList.add('valid-map-target');
          const glowRing = el.querySelector('.target-glow-ring');
          if (glowRing) glowRing.setAttribute('opacity', '1');
        }
      });
    } else {
      // 2-step abilities (Divide & Rule, Force March, Royal Navy, Sea Trade)
      if (cardTargetingMode.step === 1) {
        cardTargetingMode.validSources.forEach(srcName => {
          const el = getNodeElement(srcName);
          if (el) {
            el.classList.add('valid-map-target');
            const glowRing = el.querySelector('.target-glow-ring');
            if (glowRing) glowRing.setAttribute('opacity', '1');
          }
        });
      } else if (cardTargetingMode.step === 2 && cardTargetingMode.sourceNode) {
        const srcEl = getNodeElement(cardTargetingMode.sourceNode);
        if (srcEl) {
          srcEl.classList.add('selected-unit');
          const ring = srcEl.querySelector('.sel-ring');
          if (ring) ring.setAttribute('opacity', '1');
        }

        const validDests = getValidTwoStepDestinations(cardTargetingMode.cardName, cardTargetingMode.sourceNode);
        validDests.forEach(destName => {
          const destEl = getNodeElement(destName);
          if (destEl) {
            destEl.classList.add('valid-map-target');
            const glowRing = destEl.querySelector('.target-glow-ring');
            if (glowRing) glowRing.setAttribute('opacity', '1');
          }
        });
      }
    }
  }
}

function getNodeElement(name) {
  return document.getElementById(`node-group-${name.replace(/[^a-zA-Z0-9]/g, '_')}`);
}

function getValidMoveDestinations(sourceName) {
  const dests = new Set();
  const prefix = sourceName + " -> ";
  currentMoves.forEach(m => {
    if (m.type === 'Move' && m.desc.startsWith(prefix)) {
      const dest = m.desc.substring(prefix.length).trim();
      dests.add(dest);
    }
  });
  return dests;
}

function getValidTwoStepDestinations(cardName, sourceName) {
  const dests = new Set();
  const prefix = sourceName + " -> ";
  currentMoves.forEach(m => {
    if (m.type === cardName && m.desc.startsWith(prefix)) {
      const dest = m.desc.substring(prefix.length).trim();
      dests.add(dest);
    }
  });
  return dests;
}

// ==========================================================================
// 5. DIRECT POINT-AND-CLICK MAP INTERACTIONS (Army Movement & Target Execution)
// ==========================================================================
function handleNodeClick(nodeName) {
  // A. Card Targeting Mode Handler
  if (cardTargetingMode) {
    handleCardTargetNodeClick(nodeName);
    return;
  }

  // Cancel any staged trade if map is clicked
  if (stagedTradeCard) {
    stagedTradeCard = null;
    renderAllCards();
    updateTurnHeaderInstruction();
  }

  // B. Direct Army Selection & Toggle Deselection
  if (selectedUnit === nodeName) {
    // TOGGLE DESELECTION: Clicking the same army a second time immediately cancels selection!
    selectedUnit = null;
    refreshMapHighlights();
    updateActionButtons();
    updateTurnHeaderInstruction();
    return;
  }

  // If a unit is already selected, check if clicked node is a valid destination
  if (selectedUnit !== null) {
    const targetMoveStr = `${selectedUnit} -> ${nodeName}`;
    const move = currentMoves.find(m => m.type === 'Move' && m.desc === targetMoveStr);

    if (move) {
      const fromUnit = selectedUnit;
      selectedUnit = null;
      refreshMapHighlights();
      updateActionButtons();
      showToast(`Moving ${fromUnit} → ${nodeName}`, 'info');
      window.applyMove(move.idx);
      return;
    }

    // If clicked node is another unit of the player that can move/rest, switch selection to it
    const hasMoveMoves = currentMoves.some(m => m.type === 'Move' && m.desc.startsWith(nodeName + " -> "));
    const hasTireMove = currentMoves.some(m => m.type === 'Tire' && m.desc === nodeName);

    if (hasMoveMoves || hasTireMove) {
      selectedUnit = nodeName;
      refreshMapHighlights();
      updateActionButtons();
      updateTurnHeaderInstruction();
      return;
    }

    // Otherwise, deselect
    selectedUnit = null;
    refreshMapHighlights();
    updateActionButtons();
    updateTurnHeaderInstruction();
    return;
  }

  // No unit selected yet: check if this territory has available moves
  const hasMoveMoves = currentMoves.some(m => m.type === 'Move' && m.desc.startsWith(nodeName + " -> "));
  const hasTireMove = currentMoves.some(m => m.type === 'Tire' && m.desc === nodeName);

  if (hasMoveMoves || hasTireMove) {
    selectedUnit = nodeName;
    refreshMapHighlights();
    updateActionButtons();
    updateTurnHeaderInstruction();
  } else {
    // Info check for player
    const node = NODES[nodeName];
    if (node && node.armyType !== 'empty') {
      showToast(`${nodeName} (${node.owner} ${node.armyType}) has no legal moves right now.`);
    }
  }
}

function handleCardTargetNodeClick(nodeName) {
  if (!cardTargetingMode) return;

  if (!cardTargetingMode.isTwoStep) {
    // 1-step ability execution
    if (cardTargetingMode.targetNodes.has(nodeName)) {
      const move = currentMoves.find(m => m.type === cardTargetingMode.cardName && m.desc === nodeName);
      if (move) {
        const cardName = cardTargetingMode.cardName;
        exitCardTargetingMode();
        showToast(`Activated ${cardName} on ${nodeName}!`, 'success');
        window.applyMove(move.idx);
      }
    } else {
      showToast(`${nodeName} is not a valid target for ${cardTargetingMode.cardName}.`, 'error');
    }
  } else {
    // 2-step ability execution
    if (cardTargetingMode.step === 1) {
      if (cardTargetingMode.validSources.has(nodeName)) {
        cardTargetingMode.sourceNode = nodeName;
        cardTargetingMode.step = 2;
        refreshMapHighlights();
        updateTurnHeaderInstruction();
      } else {
        showToast(`${nodeName} cannot be selected as a source for ${cardTargetingMode.cardName}.`, 'error');
      }
    } else if (cardTargetingMode.step === 2) {
      if (nodeName === cardTargetingMode.sourceNode) {
        // Toggle deselect source back to step 1
        cardTargetingMode.sourceNode = null;
        cardTargetingMode.step = 1;
        refreshMapHighlights();
        updateTurnHeaderInstruction();
        return;
      }

      const targetMoveStr = `${cardTargetingMode.sourceNode} -> ${nodeName}`;
      const move = currentMoves.find(m => m.type === cardTargetingMode.cardName && m.desc === targetMoveStr);

      if (move) {
        const cardName = cardTargetingMode.cardName;
        exitCardTargetingMode();
        showToast(`Executed ${cardName}: ${targetMoveStr}!`, 'success');
        window.applyMove(move.idx);
      } else {
        showToast(`${nodeName} is not a valid destination for ${cardTargetingMode.sourceNode}.`, 'error');
      }
    }
  }
}

function exitCardTargetingMode() {
  cardTargetingMode = null;
  refreshMapHighlights();
  renderAllCards();
  updateActionButtons();
  updateTurnHeaderInstruction();
}

// ==========================================================================
// 6. CARD INTERACTIONS (Single-Click Strength, Double-Click Ability, Direct Trade)
// ==========================================================================
function renderAllCards() {
  if (!lastUiState) return;
  renderCardDeck('mysore', lastUiState.mysore_cards);
  renderCardDeck('british', lastUiState.british_cards);

  // Update card counter badges
  const mAvail = lastUiState.mysore_cards.filter(Boolean).length;
  const bAvail = lastUiState.british_cards.filter(Boolean).length;
  const mBadge = document.getElementById('mysore-hand-count');
  const bBadge = document.getElementById('british-hand-count');
  if (mBadge) mBadge.textContent = `${mAvail}/6`;
  if (bBadge) bBadge.textContent = `${bAvail}/6`;
}

function renderCardDeck(faction, availArray) {
  const container = document.getElementById(`${faction}-cards-list`);
  if (!container) return;
  container.innerHTML = '';

  const cardDataList = faction === 'mysore' ? MYSORE_CARD_DATA : BRITISH_CARD_DATA;

  cardDataList.forEach((card, index) => {
    const isUsable = Boolean(availArray[index]);
    const cardDiv = document.createElement('div');

    let classNames = ['player-card', `${faction}-card`];
    if (!isUsable) classNames.push('card-activated', 'used');

    // Check if staged for trade
    if (stagedTradeCard && stagedTradeCard.faction === faction && stagedTradeCard.cardIndex === index) {
      classNames.push('staged-trade');
    }

    // Check if valid trade destination (greyed-out card eligible for trade)
    if (stagedTradeCard && stagedTradeCard.faction === faction && !isUsable) {
      const tradeType = `Draw ${stagedTradeCard.cardName}`;
      const canReclaim = currentMoves.some(m => m.type === tradeType && m.desc === card.name);
      if (canReclaim) {
        classNames.push('valid-trade-target');
      }
    }

    // Check if currently targeting
    if (cardTargetingMode && cardTargetingMode.faction === faction && cardTargetingMode.cardName === card.name) {
      classNames.push('targeting-active');
    }

    cardDiv.className = classNames.join(' ');

    // Wax Seal Strength Badge (Single-Click commits Strength in Battle)
    const seal = document.createElement('div');
    seal.className = 'card-strength-seal';
    seal.textContent = card.strength;
    seal.title = `Commit +${card.strength} Combat Strength in battle`;
    seal.addEventListener('click', (e) => {
      e.stopPropagation();
      handleCardStrengthClick(faction, index, card.name);
    });
    cardDiv.appendChild(seal);

    // Card Header Row
    const headerRow = document.createElement('div');
    headerRow.className = 'card-header-row';
    headerRow.innerHTML = `
      <span class="card-icon">${card.icon}</span>
      <span class="card-name">${card.name}</span>
    `;
    cardDiv.appendChild(headerRow);

    // Card Description (Clean without action hint footers)
    const desc = document.createElement('div');
    desc.className = 'card-desc';
    desc.textContent = card.desc;
    cardDiv.appendChild(desc);

    // Exhausted Stamp
    const stamp = document.createElement('div');
    stamp.className = 'used-stamp';
    stamp.textContent = 'EXHAUSTED';
    cardDiv.appendChild(stamp);

    // Card Body Click Handler (Debounced Single-Click vs Double-Click)
    cardDiv.addEventListener('click', (e) => {
      e.stopPropagation();
      handleCardBodyClick(faction, index, card.name, isUsable);
    });

    container.appendChild(cardDiv);
  });
}

/**
 * SINGLE-CLICK CARD STRENGTH NUMBER:
 * Directly commits the card's numeric value as Combat Strength to an ongoing battle.
 */
function handleCardStrengthClick(faction, index, cardName) {
  const powerType = faction === 'mysore' ? 'Mysore Power' : 'British Power';
  const move = currentMoves.find(m => m.type === powerType && m.desc === cardName);

  if (move) {
    showToast(`Committed ${cardName} (+${CARD_VALUE[index]} Strength) to battle!`, 'success');
    window.applyMove(move.idx);
  } else {
    if (lastUiState && (lastUiState.attacker !== 'None' || lastUiState.defender !== 'None')) {
      showToast(`Cannot commit ${cardName} strength in the current battle phase.`, 'error');
    } else {
      showToast(`Combat Strength is committed during active battles.`, 'info');
    }
  }
}

/**
 * Card Body Click Handler (Unified Single-Click):
 * - If clicking a greyed-out card while a trade is staged -> Complete Trade!
 * - If clicking an active card -> Activate Ability (if available) OR Stage Trade
 */
function handleCardBodyClick(faction, index, cardName, isUsable) {
  // DIRECT CARD-TO-CARD TRADING (No Trade Docks)
  // If clicking an already-activated (greyed-out) card while an unactivated card is staged:
  if (!isUsable) {
    if (stagedTradeCard && stagedTradeCard.faction === faction) {
      const tradeType = `Draw ${stagedTradeCard.cardName}`;
      const move = currentMoves.find(m => m.type === tradeType && m.desc === cardName);

      if (move) {
        const tradedCard = stagedTradeCard.cardName;
        stagedTradeCard = null;
        renderAllCards();
        updateTurnHeaderInstruction();
        showToast(`Traded ${tradedCard} to reclaim ${cardName}!`, 'success');
        window.applyMove(move.idx);
        return;
      } else {
        showToast(`Cannot trade ${stagedTradeCard.cardName} for ${cardName}.`, 'error');
        return;
      }
    } else {
      showToast(`${cardName} is exhausted. Stage an active card to trade for it.`, 'info');
      return;
    }
  }

  // If clicking an active card:
  // Check if this card has an ability move available — if so, activate it directly.
  // Otherwise fall through to trade staging.
  const abilityCardNames = [
    'Cavalry Raid', 'Sepoy Mutiny', 'French Alliance', 'Monsoon',
    'Highlanders', 'Princely States',
    'Divide and Rule', 'Force March', 'Royal Navy', 'Sea Trade'
  ];

  if (abilityCardNames.includes(cardName)) {
    // Check if any ability move exists for this card
    const hasAbilityMove = currentMoves.some(m => m.type === cardName);
    if (hasAbilityMove) {
      handleCardAbilityActivation(faction, index, cardName);
      return;
    }
    // No ability move available — fall through to trade staging
  }

  // Stage for trade (or toggle off if already staged)
  handleCardTradeSelection(faction, index, cardName);
}

/**
 * SINGLE-CLICK CARD BODY (Ability Activation):
 * Non-Targeted: Executes immediately.
 * Targeted: Enters Targeting Mode with glowing map targets.
 */
function handleCardAbilityActivation(faction, index, cardName) {
  // Clear ALL previous interaction state (targeting, trade staging, unit selection)
  clearAllInteractionState();

  // A. Non-Targeted Abilities (e.g. Cavalry Raid)
  if (cardName === 'Cavalry Raid') {
    const move = currentMoves.find(m => m.type === 'Cavalry Raid');
    if (move) {
      showToast(`Cavalry Raid launched! British must discard.`, 'success');
      window.applyMove(move.idx);
      return;
    } else {
      showToast(`Cavalry Raid is not legal to play right now.`, 'error');
      return;
    }
  }

  // B. Single-Step Targeted Abilities (Sepoy Mutiny, French Alliance, Monsoon, Highlanders, Princely States)
  const singleStepCards = ['Sepoy Mutiny', 'French Alliance', 'Monsoon', 'Highlanders', 'Princely States'];
  if (singleStepCards.includes(cardName)) {
    const moves = currentMoves.filter(m => m.type === cardName);
    if (moves.length === 0) {
      showToast(`No legal targets on the map for ${cardName}.`, 'error');
      return;
    }

    const targetNodes = new Set(moves.map(m => m.desc));
    cardTargetingMode = {
      cardName,
      faction,
      step: 1,
      targetNodes,
      isTwoStep: false
    };

    renderAllCards();
    refreshMapHighlights();
    updateActionButtons();
    updateTurnHeaderInstruction();
    showToast(`Targeting ${cardName}: Click a pulsing territory on the map.`, 'info');
    return;
  }

  // C. Two-Step Targeted Abilities (Divide and Rule, Force March, Royal Navy, Sea Trade)
  const twoStepCards = ['Divide and Rule', 'Force March', 'Royal Navy', 'Sea Trade'];
  if (twoStepCards.includes(cardName)) {
    const moves = currentMoves.filter(m => m.type === cardName);
    if (moves.length === 0) {
      showToast(`No legal actions on the map for ${cardName}.`, 'error');
      return;
    }

    const validSources = new Set(moves.map(m => m.desc.split(' -> ')[0]));
    cardTargetingMode = {
      cardName,
      faction,
      step: 1,
      sourceNode: null,
      validSources,
      allMoves: moves,
      isTwoStep: true
    };

    renderAllCards();
    refreshMapHighlights();
    updateActionButtons();
    updateTurnHeaderInstruction();
    showToast(`Targeting ${cardName}: Click a unit / territory on the map.`, 'info');
    return;
  }

  // D. 3-Strength Cards (Wall Breach, Iron Rockets)
  if (cardName === 'Wall Breach' || cardName === 'Iron Rockets') {
    const tradeMoves = currentMoves.filter(m => m.type === `Draw ${cardName}`);
    if (tradeMoves.length > 0) {
      handleCardTradeSelection(faction, index, cardName);
    } else {
      showToast(`${cardName}: Commit +3 in battle (strength seal) or trade for exhausted cards.`, 'info');
    }
  }
}

/**
 * DIRECT CARD-TO-CARD TRADING:
 * Step 1: Click unactivated card in hand to stage it.
 */
function handleCardTradeSelection(faction, index, cardName) {
  // If clicking the currently staged card, cancel staging
  if (stagedTradeCard && stagedTradeCard.cardName === cardName) {
    stagedTradeCard = null;
    renderAllCards();
    updateActionButtons();
    updateTurnHeaderInstruction();
    return;
  }

  // Check if this card can be traded for any exhausted card
  const tradeType = `Draw ${cardName}`;
  const tradeMoves = currentMoves.filter(m => m.type === tradeType);

  if (tradeMoves.length === 0) {
    showToast(`No exhausted cards can currently be traded for with ${cardName}.`, 'info');
    return;
  }

  // Stage card for trade
  stagedTradeCard = { faction, cardIndex: index, cardName };
  if (cardTargetingMode) {
    cardTargetingMode = null;
    refreshMapHighlights();
  }
  if (selectedUnit) { selectedUnit = null; refreshMapHighlights(); }

  renderAllCards();
  updateActionButtons();
  updateTurnHeaderInstruction();
  showToast(`Trade staged (${cardName}): Click a glowing exhausted card to reclaim it.`, 'info');
}

// ==========================================================================
// 7. PERSISTENT TURN HEADER & ACTION CONTROLS
// ==========================================================================
function updateTurnHeader(uiState, winner) {
  const header = document.getElementById('turn-header');
  const icon = document.getElementById('turn-faction-icon');
  const counter = document.getElementById('turn-counter');
  const title = document.getElementById('turn-phase-title');

  if (!header || !uiState) return;

  // 1. Victory / Game Over State
  if (winner !== 0) {
    header.className = 'turn-header game-over-phase';
    icon.textContent = winner === 1 ? '👑' : '🐅';
    counter.textContent = 'WAR CONCLUDED';
    title.textContent = winner === 1 ? 'BRITISH EAST INDIA CO. VICTORY' : 'MYSORE ENDURES & PREVAILS';
    updateTurnHeaderInstruction('The war has ended.');
    return;
  }

  counter.textContent = `TURN ${uiState.turn} OF 4`;

  const whoToMove = uiState.who_to_move || '';

  if (whoToMove === 'British Move') {
    header.className = 'turn-header british-phase';
    icon.textContent = '🦁';
    title.textContent = 'BRITISH TURN: MOVE AN ARMY';
  } else if (whoToMove === 'Mysore Card') {
    header.className = 'turn-header mysore-phase';
    icon.textContent = '🐅';
    title.textContent = 'MYSORE TURN: CARD PLAY';
  } else if (whoToMove === 'British Card') {
    header.className = 'turn-header british-phase';
    icon.textContent = '🦁';
    title.textContent = 'BRITISH TURN: CARD PLAY';
  } else {
    header.className = 'turn-header';
    icon.textContent = '⚔️';
    title.textContent = whoToMove;
  }

  // Battle Status Sub-Bar
  const battleBar = document.getElementById('battle-status-bar');
  if (uiState.attacker !== 'None' && uiState.defender !== 'None') {
    battleBar.classList.remove('hidden');
    document.getElementById('battle-attacker-name').textContent = uiState.attacker;
    document.getElementById('battle-defender-name').textContent = uiState.defender;
    const strength = uiState.card_strength || 0;
    document.getElementById('battle-strength-val').textContent = (strength >= 0 ? '+' : '') + strength;
  } else {
    battleBar.classList.add('hidden');
  }

  updateActionButtons();
  updateTurnHeaderInstruction();
}

function updateTurnHeaderInstruction(customText) {
  const instructionEl = document.getElementById('turn-instruction');
  if (!instructionEl) return;

  if (customText) {
    instructionEl.textContent = customText;
    return;
  }

  if (cardTargetingMode) {
    if (!cardTargetingMode.isTwoStep) {
      instructionEl.textContent = `Targeting ${cardTargetingMode.cardName}: Click a glowing territory on the map.`;
    } else {
      if (cardTargetingMode.step === 1) {
        instructionEl.textContent = `${cardTargetingMode.cardName}: Click a valid source unit on the map.`;
      } else {
        instructionEl.textContent = `${cardTargetingMode.cardName}: Click a glowing destination territory for ${cardTargetingMode.sourceNode}.`;
      }
    }
    return;
  }

  if (stagedTradeCard) {
    instructionEl.textContent = `Trade Staged (${stagedTradeCard.cardName}): Click an exhausted card in hand to trade for it.`;
    return;
  }

  if (selectedUnit) {
    const hasTire = currentMoves.some(m => m.type === 'Tire' && m.desc === selectedUnit);
    instructionEl.textContent = `${selectedUnit} selected. Click a pulsing territory to move${hasTire ? ', or Rest unit' : ''}.`;
    return;
  }

  if (!lastUiState) return;

  const whoToMove = lastUiState.who_to_move || '';
  if (whoToMove === 'British Move') {
    instructionEl.textContent = 'Click an army unit to select, then click a highlighted destination.';
  } else {
    instructionEl.textContent = 'Double-click card for Ability, single-click strength for Battle, or click card to Trade.';
  }
}

function updateActionButtons() {
  const restBtn = document.getElementById('header-rest-btn');
  const passBtn = document.getElementById('header-pass-btn');
  const cancelBtn = document.getElementById('header-cancel-btn');

  // Rest Unit Button
  if (selectedUnit && currentMoves.some(m => m.type === 'Tire' && m.desc === selectedUnit)) {
    restBtn.classList.remove('hidden');
  } else {
    restBtn.classList.add('hidden');
  }

  // Pass Turn Button
  const hasPassMove = currentMoves.some(m => m.type === 'Pass Mysore' || m.type === 'Pass British');
  if (hasPassMove && !cardTargetingMode && !stagedTradeCard && !selectedUnit) {
    passBtn.classList.remove('hidden');
  } else {
    passBtn.classList.add('hidden');
  }

  // Cancel Button
  if (cardTargetingMode || stagedTradeCard || selectedUnit) {
    cancelBtn.classList.remove('hidden');
  } else {
    cancelBtn.classList.add('hidden');
  }
}

function handleHeaderRestClick() {
  if (!selectedUnit) return;
  const move = currentMoves.find(m => m.type === 'Tire' && m.desc === selectedUnit);
  if (move) {
    const unit = selectedUnit;
    selectedUnit = null;
    refreshMapHighlights();
    updateActionButtons();
    showToast(`Rested unit at ${unit} (Tired in place).`, 'info');
    window.applyMove(move.idx);
  }
}

function handleHeaderPassClick() {
  const passMove = currentMoves.find(m => m.type === 'Pass Mysore' || m.type === 'Pass British');
  if (passMove) {
    showToast(`Passed turn phase.`, 'info');
    window.applyMove(passMove.idx);
  }
}

function handleHeaderCancelClick() {
  selectedUnit = null;
  cardTargetingMode = null;
  stagedTradeCard = null;
  refreshMapHighlights();
  renderAllCards();
  updateActionButtons();
  updateTurnHeaderInstruction();
}

// ==========================================================================
// 8. STOCKFISH-STYLE AI ENGINE EVALUATION (Settings Toggle)
// ==========================================================================
function handleEvalToggle(enabled) {
  settings.showEval = enabled;
  const panel = document.getElementById('eval-panel');

  if (enabled) {
    panel.classList.remove('hidden');
    if (currentBitString) {
      startProgressiveEval(currentBitString);
    }
  } else {
    panel.classList.add('hidden');
  }
}

function setEvalBar(score, totalSims) {
  const mysorePercentage = Math.max(0, Math.min(100, ((1 - score) / 2) * 100));
  const bar = document.getElementById('eval-bar-mysore');
  const scoreLabel = document.getElementById('eval-bar-score');
  const simsLabel = document.getElementById('eval-sims-label');
  const winrateLabel = document.getElementById('eval-winrate-label');

  if (bar && scoreLabel) {
    bar.style.width = `${mysorePercentage}%`;

    const sign = score > 0 ? '+' : '';
    let simStr = totalSims.toString();
    if (totalSims >= 1000) {
      simStr = (totalSims / 1000).toFixed(1) + 'k';
    }

    scoreLabel.textContent = `${sign}${score.toFixed(2)}`;
    if (simsLabel) simsLabel.textContent = `MCTS: ${simStr} sims`;

    if (winrateLabel) {
      if (score > 0.3) {
        winrateLabel.textContent = `British Advantage (${(mysorePercentage).toFixed(0)}% / ${(100 - mysorePercentage).toFixed(0)}%)`;
      } else if (score < -0.3) {
        winrateLabel.textContent = `Mysore Advantage (${(mysorePercentage).toFixed(0)}% / ${(100 - mysorePercentage).toFixed(0)}%)`;
      } else {
        winrateLabel.textContent = `Even Position (${(mysorePercentage).toFixed(0)}% / ${(100 - mysorePercentage).toFixed(0)}%)`;
      }
    }
  }
}

async function startProgressiveEval(stateStr) {
  if (!settings.showEval) return;
  currentEvalLoopState = stateStr;
  const MAX_SIMS = 500000;
  let currentTotal = 0;

  const linesContainer = document.getElementById('engine-lines-container');

  while (stateStr === currentBitString && currentTotal < MAX_SIMS && settings.showEval) {
    const batchSize = 400;

    try {
      const res = await fetch('/api/eval-step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state_str: stateStr, batch_size: batchSize })
      });
      const data = await res.json();

      if (stateStr !== currentBitString || stateStr !== currentEvalLoopState || !settings.showEval) {
        break;
      }

      currentTotal = data.total_sims;
      setEvalBar(data.eval_score, data.total_sims);

      if (linesContainer && data.top_moves && data.top_moves.length > 0) {
        linesContainer.innerHTML = '';
        data.top_moves.forEach(moveData => {
          const evalVal = parseFloat(moveData.eval);
          let evalStr = evalVal.toFixed(2);
          if (evalVal > 0) evalStr = '+' + evalStr;

          const squareClass = evalVal > 0.05 ? 'british-favored' : (evalVal < -0.05 ? 'mysore-favored' : 'neutral');

          const lineDiv = document.createElement('div');
          lineDiv.className = 'engine-line';
          lineDiv.innerHTML = `
            <span class="engine-eval-square ${squareClass}">${evalStr}</span>
            <span class="engine-move">${moveData.move_name}</span>
          `;
          linesContainer.appendChild(lineDiv);
        });
      }

      await new Promise(r => setTimeout(r, 60));
    } catch (err) {
      console.warn("Eval bar step error:", err);
      break;
    }
  }
}

// ==========================================================================
// 9. DEBUG MOVE CONSOLE & DRAWER MENUS (Settings & Tutorial)
// ==========================================================================
function handleDebugToggle(enabled) {
  settings.showDebugMoves = enabled;
  const consoleEl = document.getElementById('debug-move-console');
  if (enabled) {
    consoleEl.classList.remove('hidden');
    renderDebugMoveList();
  } else {
    consoleEl.classList.add('hidden');
  }
}

function renderDebugMoveList() {
  if (!settings.showDebugMoves) return;
  const list = document.getElementById('move-list');
  const badge = document.getElementById('move-count-badge');
  if (!list) return;

  badge.textContent = currentMoves.length;
  list.innerHTML = currentMoves.map(m => `
    <div class="move-entry" onclick="window.applyMove(${m.idx})">
      <span style="color:#bfa577; min-width:30px;">[${m.idx}]</span>
      <strong style="color:var(--parchment); min-width:130px;">${m.type}</strong>
      <span>${m.desc}</span>
    </div>
  `).join('');
}

function toggleTutorialMenu() {
  const tutorialDrawer = document.getElementById('tutorial-drawer');
  const settingsDrawer = document.getElementById('settings-drawer');
  if (settingsDrawer) settingsDrawer.classList.add('hidden');
  if (tutorialDrawer) tutorialDrawer.classList.toggle('hidden');
}

function toggleSettingsMenu() {
  const tutorialDrawer = document.getElementById('tutorial-drawer');
  const settingsDrawer = document.getElementById('settings-drawer');
  if (tutorialDrawer) tutorialDrawer.classList.add('hidden');
  if (settingsDrawer) settingsDrawer.classList.toggle('hidden');
}

// Global click listener to close drawers on outside click
document.addEventListener('click', (e) => {
  const tutorialDrawer = document.getElementById('tutorial-drawer');
  const tutorialBtn = document.getElementById('tutorial-toggle-btn');
  const settingsDrawer = document.getElementById('settings-drawer');
  const settingsBtn = document.getElementById('settings-toggle-btn');

  if (tutorialDrawer && !tutorialDrawer.classList.contains('hidden')) {
    if (!tutorialDrawer.contains(e.target) && !tutorialBtn.contains(e.target)) {
      tutorialDrawer.classList.add('hidden');
    }
  }

  if (settingsDrawer && !settingsDrawer.classList.contains('hidden')) {
    if (!settingsDrawer.contains(e.target) && !settingsBtn.contains(e.target)) {
      settingsDrawer.classList.add('hidden');
    }
  }
});

// Escape key cancels current interaction mode or closes open drawer
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const tutorialDrawer = document.getElementById('tutorial-drawer');
    const settingsDrawer = document.getElementById('settings-drawer');
    if (tutorialDrawer && !tutorialDrawer.classList.contains('hidden')) {
      tutorialDrawer.classList.add('hidden');
      return;
    }
    if (settingsDrawer && !settingsDrawer.classList.contains('hidden')) {
      settingsDrawer.classList.add('hidden');
      return;
    }
    handleHeaderCancelClick();
  }
});

// ==========================================================================
// 10. SERVER COMMUNICATION & GAME LOOP
// ==========================================================================
function updateConnectionPill(status) {
  const pill = document.getElementById('connection-pill');
  if (!pill) return;
  pill.className = `pill ${status}`;
  pill.textContent = status === 'connected' ? '⬤ CONNECTED' : (status === 'waiting' ? '⬤ CONNECTING…' : '⬤ DISCONNECTED');
}

function handleServerResponse(data) {
  if (data.error) {
    console.error("Server Error:", data.error);
    showToast(`Error: ${data.error}`, 'error');
    return;
  }

  // Reset ALL interaction state from the previous turn — clean slate
  selectedUnit = null;
  cardTargetingMode = null;
  stagedTradeCard = null;

  currentBitString = data.state_str;
  lastUiState = data.ui_state;
  currentMoves = data.moves || [];

  // Update board node states
  if (data.ui_state && data.ui_state.nodes) {
    data.ui_state.nodes.forEach(nodeData => {
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
  }

  // Render visual updates
  window.renderNodes();
  renderAllCards();
  updateTurnHeader(data.ui_state, data.winner);
  renderDebugMoveList();
  updateConnectionPill('connected');

  // Trigger progressive evaluation if enabled
  if (settings.showEval) {
    startProgressiveEval(data.state_str);
  }

  // Handle AI turn progression
  if (data.winner === 0 && isCurrentSideAi(data.ui_state)) {
    const delay = players.british === 'ai' && players.mysore === 'ai' ? 800 : 350;
    setTimeout(() => triggerAiMove(data.state_str), delay);
  }
}

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
}

function isCurrentSideAi(uiState) {
  const whoToMove = (uiState.who_to_move || '').toLowerCase();
  if (whoToMove.includes('british')) return players.british === 'ai';
  if (whoToMove.includes('mysore')) return players.mysore === 'ai';
  return false;
}

async function triggerAiMove(stateStr) {
  try {
    const response = await fetch('/api/play-ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_str: stateStr })
    });
    const data = await response.json();
    handleServerResponse(data);
  } catch (err) {
    console.error("Failed to fetch AI move:", err);
    showToast("Error connecting to server for AI move.", 'error');
  }
}

window.applyMove = async function(moveIdx) {
  try {
    const response = await fetch('/api/play-move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_str: currentBitString, move_idx: moveIdx })
    });
    const data = await response.json();
    handleServerResponse(data);
  } catch (err) {
    console.error("Error applying move:", err);
    showToast("Failed to send move to server.", 'error');
  }
};

async function initGame() {
  renderEdges();
  window.renderNodes();
  updateConnectionPill('waiting');

  try {
    const response = await fetch('/api/init');
    const data = await response.json();
    buildPlayerMap(data.match_mode, data.human_side);
    handleServerResponse(data);
  } catch (err) {
    updateConnectionPill('disconnected');
    console.error("Failed to reach server:", err);
  }
}

// ==========================================================================
// 11. ZERO-POPUP STATE SAVE / LOAD & UTILITIES
// ==========================================================================
function saveBinaryState() {
  if (!currentBitString) {
    showToast("No active game state to save.", 'error');
    return;
  }

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(currentBitString).then(() => {
      showToast("Game state binary string copied to clipboard!", 'success');
    });
  } else {
    const ta = document.createElement('textarea');
    ta.value = currentBitString;
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast("Game state binary string copied to clipboard!", 'success');
  }
  toggleSettingsMenu();
}

async function loadBinaryState() {
  const input = document.getElementById('binary-load-input');
  const rawInput = input ? input.value.trim() : '';

  if (!rawInput) {
    showToast("Please enter a valid binary state string.", 'error');
    return;
  }

  try {
    const response = await fetch('/api/load-state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_str: rawInput })
    });
    const data = await response.json();
    if (data.error) {
      showToast(`Error loading state: ${data.error}`, 'error');
      return;
    }
    handleServerResponse(data);
    showToast("Game state loaded successfully!", 'success');
    toggleSettingsMenu();
  } catch (err) {
    showToast("Failed to reach the server.", 'error');
  }
}

function resetGamePrompt() {
  initGame();
  showToast("Game reset to starting position.", 'info');
  toggleSettingsMenu();
}

// ==========================================================================
// 12. FLOATING TOOLTIPS & TOAST NOTIFICATIONS
// ==========================================================================
const tooltip = document.getElementById('tooltip');

function tooltipShow(e, name, data) {
  if (!tooltip) return;
  const armyType = data.armyType || 'empty';
  const owner = data.owner === 'empty' ? 'Unoccupied' : data.owner.charAt(0).toUpperCase() + data.owner.slice(1);
  const armyLabel = { active: '⚔ Fresh Army', tired: '😴 Tired Army', fort: '🏰 Fort', empty: 'Empty' };

  let extra = '';
  if (data.key) extra += ' · ⬛ Key City';
  if (data.coast) extra += ' · 🌊 Coastal';

  tooltip.innerHTML = `<b>${name}</b><span style="color:#6a4c1e;">${owner} · ${armyLabel[armyType] || ''}${extra}</span>`;
  tooltip.classList.add('show');
  tooltip.style.left = (e.clientX + 14) + 'px';
  tooltip.style.top = (e.clientY + 14) + 'px';
}

function tooltipHide() {
  if (tooltip) tooltip.classList.remove('show');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 3000);
}

// Start game client on load
initGame();