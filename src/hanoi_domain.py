# M_causes = 3
# def causes(v):
#     """
#     Causal relation for the robotic imitation learning domain.
#     v is a sequence of intentions or actions.
#     Each element v[i] is of the form (state, task name, parameter values).
#     Returns the set of all possible causes of v.
#     """
#     g = set() # set of possible causes
#     clear_ids = ("discard-bin")
#     states, tasks, args = zip(*v)
#     if len(v) == 1:
#         if tasks == ("grasp",):
#             arm_name, object_id = args[0]
#             arm = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             # state tuple is (gripping, objects, controls)
#             asm_type = dict(states[0][1])[object_id]
#             if asm_type not in ("DockCase","DockDrawer"):
#                 g.add((states[0], "move unobstructed object",(object_id, arm, (), ())))
#         if tasks == ("release",):
#             arm_name, dM, dt = args[0]
#             arm = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             object_id = states[0][0][int(arm)][1]
#             asm_type = dict(states[0][1])[object_id]
#             if asm_type not in ("DockCase","DockDrawer"):
#                 g.add((states[0], "put down grasped object", args[0]))
#         if tasks == ("put down grasped object",):
#             arm_name, dM, dt = args[0]
#             arm = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             object_id = states[0][0][int(arm)][1]
#             g.add((states[0], "move unobstructed object", (object_id, dM, dt)))
#         if tasks == ("move unobstructed object",):
#             g.add((states[0],"move object", args[0]))
#         if tasks == ("move object",):
#             object_id, dM, dt = args[0]
#             g.add((states[0],"move object to free spot", (object_id,)))
#     if len(v)==2:
#         if tasks == ("move grasped object","release"):
#             arm_name, dest_id, dM, dt = args[0]
#             arm = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             object_id = states[0][0][int(arm)][1]
#             asm_type = dict(states[0][1])[object_id]
#             if asm_type not in ("DockCase","DockDrawer"):
#                 g.add((states[0], "put down grasped object", args[0]))
#         if tasks == ("grasp","put down grasped object"):
#             arm_name, object_id = args[0]
#             arm_0 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             arm_name, dest_id, dM, dt = args[1]
#             arm_1 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             asm_type = dict(states[0][1])[object_id]
#             if (arm_0==arm_1) and not (asm_type=="DockDrawer"):
#                 g.add((states[0],"move unobstructed object",(object_id, dest_id, dM, dt)))
#         if tasks == ("screw valve","screw valve"):
#             arms, rotations = zip(*args)
#             if arms[0]==arms[1]:
#                 g.add((states[0],"screw valve",(arms[0],sum(rotations))))
#         if tasks == ("screw valve","remove screw from valve"):
#             g.add((states[0],"remove screw from valve",()))
#         if tasks == ("grasp","remove screw from valve"):
#             object_id = args[0][1]
#             asm_type = dict(states[0][1])[object_id]
#             if asm_type == 'valve_screw':
#                 g.add((states[0],"grasp and remove screw from valve",(object_id,)))
#         if tasks == ("insert screw in valve","release"):
#             num_rotations = 0
#             rotation_level = 4 - num_rotations # 4 = initial inserted, unscrewed
#             g.add((states[0],"insert and screw valve",(rotation_level,)))
#         if tasks == ("grasp","remove screw from valve"):
#             object_id = args[0][1]
#             asm_type = dict(states[0][1])[object_id]
#             if asm_type == 'valve_screw':
#                 g.add((states[0],"grasp and remove screw from valve",(object_id,)))
#     if len(v)==3:
#         if tasks == ("grasp","move grasped object","release"):
#             arm_name, object_id = args[0]
#             arm_0 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             arm_name, _, _, dt = args[1]
#             arm_1 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             arm_name, = args[2]
#             arm_2 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             asm_type = dict(states[0][1])[object_id]
#             if (arm_0==arm_1) and (arm_1==arm_2) and (asm_type=="DockDrawer"):
#                 distance = sum([x**2 for (x,) in dt])**0.5
#                 if distance > 1:
#                     g.add((states[0],"open dock drawer",(object_id, states[2])))
#                 else:
#                     g.add((states[0],"close dock drawer",(object_id,)))
#         if tasks in [("grasp","close ball","release"),("grasp","open ball","release")]:
#             arm_name, object_id = args[0]
#             arm_0 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             arm_name, = args[2]
#             arm_2 = ["LeftHand", "RightHand", "AnyHand"].index(arm_name)
#             asm_type = dict(states[0][1])[object_id]
#             if (arm_0==arm_2) and (asm_type=="ball_swivel"):
#                 g.add((states[0],tasks[1],()))
#         if tasks == ("insert screw in valve","screw valve","release"):
#             num_rotations = args[1][1]
#             rotation_level = 4 - num_rotations # 4 = initial inserted, unscrewed
#             g.add((states[0],"insert and screw valve",(rotation_level,)))
#         if tasks == ("grasp","screw valve","release"):
#             arm_0, arm_1, arm_2 = args[0][0], args[1][0], args[2][0]
#             arm_0 = 0 if arm_0 in ["Left", "AnyHand"] else 1
#             arm_1 = 0 if arm_1 in ["Left", "AnyHand"] else 1
#             arm_2 = 0 if arm_2 in ["Left", "AnyHand"] else 1
#             if arm_0 == arm_1 and arm_1 == arm_2:
#                 screw_id = args[0][1]
#                 num_rotations = args[1][1]
#                 rotation_level = 4 - num_rotations # 4 = initial inserted, unscrewed
#                 g.add((states[0],"grasp and screw valve",(screw_id, rotation_level,)))
#     return g

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
        if tasks == ("grasp","release"):
            hand, name = args[0]
            dest = args[1][1:]
            g.add((state_tuples[0], "move", (hand, name)+dest))
    if len(v) == 3:
        if tasks == ("trigger","discard_screw","trigger"):
            hand, name = args[1]
            g.add((state_tuples[0], "retire_screw", (name,)))
    return g


def htn_methods():
    # Stub, without this only copct part of ceril will work
    return dict(locals())

def htn_operators():
    # Stub, without this only copct part of ceril will work
    return dict(locals())

if __name__ == "__main__":
    
    import copct as co
    import parse_demo as pd

    # load demo
    states, actions = pd.parse_demo("../demos/hanoi_5disk")
    tasks, args = zip(*[(a["name"], a["args"]) for a in actions])
    states = [s.tuplify() for s in states]
    w = tuple(zip(states, tasks, args))
    # print(states)
    print(tasks)
    print(args)
    # compute explanations
    status, tlcovs, g = co.explain(causes, w, M=M_causes, verbose=True)
    # Prune by minimum cardinality
    tlcovs_ml, ml = co.minCardinalityTLCovers(tlcovs)
    # Print results
    print("Observed")
    tasks = list(zip(*w))[1]
    print("len %d: %s" % (len(tasks), tasks))
    print("Top-level covers:")
    for (u,_,_,_,_) in tlcovs_ml:
        states, tasks, args = zip(*u)
        print("len %d: %s" % (len(tasks), tasks))
    print("Ratio: %d / %d" % (ml,len(w)))

