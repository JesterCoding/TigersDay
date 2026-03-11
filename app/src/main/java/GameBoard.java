import java.util.*;
import java.util.stream.Collectors;

/**
 * Holds all territories and their connections.
 * Data mirrors the NODES and EDGES constants in tiger-day.html exactly.
 *
 * To change starting ownership, edit the add() calls in the constructor.
 * To change the map topology, edit the connect() calls.
 */
public class GameBoard {

    private final Map<String, Territory> territories = new LinkedHashMap<>();

    // ── Edges flagged as sea routes ───────────────────────────────
    private final Set<String> seaEdges = new HashSet<>();

    public GameBoard() {
        initTerritories();
        initEdges();
    }

    // ═════════════════════════════════════════════════════════════
    //  MAP DATA  –  keep in sync with tiger-day.html
    // ═════════════════════════════════════════════════════════════

    private void initTerritories() {
        // add(name, owner, isKeyCity, isCoastal)
        // ── Key cities ───────────────────────────────────────────
        add("Bombay",        Territory.Owner.BRITISH, true,  true);
        add("Hyderabad",     Territory.Owner.BRITISH, true,  false);
        add("Madras",        Territory.Owner.BRITISH, true,  true);
        add("Srirangapatna", Territory.Owner.MYSORE,  true,  false);
        add("Coimbatore",    Territory.Owner.MYSORE,  true,  false);

        // ── Regular territories ───────────────────────────────────
        add("Pune",          Territory.Owner.EMPTY,   false, false);
        add("Koppal",        Territory.Owner.EMPTY,   false, false);
        add("Vizag",         Territory.Owner.EMPTY,   false, true);
        add("Goa",           Territory.Owner.EMPTY,   false, true);
        add("Darwar",        Territory.Owner.MYSORE,  false, false);
        add("Anantapur",     Territory.Owner.EMPTY,   false, false);
        add("Bednore",       Territory.Owner.MYSORE,  false, false);
        add("Mangalore",     Territory.Owner.MYSORE,  false, true);
        add("Bangalore",     Territory.Owner.MYSORE,  false, false);
        add("Vellore",       Territory.Owner.EMPTY,   false, false);
        add("Mahé",          Territory.Owner.MYSORE,  false, true);
        add("Pondicherry",   Territory.Owner.EMPTY,   false, true);
        add("Erode",         Territory.Owner.MYSORE,  false, false);
        add("Trichy",        Territory.Owner.EMPTY,   false, false);
        add("Palgautcherry", Territory.Owner.MYSORE,  false, false);
        add("Dindigul",      Territory.Owner.EMPTY,   false, false);
        add("Travancore",    Territory.Owner.BRITISH, false, true);
        add("Ceylon",        Territory.Owner.EMPTY,   false, true);
    }

    private void initEdges() {
        // connect(a, b)        → land route
        // connectSea(a, b)     → sea route (dashed on map)
        connect("Bombay",        "Pune");
        connect("Bombay",        "Goa");
        connect("Pune",          "Koppal");
        connect("Pune",          "Darwar");
        connect("Pune",          "Goa");
        connect("Hyderabad",     "Koppal");
        connect("Hyderabad",     "Anantapur");
        connect("Hyderabad",     "Vizag");
        connect("Koppal",        "Anantapur");
        connect("Koppal",        "Bednore");
        connect("Darwar",        "Goa");
        connect("Darwar",        "Bednore");
        connect("Anantapur",     "Vellore");
        connect("Goa",           "Mangalore");
        connect("Bednore",       "Mangalore");
        connect("Bednore",       "Bangalore");
        connect("Madras",        "Vellore");
        connect("Madras",        "Pondicherry");
        connect("Madras",        "Vizag");
        connect("Madras",        "Anantapur");
        connect("Vellore",       "Bangalore");
        connect("Mangalore",     "Srirangapatna");
        connect("Bangalore",     "Srirangapatna");
        connect("Srirangapatna", "Mahé");
        connect("Srirangapatna", "Erode");
        connect("Erode",         "Coimbatore");
        connect("Erode",         "Trichy");
        connect("Erode",         "Pondicherry");
        connect("Erode",         "Vellore");
        connect("Pondicherry",   "Trichy");
        connect("Mahé",          "Coimbatore");
        connect("Mahé",          "Palgautcherry");
        connect("Coimbatore",    "Palgautcherry");
        connect("Coimbatore",    "Dindigul");
        connect("Trichy",        "Dindigul");
        connect("Palgautcherry", "Travancore");
        connect("Dindigul",      "Travancore");
        connectSea("Dindigul",   "Ceylon");
        connectSea("Travancore", "Ceylon");
    }

    // ═════════════════════════════════════════════════════════════
    //  PUBLIC API
    // ═════════════════════════════════════════════════════════════

    /** Returns the territory with that name, or null. */
    public Territory get(String name) {
        return territories.get(name);
    }

    /** Returns all territories. */
    public Collection<Territory> all() {
        return Collections.unmodifiableCollection(territories.values());
    }

    /** True if there is any edge (land or sea) between a and b. */
    public boolean isAdjacent(String a, String b) {
        Territory t = territories.get(a);
        return t != null && t.getAdjacent().contains(b);
    }

    /** True if the edge between a and b is a sea route. */
    public boolean isSeaRoute(String a, String b) {
        return seaEdges.contains(edgeKey(a, b));
    }

    /** True when the British player holds all five key cities. */
    public boolean britishControlsAllKeyCities() {
        return territories.values().stream()
                .filter(Territory::isKeyCity)
                .allMatch(t -> t.getOwner() == Territory.Owner.BRITISH);
    }

    /** All territories currently owned by the given player. */
    public List<Territory> territoriesOwnedBy(Territory.Owner owner) {
        return territories.values().stream()
                .filter(t -> t.getOwner() == owner)
                .collect(Collectors.toList());
    }

    /** Key cities owned by the given player. */
    public List<Territory> keyCitiesOwnedBy(Territory.Owner owner) {
        return territories.values().stream()
                .filter(t -> t.isKeyCity() && t.getOwner() == owner)
                .collect(Collectors.toList());
    }

    /** Serialise the full board to a JSON array of territory objects. */
    public String toJson() {
        StringJoiner sj = new StringJoiner(",", "[", "]");
        for (Territory t : territories.values()) sj.add(t.toJson());
        return sj.toString();
    }

    // ═════════════════════════════════════════════════════════════
    //  PRIVATE HELPERS
    // ═════════════════════════════════════════════════════════════

    private void add(String name, Territory.Owner owner, boolean key, boolean coastal) {
        territories.put(name, new Territory(name, owner, key, coastal));
    }

    private void connect(String a, String b) {
        requireBoth(a, b);
        territories.get(a).addAdjacent(b);
        territories.get(b).addAdjacent(a);
    }

    private void connectSea(String a, String b) {
        connect(a, b);
        seaEdges.add(edgeKey(a, b));
    }

    /** Canonical undirected edge key so A↔B and B↔A map to the same string. */
    private String edgeKey(String a, String b) {
        return a.compareTo(b) < 0 ? a + "|" + b : b + "|" + a;
    }

    private void requireBoth(String a, String b) {
        if (!territories.containsKey(a)) throw new IllegalArgumentException("Unknown territory: " + a);
        if (!territories.containsKey(b)) throw new IllegalArgumentException("Unknown territory: " + b);
    }
}