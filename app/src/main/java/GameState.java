import java.util.HashMap;
import java.util.List;

/**
 * Updated GameState for Impulse-based turns.
 * A turn ends only when all British armies are 'tired'.
 */
public class GameState {

    public static final int MAX_TURNS = 5;

    public enum Phase {
        BRITISH_MOVE,
        MYSORE_CARD,
        BRITISH_CARD,
        RESOLVE_BATTLE,
        GAME_OVER
    }

    private Phase  phase  = Phase.BRITISH_MOVE;
    private int    turn   = 1;

    public GameState() {

    }

    // ── Accessors ─────────────────────────────────────────────────
    public boolean isOver() { return phase == Phase.GAME_OVER; }

    // ═════════════════════════════════════════════════════════════
    //  CORE ACTIONS
    // ═════════════════════════════════════════════════════════════

    public MoveResult applyMove(String playerStr, String from, String to) {
        if (isOver()) return MoveResult.invalid("Game Over.");

        Territory.Owner player = parsePlayer(playerStr);
        if (player == null) return MoveResult.invalid("Unknown player: " + playerStr);

        if (!phaseMatchesPlayer(player)) {
            return MoveResult.invalid("It is not " + playerStr + "'s turn (current phase: " + phase + ").");
        }

        Territory src = board.get(from);
        Territory dst = board.get(to);

        // Validation Logic
        if (src == null || dst == null) return MoveResult.invalid("Invalid territory.");
        if (src.getOwner() != Territory.Owner.BRITISH) return MoveResult.invalid("No British army there.");
        if (src.isTired()) return MoveResult.invalid("This army has already moved this turn.");
        if (!board.isAdjacent(from, to)) return MoveResult.invalid("Not adjacent.");

        // ── Execute Move ──────────────────────────────────────────
        // If destination is empty or enemy, British take it
        dst.setOwner(Territory.Owner.BRITISH);
        src.setOwner(Territory.Owner.EMPTY);

        // Mark the specific army as tired for this turn
        dst.setTired(true);

        // ── Check Victory ─────────────────────────────────────────
        if (board.britishControlsAllKeyCities()) {
            return endGame("british");
        }

        // After a British impulse, Mysore gets a chance to play a card
        phase = Phase.MYSORE_CARD;

        return MoveResult.ok(serializeBoard(), turn, phase.name());
    }

    /**
     * Mysore plays a power card.
     * After this, we check if the British have any fresh armies left.
     */
    public MoveResult playMysoreCard(String cardName) {
        if (phase != Phase.MYSORE_CARD) return MoveResult.invalid("Not the Mysore card phase.");

        // Logic for specific card effects would go here...

        advanceImpulse();
        return MoveResult.ok(serializeBoard(), turn, phase.name());
    }

    // ═════════════════════════════════════════════════════════════
    //  PASS (player skips their action this impulse)
    // ═════════════════════════════════════════════════════════════

    public MoveResult applyPass(String playerStr) {
        if (isOver()) return MoveResult.invalid("The game is already over.");

        Territory.Owner player = parsePlayer(playerStr);
        if (player == null) return MoveResult.invalid("Unknown player: " + playerStr);

        if (!phaseMatchesPlayer(player)) {
            return MoveResult.invalid("It is not " + playerStr + "'s turn.");
        }

        // Advance the state based on who passed
        if (phase == Phase.BRITISH_MOVE) {
            phase = Phase.MYSORE_CARD;
        } else if (phase == Phase.MYSORE_CARD) {
            advanceImpulse();
        }

        if (isOver()) return endGame("mysore");

        return MoveResult.ok(serializeBoard(), turn, phase.name());
    }

    // ═════════════════════════════════════════════════════════════
    //  FULL STATE SNAPSHOT (Used by GameServer on connect)
    // ═════════════════════════════════════════════════════════════

    /**
     * Returns a complete JSON snapshot of the current game state.
     * Sent to every newly-connecting browser and after every state change.
     */
    public String fullStateJson() {
        return String.format(
                "{\"type\":\"STATE\",\"turn\":%d,\"maxTurns\":%d,\"phase\":\"%s\",\"winner\":%s,\"board\":%s}",
                turn,
                MAX_TURNS,
                phase.name(),
                winner == null ? "null" : "\"" + winner + "\"",
                serializeBoard()
        );
    }

    // ═════════════════════════════════════════════════════════════
    //  PRIVATE HELPERS
    // ═════════════════════════════════════════════════════════════

    private void advanceImpulse() {
        if (board.hasReadyBritishArmies()) {
            // British still have fresh troops; back to their move
            phase = Phase.BRITISH_MOVE;
        } else {
            // All British armies are tired. End of the Turn.
            if (turn >= MAX_TURNS) {
                endGame("mysore");
            } else {
                turn++;
                board.resetTiredStatus(); // Refresh all British armies for the new turn
                phase = Phase.BRITISH_MOVE;
            }
        }
    }

    private MoveResult endGame(String w) {
        phase  = Phase.GAME_OVER;
        winner = w;
        return MoveResult.gameOver(w, serializeBoard(), turn);
    }

    private boolean phaseMatchesPlayer(Territory.Owner player) {
        return switch (phase) {
            case BRITISH_MOVE -> player == Territory.Owner.BRITISH;
            case MYSORE_CARD  -> player == Territory.Owner.MYSORE;
            case GAME_OVER    -> false;
        };
    }

    private Territory.Owner parsePlayer(String playerStr) {
        try {
            return Territory.Owner.valueOf(playerStr.toUpperCase());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }

    private String serializeBoard() {
        return board.toJson();
    }

    @Override
    public String toString() {
        return String.format("GameState{turn=%d/%d, phase=%s, winner=%s}", turn, MAX_TURNS, phase, winner);
    }
}