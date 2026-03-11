/**
 * Single source of truth for all game rules and progression.
 *
 * Turn structure (mirrors the sidebar rules in tiger-day.html):
 *   • The game has MAX_TURNS turns.
 *   • Each turn: British moves first, then Mysore.
 *   • A player may move one of their territories' armies to an adjacent territory.
 *   • Capture: moving into an enemy or empty territory transfers ownership.
 *   • British win: hold all 5 key cities.
 *   • Mysore win: survive all MAX_TURNS turns without British holding all key cities.
 */
public class GameState {

    // ── Configurable constants ────────────────────────────────────
    public static final int MAX_TURNS = 4;

    public enum Phase { BRITISH_MOVE, MYSORE_MOVE, GAME_OVER }

    // ── State ─────────────────────────────────────────────────────
    private final GameBoard board;
    private Phase  phase  = Phase.BRITISH_MOVE;
    private int    turn   = 1;
    private String winner = null;   // set when the game ends

    public GameState() {
        this.board = new GameBoard();
    }

    // ── Accessors ─────────────────────────────────────────────────
    public GameBoard getBoard()   { return board; }
    public Phase     getPhase()   { return phase; }
    public int       getTurn()    { return turn;  }
    public String    getWinner()  { return winner; }
    public boolean   isOver()     { return phase == Phase.GAME_OVER; }

    // ═════════════════════════════════════════════════════════════
    //  CORE ACTION: applyMove
    // ═════════════════════════════════════════════════════════════

    /**
     * Attempt to move a piece from {@code from} to {@code to} on behalf of {@code player}.
     *
     * Rules checked:
     *   1. Game must not already be over.
     *   2. Player must match the current phase.
     *   3. Source territory must be owned by the player.
     *   4. Destination must be adjacent to the source.
     *   5. Cannot move into a territory you already own (must attack or advance).
     *
     * On success, ownership of the destination changes to the player,
     * the phase advances, and victory is checked.
     */
    public MoveResult applyMove(String playerStr, String from, String to) {

        // ── Pre-conditions ────────────────────────────────────────
        if (isOver())
            return MoveResult.invalid("The game is already over — " + winner + " has won.");

        Territory.Owner player;
        try {
            player = Territory.Owner.valueOf(playerStr.toUpperCase());
        } catch (IllegalArgumentException e) {
            return MoveResult.invalid("Unknown player: " + playerStr);
        }

        if (!phaseMatchesPlayer(player))
            return MoveResult.invalid("It is not " + playerStr + "'s turn (current phase: " + phase + ").");

        Territory src = board.get(from);
        Territory dst = board.get(to);

        if (src == null) return MoveResult.invalid("Unknown territory: " + from);
        if (dst == null) return MoveResult.invalid("Unknown territory: " + to);

        if (src.getOwner() != player)
            return MoveResult.invalid("You do not control " + from + ".");

        if (!board.isAdjacent(from, to))
            return MoveResult.invalid(from + " is not adjacent to " + to + ".");

        if (dst.getOwner() == player)
            return MoveResult.invalid("You already control " + to + ".");

        // ── Apply ─────────────────────────────────────────────────
        dst.setOwner(player);

        // ── Victory check ─────────────────────────────────────────
        if (board.britishControlsAllKeyCities()) {
            return endGame("british");
        }

        // ── Advance phase / turn ──────────────────────────────────
        advancePhase();

        if (isOver()) {
            // Turn limit reached after phase advance
            return endGame("mysore");
        }

        return MoveResult.ok(serializeBoard(), turn, phase.name());
    }

    // ═════════════════════════════════════════════════════════════
    //  PASS (player skips their move this impulse)
    // ═════════════════════════════════════════════════════════════

    public MoveResult applyPass(String playerStr) {
        if (isOver())
            return MoveResult.invalid("The game is already over.");

        Territory.Owner player;
        try {
            player = Territory.Owner.valueOf(playerStr.toUpperCase());
        } catch (IllegalArgumentException e) {
            return MoveResult.invalid("Unknown player: " + playerStr);
        }

        if (!phaseMatchesPlayer(player))
            return MoveResult.invalid("It is not " + playerStr + "'s turn.");

        advancePhase();

        if (isOver()) return endGame("mysore");

        return MoveResult.ok(serializeBoard(), turn, phase.name());
    }

    // ═════════════════════════════════════════════════════════════
    //  FULL STATE SNAPSHOT  (sent on initial connect & after each move)
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

    private String serializeBoard() {
        return board.toJson();
    }

    private boolean phaseMatchesPlayer(Territory.Owner player) {
        return switch (phase) {
            case BRITISH_MOVE -> player == Territory.Owner.BRITISH;
            case MYSORE_MOVE  -> player == Territory.Owner.MYSORE;
            case GAME_OVER    -> false;
        };
    }

    private void advancePhase() {
        switch (phase) {
            case BRITISH_MOVE -> phase = Phase.MYSORE_MOVE;
            case MYSORE_MOVE  -> {
                if (turn >= MAX_TURNS) {
                    phase  = Phase.GAME_OVER;
                    winner = "mysore";           // survived all turns
                } else {
                    turn++;
                    phase = Phase.BRITISH_MOVE;
                }
            }
            case GAME_OVER -> {}
        }
    }

    private MoveResult endGame(String w) {
        phase  = Phase.GAME_OVER;
        winner = w;
        return MoveResult.gameOver(w, serializeBoard(), turn);
    }

    @Override
    public String toString() {
        return String.format("GameState{turn=%d/%d, phase=%s, winner=%s}", turn, MAX_TURNS, phase, winner);
    }
}