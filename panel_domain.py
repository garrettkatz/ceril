"""
primitives:

grasp(hand, thing): grasps the thing with hand
move(thing, position, rotation): moves the thing to given pose
release(hand, position, rotation): releases whatever thing in hand at given pose
trigger(hand, toggle): changes toggle state with hand
loosen(hand, host bond, host thing, guest bond, guest thing): loosen thing bond with hand

higher-level tasks:
unscrew(hand, screw):
    [grasp(hand, screw), loosen(hand, host bond, host thing, guest bond, guest thing)]
remove_screw(hand, screw):
    [unscrew, release]
retire_screw(hand, screw):
    [trigger, remove_screw, trigger]
"""
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
            g.add((state_tuples[0], "remove_screw", (hand, name)))
    if len(v) == 3:
        if tasks == ("trigger","remove_screw","trigger"):
            hand, name = args[1]
            g.add((state_tuples[0], "retire_screw", (hand, name)))
    return g


if __name__ == "__main__":
    
    # load demo sequence
    import parse_demo as pd
    states, actions = pd.parse_demo("demos/test")
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
    
    # # Display results
    # print('Observed w:')
    # print(w)
    # print('Singleton sub-covers:')
    # for jk in itr.combinations(range(7),2):
    #     if len(g[jk])>0:
    #         print("sub-seq from %d to %d covered by: %s"%(jk[0], jk[1], g[jk]))
    # print('Top-level covers:')
    # print([u for (u,_,_,_,_) in tlcovs])
    # print('MC top-level covers:')
    # print([u for (u,_,_,_,_) in tlcovs_ml])
