import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;
import org.json.JSONObject;

import java.net.InetSocketAddress;
import java.util.Collection;

/**
 * WebSocket server that bridges the browser (tiger-day.html) and GameState.
 *
 * Port: 8887 (ws://localhost:8887)
 *
 * ── Inbound message types (browser → Java) ────────────────────────────────
 *
 * MOVE   { "type":"MOVE",  "player":"british", "from":"X", "to":"Y" }
 * CARD   { "type":"CARD",  "player":"mysore", "cardName":"..." }       <-- NEW
 * PASS   { "type":"PASS",  "player":"british"|"mysore" }
 * RESET  { "type":"RESET" }
 * PING   { "type":"PING"  }
 *
 * ── Outbound message types (Java → browser) ───────────────────────────────
 *
 * STATE        full board snapshot          (sent on connect and after RESET)
 * MOVE_RESULT  result of a MOVE, CARD or PASS (valid/invalid/game_over + board)
 * PONG         { "type":"PONG" }
 * ERROR        { "type":"ERROR", "message":"..." }
 */
public class GameServer extends WebSocketServer {

    private GameState state = new GameState();

    public GameServer(int port) {
        super(new InetSocketAddress(port));
        setReuseAddr(true);
    }

    // ═════════════════════════════════════════════════════════════
    //  WebSocket lifecycle
    // ═════════════════════════════════════════════════════════════

    @Override
    public void onOpen(WebSocket conn, ClientHandshake handshake) {
        System.out.printf("[CONNECT] %s%n", conn.getRemoteSocketAddress());
        // Send the full current state so any browser that connects mid-game catches up
        conn.send(state.fullStateJson());
    }

    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        System.out.printf("[DISCONNECT] %s — %s%n", conn.getRemoteSocketAddress(), reason);
    }

    @Override
    public void onError(WebSocket conn, Exception ex) {
        System.err.printf("[ERROR] %s — %s%n",
                conn != null ? conn.getRemoteSocketAddress() : "server", ex.getMessage());
    }

    @Override
    public void onStart() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("  The Tiger's Day — Game Server");
        System.out.printf ("  Listening on ws://localhost:%d%n", getPort());
        System.out.println("═══════════════════════════════════════");
    }

    // ═════════════════════════════════════════════════════════════
    //  Message dispatch
    // ═════════════════════════════════════════════════════════════

    @Override
    public void onMessage(WebSocket conn, String raw) {
        System.out.printf("[MSG] %s → %s%n", conn.getRemoteSocketAddress(), raw);
        try {
            JSONObject msg  = new JSONObject(raw);
            String     type = msg.getString("type").toUpperCase();

            switch (type) {

                case "MOVE" -> {
                    String player = msg.getString("player");
                    String from   = msg.getString("from");
                    String to     = msg.getString("to");
                    MoveResult result = state.applyMove(player, from, to);
                    System.out.println("[RESULT] " + result);

                    // Broadcast the result to everyone so multiple observers stay in sync
                    broadcast(result.toJson());
                }

                // NEW: Route the Mysore card action to the updated GameState
                case "CARD" -> {
                    String cardName = msg.optString("cardName", "Pass");
                    MoveResult result = state.playMysoreCard(cardName);
                    System.out.println("[CARD PLAYED] " + result);
                    broadcast(result.toJson());
                }

                case "PASS" -> {
                    String player = msg.getString("player");
                    // If Mysore passes instead of playing a card, we can route it through applyPass
                    // or treat it as a blank playMysoreCard("Pass").
                    MoveResult result = state.applyPass(player);
                    System.out.println("[PASS] " + result);
                    broadcast(result.toJson());
                }

                case "RESET" -> {
                    state = new GameState();
                    System.out.println("[RESET] Game restarted.");
                    broadcast(state.fullStateJson());
                }

                case "PING" -> conn.send("{\"type\":\"PONG\"}");

                default -> conn.send(error("Unknown message type: " + type));
            }

        } catch (Exception e) {
            System.err.println("[PARSE ERROR] " + e.getMessage());
            conn.send(error("Bad message format: " + e.getMessage()));
        }
    }

    // ═════════════════════════════════════════════════════════════
    //  Helpers
    // ═════════════════════════════════════════════════════════════

    private static String error(String msg) {
        return "{\"type\":\"ERROR\",\"message\":\"" + msg.replace("\"", "\\\"") + "\"}";
    }
}