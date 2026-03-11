import java.util.Set;

public class GameNode {

    private final boolean isKey; //keeps track of if the node is a tree
    private Owner piece; // who is on a node, if any
    private final Set<GameNode> adjacency; // who is next to this node
    private final boolean isCoast; //is the territory on the coast

    public GameNode() {
        isKey = false;
        piece = Owner.Empty;
        adjacency = null;
        isCoast = false;
    }

    public GameNode(boolean key, Owner own, Set<GameNode> adj, boolean coast){
        isKey = key;
        piece = own;
        adjacency = adj;
        isCoast = coast;
    }

    public Owner getPiece() {
        return piece;
    }

    public boolean isKey() {
        return isKey;
    }

    public Set<GameNode> getAdjacency() {
        return adjacency;
    }

    public void setOwner(Owner newOwner) {
        piece = newOwner;
    }

    public boolean isCoast() {
        return isCoast;
    }
}
