import numpy as np
from game.state import GameState
from game.engine import MoveEngine
from game.winchecker import WinChecker


class GameUpdater:

    def __init__(self):
        self.engine = MoveEngine()
        self.checker = WinChecker()
        self._build_offset_table()

    def _build_offset_table(self):
        """Precompute (name, start, end, move_type) for each action category."""
        self.offsets = []
        running = 0
        for name, size, move_type in MoveEngine.MOVE_SPACE:
            self.offsets.append((name, running, running + size, move_type))
            running += size

    def _decode_move(self, move_idx):
        """Given a move index (0-635), return (action_name, local_idx)."""
        for name, start, end, move_type in self.offsets:
            if start <= move_idx < end:
                return name, move_idx - start
        raise ValueError(f"Invalid move index: {move_idx}")

    def _territory_name(self, idx):
        return GameState.TERRITORIES[idx]

    def _has_fort(self, state, territory_idx):
        return state.vector[GameState.IDX_TERRITORIES_OFFSET + 3 * territory_idx + 2]

    def _is_fresh(self, state, territory_idx):
        return state.vector[GameState.IDX_TERRITORIES_OFFSET + 3 * territory_idx]

    def _is_tired(self, state, territory_idx):
        return state.vector[GameState.IDX_TERRITORIES_OFFSET + 3 * territory_idx + 1]

    def apply_move(self, state, move_idx):
        """Apply a move to the game state.
        Returns: (new_state, game_result, luck_turn_info)
          - new_state: GameState after the move
          - game_result: 0 (ongoing), 1 (British win), -1 (Mysore win)
          - luck_turn_info: None or {"player": str, "reason": str}
        """
        new_state = state.copy()
        british_strength_bonus = 0
        luck_turn_info = None

        action_name, local_idx = self._decode_move(move_idx)

        # ── Phase 1: British Move ──
        if action_name == "Move":
            src = int(MoveEngine.EDGE_SOURCES[local_idx])
            dst = int(MoveEngine.EDGE_DESTS[local_idx])
            if self._has_fort(new_state, dst):
                # Attack fort: army stays at source, becomes tired, queue combat
                new_state.set_territory_vector_tired_army(self._territory_name(src))
                new_state.queue_combat_by_value(src, dst)
            else:
                # Move into empty: army moves to dest as tired, source emptied
                new_state.set_territory_vector_empty(self._territory_name(src))
                new_state.set_territory_vector_tired_army(self._territory_name(dst))
            new_state.update_who_to_move()

        elif action_name == "Tire":
            # Trapped fresh army tires in place
            new_state.set_territory_vector_tired_army(self._territory_name(local_idx))
            new_state.update_who_to_move()

        # ── Phase 2: Mysore Card ──
        elif action_name == "Sepoy Mutiny":
            # Remove British army from non-key territory
            new_state.set_territory_vector_empty(self._territory_name(local_idx))
            new_state.use_card_mysore_by_name("Sepoy Mutiny")
            new_state.update_who_to_move()

        elif action_name == "French Alliance":
            # Deploy fort on empty territory adjacent to existing fort
            new_state.set_territory_vector_fort(self._territory_name(local_idx))
            new_state.use_card_mysore_by_name("French Alliance")
            new_state.update_who_to_move()

        elif action_name == "Monsoon":
            # Flip fresh army to tired
            new_state.set_territory_vector_tired_army(self._territory_name(local_idx))
            new_state.use_card_mysore_by_name("Monsoon")
            new_state.update_who_to_move()

        elif action_name == "Cavalry Raid":
            # Force British to randomly discard a card
            new_state.use_card_mysore_by_name("Cavalry Raid")
            new_state.update_who_to_move()
            if np.any(new_state.vector[GameState.IDX_BRITISH_CARDS]):
                luck_turn_info = {"player": "british", "reason": "cavalry_raid"}

        elif action_name == "Sea Trade":
            # Recover a used Mysore card (local_idx = target card index)
            new_state.vector[GameState.IDX_MYSORE_CARDS_OFFSET + local_idx] = True
            new_state.use_card_mysore_by_name("Sea Trade")
            new_state.update_who_to_move()

        elif action_name == "Mysore Power":
            # Play Mysore card for combat strength
            new_state.use_card_mysore_by_value(local_idx)
            new_state.set_combat_strength(local_idx)
            new_state.update_who_to_move()

        elif action_name in ("Draw Iron Rockets", "Draw Sepoy Mutiny", "Draw French Alliance"):
            source_card_map = {
                "Draw Iron Rockets": 0,
                "Draw Sepoy Mutiny": 1,
                "Draw French Alliance": 2,
            }
            source_idx = source_card_map[action_name]
            new_state.use_card_mysore_by_value(source_idx)
            new_state.vector[GameState.IDX_MYSORE_CARDS_OFFSET + local_idx] = True
            new_state.update_who_to_move()

        elif action_name == "Pass Mysore":
            new_state.update_who_to_move()

        # ── Phase 3: British Card ──
        elif action_name == "Highlanders":
            # Deploy fresh army on empty coastal territory
            new_state.set_territory_vector_fresh_army(self._territory_name(local_idx))
            new_state.use_card_british_by_name("Highlanders")

        elif action_name == "Royal Navy":
            # Decode flattened 23x9 matrix
            num_coastal = len(MoveEngine.COASTAL_INDICES)
            src = local_idx // num_coastal
            coastal_offset = local_idx % num_coastal
            dst = int(MoveEngine.COASTAL_INDICES[coastal_offset])

            if self._has_fort(new_state, dst):
                # Attack fort: army stays at source, becomes tired, queue combat
                new_state.set_territory_vector_tired_army(self._territory_name(src))
                new_state.queue_combat_by_value(src, dst)
            else:
                # Move army preserving fresh/tired status
                was_fresh = self._is_fresh(new_state, src)
                new_state.set_territory_vector_empty(self._territory_name(src))
                if was_fresh:
                    new_state.set_territory_vector_fresh_army(self._territory_name(dst))
                else:
                    new_state.set_territory_vector_tired_army(self._territory_name(dst))
            new_state.use_card_british_by_name("Royal Navy")

        elif action_name == "Divide and Rule":
            # Move non-key fort to adjacent empty territory
            src = int(MoveEngine.EDGE_SOURCES[local_idx])
            dst = int(MoveEngine.EDGE_DESTS[local_idx])
            new_state.set_territory_vector_empty(self._territory_name(src))
            new_state.set_territory_vector_fort(self._territory_name(dst))
            new_state.use_card_british_by_name("Divide and Rule")

        elif action_name == "Force March":
            # Move tired army along edge
            src = int(MoveEngine.EDGE_SOURCES[local_idx])
            dst = int(MoveEngine.EDGE_DESTS[local_idx])
            if self._has_fort(new_state, dst):
                # Attack fort: army stays at source, queue combat
                new_state.queue_combat_by_value(src, dst)
            else:
                new_state.set_territory_vector_empty(self._territory_name(src))
                new_state.set_territory_vector_tired_army(self._territory_name(dst))
            new_state.use_card_british_by_name("Force March")

        elif action_name == "Princely States":
            # Deploy tired army on empty key territory
            new_state.set_territory_vector_tired_army(self._territory_name(local_idx))
            new_state.use_card_british_by_name("Princely States")

        elif action_name == "British Power":
            # Play British card for combat strength
            british_strength_bonus = GameState.CARD_VALUE[local_idx]
            new_state.use_card_british_by_value(local_idx)

        elif action_name in ("Draw Wall Breach", "Draw Highlanders", "Draw Royal Navy"):
            source_card_map = {
                "Draw Wall Breach": 0,
                "Draw Highlanders": 1,
                "Draw Royal Navy": 2,
            }
            source_idx = source_card_map[action_name]
            new_state.use_card_british_by_value(source_idx)
            new_state.vector[GameState.IDX_BRITISH_CARDS_OFFSET + local_idx] = True

        elif action_name == "Pass British":
            pass

        # ── Post-Phase-3 processing ──
        is_phase3 = action_name in (
            "Highlanders", "Royal Navy", "Divide and Rule", "Force March",
            "Princely States", "British Power", "Draw Wall Breach",
            "Draw Highlanders", "Draw Royal Navy", "Pass British"
        )

        if is_phase3:
            # Resolve combat if queued
            if np.any(new_state.vector[GameState.IDX_COMBATANTS]):
                combat_luck = self._resolve_combat(new_state, british_strength_bonus)
                if combat_luck is not None:
                    luck_turn_info = combat_luck

            # Check for British win immediately after combat
            game_result = self.checker.check(new_state)
            if game_result != 0:
                return new_state, game_result, luck_turn_info

            # Advance to next impulse
            new_state.set_who_to_move_by_name("British Move")

            # Check if turn is over (no fresh armies remain)
            fresh = new_state.vector[GameState.IDX_TERRITORIES_OFFSET::3][:23]
            if not np.any(fresh):
                self._advance_turn(new_state)

        # Final win check
        game_result = self.checker.check(new_state)
        return new_state, game_result, luck_turn_info

    def _resolve_combat(self, state, british_strength_bonus):
        """Resolve a queued battle in-place. Returns luck_turn_info or None."""
        attacker_idx = int(np.argmax(
            state.vector[GameState.IDX_COMBATANTS_OFFSET:GameState.IDX_COMBATANTS_DEFENDER_OFFSET]))
        defender_idx = int(np.argmax(
            state.vector[GameState.IDX_COMBATANTS_DEFENDER_OFFSET:GameState.IDX_COMBATANTS_DEFENDER_OFFSET + 23]))

        neighbors = MoveEngine.ADJACENCY_MATRIX[defender_idx]

        fresh = state.vector[GameState.IDX_TERRITORIES_OFFSET::3][:23]
        tired = state.vector[GameState.IDX_TERRITORIES_OFFSET + 1::3][:23]
        fort = state.vector[GameState.IDX_TERRITORIES_OFFSET + 2::3][:23]

        # Mysore strength: adjacent forts + card bonus
        mysore_card_bonus = int(np.argmax(state.vector[GameState.IDX_COMBAT_STRENGTH]))
        mysore_strength = int(np.sum(neighbors & fort)) + mysore_card_bonus

        # British strength: adjacent armies + card bonus
        british_army = fresh | tired
        british_strength = int(np.sum(neighbors & british_army)) + british_strength_bonus

        luck_turn_info = None

        if british_strength > mysore_strength:
            # British wins: fort removed, army moves to defender territory
            state.set_territory_vector_empty(self._territory_name(attacker_idx))
            state.set_territory_vector_tired_army(self._territory_name(defender_idx))
            # Mysore must discard
            if np.any(state.vector[GameState.IDX_MYSORE_CARDS]):
                luck_turn_info = {"player": "mysore", "reason": "combat_loss"}
        else:
            # Mysore wins (ties go to Mysore): army stays, already tired
            # British must discard
            if np.any(state.vector[GameState.IDX_BRITISH_CARDS]):
                luck_turn_info = {"player": "british", "reason": "combat_loss"}

        # Clear combat state
        state.clear_combat()

        return luck_turn_info

    def _advance_turn(self, state):
        """Advance to the next turn. Reset cards and refresh armies."""
        current = state.get_turn()
        if current < 4:
            state.set_turn(current + 1)
            state.reset_cards()
            # Refresh all tired armies to fresh
            for i in range(23):
                offset = GameState.IDX_TERRITORIES_OFFSET + 3 * i
                if state.vector[offset + 1]:  # tired
                    state.vector[offset] = True       # fresh
                    state.vector[offset + 1] = False   # not tired
        # If turn == 4, game is over — winchecker catches this
