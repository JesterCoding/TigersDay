import java.util.*;

public class Game {

    private final Set<GameNode> allNodes;
    private int turn;

    public Game() {
        turn = 0;
        allNodes = new HashSet<>();
        Set<GameNode> bombayAdj = new HashSet<>();
        GameNode bombay = new GameNode(true, Owner.British, bombayAdj, true);
    }

}
