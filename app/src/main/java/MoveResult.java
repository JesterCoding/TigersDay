/**
 * Returned by GameState after every attempted move or action.
 * Serialises cleanly to the JSON the browser expects.
 */
public class MoveResult {

    public enum Status { OK, INVALID, GAME_OVER }

    private final Status  status;
    private final String  reason;     // human-readable explanation (always set)
    private final String  winner;     // "british" | "mysore" | null
    private final String  boardJson;  // full board state after the move (null if invalid)
    private final int     turn;
    private final String  phase;

    private MoveResult(Status status, String reason, String winner,
                       String boardJson, int turn, String phase) {
        this.status    = status;
        this.reason    = reason;
        this.winner    = winner;
        this.boardJson = boardJson;
        this.turn      = turn;
        this.phase     = phase;
    }

    // ── Factory methods ────────────────────────────────────────────

    public static MoveResult ok(String boardJson, int turn, String phase) {
        return new MoveResult(Status.OK, "Move accepted", null, boardJson, turn, phase);
    }

    public static MoveResult invalid(String reason) {
        return new MoveResult(Status.INVALID, reason, null, null, -1, null);
    }

    public static MoveResult gameOver(String winner, String boardJson, int turn) {
        return new MoveResult(Status.GAME_OVER, winner + " wins!", winner, boardJson, turn, "GAME_OVER");
    }

    // ── Accessors ──────────────────────────────────────────────────

    public boolean  isOk()       { return status == Status.OK; }
    public boolean  isGameOver() { return status == Status.GAME_OVER; }
    public String   getWinner()  { return winner; }
    public String   getReason()  { return reason; }

    // ── JSON serialisation ─────────────────────────────────────────

    public String toJson() {
        StringBuilder sb = new StringBuilder("{");
        sb.append("\"type\":\"MOVE_RESULT\",");
        sb.append("\"status\":\"").append(status.name().toLowerCase()).append("\",");
        sb.append("\"reason\":\"").append(escape(reason)).append("\",");
        sb.append("\"turn\":").append(turn).append(",");

        if (phase != null)
            sb.append("\"phase\":\"").append(phase).append("\",");

        if (winner != null)
            sb.append("\"winner\":\"").append(winner).append("\",");

        if (boardJson != null)
            sb.append("\"board\":").append(boardJson);
        else
            sb.append("\"board\":null");

        sb.append("}");
        return sb.toString();
    }

    private static String escape(String s) {
        return s == null ? "" : s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    @Override
    public String toString() {
        return String.format("MoveResult{%s, reason='%s', winner=%s}", status, reason, winner);
    }
}