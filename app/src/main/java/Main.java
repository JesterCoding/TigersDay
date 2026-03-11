/**
 * Entry point.
 *
 * Usage:
 *   ./gradlew run
 *   — or —
 *   java -jar tigers-day-1.0.jar
 *
 * Then open tiger-day.html in a browser.
 * The browser will connect to ws://localhost:8887 automatically.
 */
public class Main {

    private static final int PORT = 8887;

    public static void main(String[] args) throws InterruptedException {
        GameServer server = new GameServer(PORT);
        server.start();

        // Block the main thread — the WebSocket server runs its own daemon threads.
        // Press Ctrl+C to stop.
        Thread.currentThread().join();
    }
}