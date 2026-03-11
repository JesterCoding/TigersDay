import java.util.ArrayList;
import java.util.List;

/**
 * Represents a single territory (node) on the board.
 * Mirrors the NODES entries in tiger-day.html exactly.
 */
public class Territory {

    public enum Owner { BRITISH, MYSORE, EMPTY }

    private final String  name;
    private       Owner   owner;
    private final boolean keyCity;
    private final boolean coastal;
    private final List<String> adjacent = new ArrayList<>();

    public Territory(String name, Owner owner, boolean keyCity, boolean coastal) {
        this.name    = name;
        this.owner   = owner;
        this.keyCity = keyCity;
        this.coastal = coastal;
    }

    // ── Getters ────────────────────────────────────────────────────
    public String       getName()     { return name; }
    public Owner        getOwner()    { return owner; }
    public boolean      isKeyCity()   { return keyCity; }
    public boolean      isCoastal()   { return coastal; }
    public List<String> getAdjacent() { return adjacent; }

    // ── Mutators ───────────────────────────────────────────────────
    public void setOwner(Owner o) { this.owner = o; }

    void addAdjacent(String other) { adjacent.add(other); }

    // ── Serialise to JSON fragment ─────────────────────────────────
    public String toJson() {
        return String.format(
                "{\"name\":\"%s\",\"owner\":\"%s\",\"keyCity\":%b,\"coastal\":%b,\"adjacent\":[%s]}",
                name,
                owner.name().toLowerCase(),
                keyCity,
                coastal,
                String.join(",", adjacent.stream().map(a -> "\"" + a + "\"").toList())
        );
    }

    @Override
    public String toString() {
        return String.format("Territory{%s, owner=%s, key=%b}", name, owner, keyCity);
    }
}