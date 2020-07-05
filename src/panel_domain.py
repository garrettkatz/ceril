import numpy as np
import copct as co
import geom as gm
import smile_state as st

M_causes = 3 # length of longest directly caused sequence
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
        position = (2.5, 0., 0.)
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
        if state.smile.gripping[hand] != "nothing": return False
        state.smile.gripping[hand] = name

        # get named thing's grasp, transform to current position, and run robot motion planner
        thing = state.smile.things[name]
        G = thing.grasp # transformation matrix for grasp
        M = gm.smile_rotation(thing.rotation, d=4) # transformation matrix for thing
        M[:3,3] = thing.position # including translation
        targets = M.dot(G)
        base, joints, success = state.robot.plan_motion(state.smile, targets, verbose=1)
        
        if not success: return False
        
        state.robot.base_x, state.robot.base_y, state.robot.base_a = base
        state.robot.arm_joints = joints
        
        return state

    def release(state, hand, position, rotation):
        if state.smile.gripping[hand] == "nothing": return False
        name = state.smile.gripping[hand]
        state.smile.gripping[hand] = "nothing"
        thing = state.smile.things[name]
        thing.position = position
        thing.rotation = rotation

        # get named thing's grasp, transform to target position, and run robot motion planner
        G = thing.grasp # transformation matrix for grasp
        M = gm.smile_rotation(rotation, d=4) # transformation matrix for target
        M[:3,3] = position # including translation
        targets = M.dot(G)
        base, joints, success = state.robot.plan_motion(state.smile, targets, verbose=1)
        
        if not success: return False
        
        state.robot.base_x, state.robot.base_y, state.robot.base_a = base
        state.robot.arm_joints = joints

        return state
    
    def trigger(state, hand, control):
        if state.smile.gripping[hand] != "nothing": return False
        # get control's grasp, run robot motion planner
        return state

    def loosen(state, hand, host_bond, host, guest_bond, guest, tightness):
        if state.smile.gripping[hand] != guest: return False
        return state

    return dict(locals())


if __name__ == "__main__":
    
    # load demo sequence
    import parse_demo as pd
    # print(pd)    
    # def print_import(mod): print(mod)
    # print_import(pd)

    states, actions = pd.parse_demo("../demos/panel")
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
    
