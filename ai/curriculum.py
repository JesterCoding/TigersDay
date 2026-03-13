import numpy as np
from collections import deque
from game.state import GameState


class CurriculumManager:

    MIXING_RATIOS = {
        4: {4: 1.0},
        3: {4: 0.2, 3: 0.8},
        2: {4: 0.1, 3: 0.2, 2: 0.7},
        1: {4: 0.05, 3: 0.1, 2: 0.15, 1: 0.7},
    }

    GRADUATION_THRESHOLDS = {
        4: {'win_rate': 0.65, 'min_games': 200},
        3: {'win_rate': 0.45, 'min_games': 300},
        2: {'win_rate': 0.35, 'min_games': 400},
    }

    def __init__(self, start_stage=4, window_size=200):
        self.current_stage = start_stage
        self.window_size = window_size
        self.results = {s: deque(maxlen=window_size) for s in range(1, 5)}

    def generate_position(self):
        """Generate a GameState based on current stage and mixing ratios.
        Returns (state, stage_used).
        """
        ratios = self.MIXING_RATIOS[self.current_stage]
        stages = list(ratios.keys())
        probs = [ratios[s] for s in stages]
        chosen_stage = int(np.random.choice(stages, p=probs))

        templates = self._get_templates(chosen_stage)
        template_fn = templates[np.random.randint(len(templates))]
        state = template_fn()
        return state, chosen_stage

    def record_result(self, game_result, stage_used):
        """Record a game result. game_result: +1 British win, -1 Mysore win."""
        self.results[stage_used].append(game_result)

    def check_graduation(self):
        """Check if current stage should graduate. Returns True if advanced."""
        if self.current_stage not in self.GRADUATION_THRESHOLDS:
            return False

        thresh = self.GRADUATION_THRESHOLDS[self.current_stage]
        results = self.results[self.current_stage]

        if len(results) < thresh['min_games']:
            return False

        win_rate = sum(1 for r in results if r == 1) / len(results)
        if win_rate >= thresh['win_rate']:
            old = self.current_stage
            self.current_stage -= 1
            print(f"  *** GRADUATED: Stage {old} -> Stage {self.current_stage} "
                  f"(British win rate: {win_rate:.1%}) ***")
            return True
        return False

    def get_stage_stats(self):
        """Return current win rates per stage for logging."""
        stats = {'current_stage': self.current_stage}
        for stage in range(1, 5):
            results = self.results[stage]
            if len(results) > 0:
                stats[f'stage{stage}_british_wr'] = (
                    sum(1 for r in results if r == 1) / len(results))
                stats[f'stage{stage}_games'] = len(results)
        return stats

    def _get_templates(self, stage):
        return {
            4: [self._t4a, self._t4b, self._t4c, self._t4d],
            3: [self._t3a, self._t3b, self._t3c, self._t3d],
            2: [self._t2a, self._t2b, self._t2c, self._t2d],
            1: [self._t1a, self._t1b, self._t1c, self._t1d],
        }[stage]

    # ── Shared randomization ──

    def _randomize_cards(self, state):
        """Randomly remove 0-2 cards from each side."""
        for _ in range(np.random.randint(0, 3)):
            idx = np.random.randint(6)
            if state.vector[GameState.IDX_MYSORE_CARDS_OFFSET + idx]:
                state.use_card_mysore_by_value(idx)
        for _ in range(np.random.randint(0, 3)):
            idx = np.random.randint(6)
            if state.vector[GameState.IDX_BRITISH_CARDS_OFFSET + idx]:
                state.use_card_british_by_value(idx)

    def _base_state(self, turn):
        """Create a blank state with cards and turn set."""
        state = GameState()
        state.reset_cards()
        state.set_turn(turn)
        state.set_who_to_move_by_name("British Move")
        return state

    # ══════════════════════════════════════════════
    # Stage 4: "Deliver the Final Blow" — Turn 4, need 1 key
    # ══════════════════════════════════════════════

    def _t4a(self):
        """Attack Srirangapatna — western approach."""
        state = self._base_state(4)
        # British holds 4 keys
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Coimbatore")
        # Attacker + adjacency support
        state.set_territory_vector_fresh_army("Mangalore")
        state.set_territory_vector_tired_army("Bangalore")
        # Target fort
        state.set_territory_vector_fort("Srirangapatna")
        # 0-1 extra defensive forts
        if np.random.random() < 0.5:
            extra = np.random.choice(["Mahé", "Erode"])
            state.set_territory_vector_fort(extra)
        self._randomize_cards(state)
        return state

    def _t4b(self):
        """Attack Coimbatore — southern approach."""
        state = self._base_state(4)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Srirangapatna")
        # Attacker + adjacency support
        state.set_territory_vector_fresh_army("Palgautcherry")
        state.set_territory_vector_tired_army("Erode")
        # Target fort
        state.set_territory_vector_fort("Coimbatore")
        if np.random.random() < 0.5:
            extra = np.random.choice(["Mahé", "Dindigul"])
            state.set_territory_vector_fort(extra)
        self._randomize_cards(state)
        return state

    def _t4c(self):
        """Attack Srirangapatna — dual armies adjacent."""
        state = self._base_state(4)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Coimbatore")
        # Two adjacent attackers — strong combat position
        state.set_territory_vector_fresh_army("Bangalore")
        state.set_territory_vector_fresh_army("Erode")
        # Target + 1 defensive fort
        state.set_territory_vector_fort("Srirangapatna")
        defense = np.random.choice(["Mangalore", "Mahé"])
        state.set_territory_vector_fort(defense)
        self._randomize_cards(state)
        return state

    def _t4d(self):
        """Attack Coimbatore — Royal Navy option."""
        state = self._base_state(4)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Srirangapatna")
        # Travancore can Royal Navy to coast or push overland
        state.set_territory_vector_fresh_army("Travancore")
        state.set_territory_vector_tired_army("Dindigul")
        # Target + blocker
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Palgautcherry")
        self._randomize_cards(state)
        return state

    # ══════════════════════════════════════════════
    # Stage 3: "Break Through and Hold" — Turn 3, need 2 keys
    # ══════════════════════════════════════════════

    def _t3a(self):
        """Southern pincer — armies threatening both keys."""
        state = self._base_state(3)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        # Interior positions
        state.set_territory_vector_fresh_army("Bangalore")
        state.set_territory_vector_fresh_army("Erode")
        state.set_territory_vector_tired_army("Vellore")
        # Key forts + 1 blocker
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Mahé")
        self._randomize_cards(state)
        return state

    def _t3b(self):
        """Western + southern approach."""
        state = self._base_state(3)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Mangalore")
        state.set_territory_vector_fresh_army("Palgautcherry")
        state.set_territory_vector_tired_army("Bednore")
        # Key forts + 1 interior fort
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Erode")
        self._randomize_cards(state)
        return state

    def _t3c(self):
        """Central pivot — Erode adjacent to both keys."""
        state = self._base_state(3)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Erode")
        state.set_territory_vector_tired_army("Bangalore")
        # Keys + 2 blockers
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Mahé")
        state.set_territory_vector_fort("Palgautcherry")
        self._randomize_cards(state)
        return state

    def _t3d(self):
        """Dominant position — only 2 key forts remain."""
        state = self._base_state(3)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Mangalore")
        state.set_territory_vector_fresh_army("Bangalore")
        state.set_territory_vector_fresh_army("Palgautcherry")
        # Only the 2 key forts remain
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        self._randomize_cards(state)
        return state

    # ══════════════════════════════════════════════
    # Stage 2: "Breach the Outer Wall" — Turn 2, partial progress
    # ══════════════════════════════════════════════

    def _t2a(self):
        """Southern corridor — Darwar/Bednore/Mangalore cleared."""
        state = self._base_state(2)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Travancore")
        state.set_territory_vector_tired_army("Vellore")
        # 6 forts remain
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Bangalore")
        state.set_territory_vector_fort("Erode")
        state.set_territory_vector_fort("Palgautcherry")
        state.set_territory_vector_fort("Mahé")
        self._randomize_cards(state)
        return state

    def _t2b(self):
        """Western corridor — Darwar/Bangalore cleared."""
        state = self._base_state(2)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Goa")
        state.set_territory_vector_tired_army("Pune")
        # 7 forts remain
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Mangalore")
        state.set_territory_vector_fort("Bednore")
        state.set_territory_vector_fort("Erode")
        state.set_territory_vector_fort("Palgautcherry")
        state.set_territory_vector_fort("Mahé")
        self._randomize_cards(state)
        return state

    def _t2c(self):
        """Central push from Hyderabad axis."""
        state = self._base_state(2)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Travancore")
        state.set_territory_vector_fresh_army("Anantapur")
        state.set_territory_vector_tired_army("Koppal")
        # 7 forts remain
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Darwar")
        state.set_territory_vector_fort("Bangalore")
        state.set_territory_vector_fort("Erode")
        state.set_territory_vector_fort("Mahé")
        state.set_territory_vector_fort("Palgautcherry")
        self._randomize_cards(state)
        return state

    def _t2d(self):
        """Multi-axis — Darwar captured by British."""
        state = self._base_state(2)
        state.set_territory_vector_fresh_army("Bombay")
        state.set_territory_vector_fresh_army("Hyderabad")
        state.set_territory_vector_fresh_army("Madras")
        state.set_territory_vector_fresh_army("Darwar")
        state.set_territory_vector_fresh_army("Travancore")
        state.set_territory_vector_tired_army("Vellore")
        # 7 forts, maybe remove 1
        state.set_territory_vector_fort("Srirangapatna")
        state.set_territory_vector_fort("Coimbatore")
        state.set_territory_vector_fort("Bednore")
        state.set_territory_vector_fort("Mangalore")
        state.set_territory_vector_fort("Bangalore")
        state.set_territory_vector_fort("Erode")
        state.set_territory_vector_fort("Palgautcherry")
        # 50% chance to remove one outer fort
        if np.random.random() < 0.5:
            remove = np.random.choice(["Bednore", "Mangalore"])
            state.set_territory_vector_empty(remove)
        self._randomize_cards(state)
        return state

    # ══════════════════════════════════════════════
    # Stage 1: "Full Game" — Turn 1, default (with variants)
    # ══════════════════════════════════════════════

    def _t1a(self):
        """Standard default setup."""
        state = GameState()
        state.default_setup()
        return state

    def _t1b(self):
        """Default with 1 random outer fort removed."""
        state = GameState()
        state.default_setup()
        remove = np.random.choice(["Darwar", "Bednore", "Palgautcherry"])
        state.set_territory_vector_empty(remove)
        return state

    def _t1c(self):
        """Default with 1 extra British fresh army."""
        state = GameState()
        state.default_setup()
        extra = np.random.choice(["Pune", "Goa", "Anantapur", "Vizag"])
        state.set_territory_vector_fresh_army(extra)
        return state

    def _t1d(self):
        """Default with 1-2 Mysore cards removed."""
        state = GameState()
        state.default_setup()
        num_remove = np.random.randint(1, 3)
        indices = np.random.choice(6, size=num_remove, replace=False)
        for idx in indices:
            state.use_card_mysore_by_value(int(idx))
        return state
