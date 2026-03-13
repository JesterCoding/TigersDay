import numpy as np
from game.state import GameState


class WinChecker:

    RESULT_ONGOING = 0
    RESULT_BRITISH_WIN = 1
    RESULT_MYSORE_WIN = -1

    NUM_KEYS = 5  # First 5 territories are key territories

    def check(self, state):
        """Check if the game is over.
        Returns: 0 (ongoing), 1 (British win), -1 (Mysore win)
        """
        fresh = state.vector[GameState.IDX_TERRITORIES_OFFSET::3][:23]
        tired = state.vector[GameState.IDX_TERRITORIES_OFFSET + 1::3][:23]

        # British win: army (fresh or tired) in all 5 key territories
        if (fresh[:self.NUM_KEYS] | tired[:self.NUM_KEYS]).all():
            return self.RESULT_BRITISH_WIN

        # Mysore win: no British armies anywhere on the board
        if not np.any(fresh) and not np.any(tired):
            return self.RESULT_MYSORE_WIN

        # Mysore win: survived turn 4 (all impulses exhausted)
        # Triggers when it's British Move phase in turn 4 but no fresh armies remain
        if (state.get_turn() == 4
                and state.get_who_to_move() == 0
                and not np.any(fresh)):
            return self.RESULT_MYSORE_WIN

        return self.RESULT_ONGOING
