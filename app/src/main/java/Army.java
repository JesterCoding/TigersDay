public class Army {
    private GameNode location; // what is the location of this army
    private boolean isTired; // is the army tired?

    public Army(GameNode loc, boolean tired){
        location = loc;
        isTired = tired;
    }

    private boolean canMove(GameNode newLocation){
        return  !isTired
                && location.getAdjacency().contains(newLocation)
                && newLocation.getOwner() != Owner.British;
    }

    public void resolve(GameNode newLocation) {
        if (canMove(newLocation) && newLocation.getOwner() == Owner.Empty) {
            location = newLocation;
            isTired = true;
        }
        // come back to this

    }

    private void attack() {

    }

    public GameNode getLocation() {
        return location;
    }

    public boolean getTired() {
        return isTired;
    }


}
