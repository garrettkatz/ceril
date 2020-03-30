import copct as co
import smile_state as st

def causes(v): 
    g = set() # set of possible causes
    state_tuples, tasks, args = zip(*v)
    # states = [st.from_tuple(s) for s in state_tuples]
    if len(v) == 2:
        if tasks == ("grasp","loosen"):
            hand, name = args[0]
            g.add((state_tuples[0], "unscrew", (hand, name)))
        if tasks == ("unscrew","release"):
            hand, name = args[0]
            g.add((state_tuples[0], "discard_screw", (hand, name)))
    if len(v) == 3:
        if tasks == ("trigger","discard_screw","trigger"):
            hand, name = args[1]
            g.add((state_tuples[0], "retire_screw", (name,)))
    return g

def htn_methods():

    def retire_screw(state, screw):
        hand = "LeftHand"
        return [
            ("trigger", hand, "toggle"),
            ("discard_screw", hand, screw),
            ("trigger", hand, "toggle"),
        ]

    def discard_screw(state, hand, screw):
        position = (10., 0., 0.)
        rotation = (0., 0., 0.)
        return [
            ("unscrew", hand, screw),
            ("release", hand, position, rotation),
        ]
    
    def unscrew(state, hand, screw):
        host_bond, host = "tube1bond", "pbox"
        guest_bond, tightness = "panelscrewbond", 0
        return [
            ("grasp", hand, screw),
            ("loosen", hand, host_bond, host, guest_bond, screw, tightness),
        ]

    return dict(locals())

def htn_operators():

    def grasp(state, hand, name):
        if state.gripping[hand] != "nothing": return False
        state.gripping[hand] = name
        # get named thing's grasp, transform to current position, and run robot motion planner
        return state

    def release(state, hand, position, rotation):
        if state.gripping[hand] == "nothing": return False
        name = state.gripping[hand]
        # get named thing's grasp, transform to target position, and run robot motion planner
        state.gripping[hand] = "nothing"
        thing = state.things[name]
        thing.position = position
        thing.rotation = rotation
        return state
    
    def trigger(state, hand, control):
        if state.gripping[hand] != "nothing": return False
        return state

    def loosen(state, hand, host_bond, host, guest_bond, guest, tightness):
        if state.gripping[hand] != guest: return False
        return state

    return dict(locals())


if __name__ == "__main__":
    
    # load demo sequence
    import parse_demo as pd
    states, actions = pd.parse_demo("../demos/test")
    tasks, args = zip(*[(a["name"], a["args"]) for a in actions])
    states = [s.tuplify() for s in states]
    # print(states)
    # print(tasks)
    # print(args)
    w = tuple(zip(states, tasks, args))

    # compute explanations
    status, tlcovs, g = co.explain(causes, w, M=3, verbose=True)
    # Prune by minimum cardinality
    tlcovs_ml, ml = co.minCardinalityTLCovers(tlcovs)
    
    print("Observed:")
    print(tasks)
    print("Top-level covers:")
    for (u,_,_,_,_) in tlcovs:
        states, tasks, args = zip(*u)
        print(tasks)
    
