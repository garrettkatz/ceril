M_causes = 3
def causes(v):
    """
    Causal relation for the robotic imitation learning domain.
    v is a sequence of intentions or actions.
    Each element v[i] is of the form (state, task name, parameter values).
    Returns the set of all possible causes of v.
    """
    g = set() # set of possible causes
    arm_ids = ("left","right")
    clear_ids = ("discard-bin")
    states, tasks, args = zip(*v)
    if len(v) == 1:
        if tasks == ("move arm and grasp",):
            arm, object_id = args[0]
            dest_id = arm_ids[int(arm)-1]
            asm_type = dict(states[0])[object_id]
            if asm_type not in ("DockCase","DockDrawer"):
                g.add((states[0], "move unobstructed object",(object_id, dest_id, (), ())))
        if tasks == ("put down grasped object",):
            arm, dest_id, dM, dt = args[0]
            object_id = dict(states[0])["gripping"][int(arm)-1]
            g.add((states[0], "move unobstructed object", (object_id, dest_id, dM, dt)))
        if tasks == ("move unobstructed object",):
            object_id, dest_id, dM, dt = args[0]
            if dest_id in arm_ids:
                g.add((states[0], "move object", args[0]))
            else:
                asm_type = dict(states[0])[dest_id]
                if (asm_type=="DockCase") or (dest_id in clear_ids):
                    g.add((states[0],"move unobstructed object to free spot", (object_id, dest_id)))
                g.add((states[0],"move object", args[0]))
        if tasks == ("move object",):
            object_id, dest_id, dM, dt = args[0]
            if dest_id not in arm_ids:
                if (dest_id=="dock-case_6") or (dest_id in clear_ids):
                    g.add((states[0],"move object to free spot", (object_id, dest_id)))
        if tasks == ("move object to free spot",):
            object_id, dest_id = args[0]
            if dest_id=="discard-bin":
                g.add((states[0],"discard object",(object_id,)))
    if len(v)==2:
        if tasks == ("move grasped object","release"):
            arm, dest_id, dM, dt = args[0]
            object_id = dict(states[0])["gripping"][int(arm)-1]
            asm_type = dict(states[0])[object_id]
            if asm_type not in ("DockCase","DockDrawer"):
                g.add((states[0], "put down grasped object", args[0]))
        if tasks == ("move arm and grasp","put down grasped object"):
            arm_0, object_id = args[0]
            arm_1, dest_id, dM, dt = args[1]
            asm_type = dict(states[0])[object_id]
            if (arm_0==arm_1) and not (asm_type=="DockDrawer"):
                g.add((states[0],"move unobstructed object",(object_id, dest_id, dM, dt)))
        if tasks == ("screw valve","screw valve"):
            arms, rotations = zip(*args)
            if arms[0]==arms[1]:
                g.add((states[0],"screw valve",(arms[0],sum(rotations))))
        if tasks == ("screw valve","remove screw from valve"):
            g.add((states[0],"remove screw from valve",()))
        if tasks == ("move arm and grasp","remove screw from valve"):
            object_id = args[0][1]
            asm_type = dict(states[0])[object_id]
            if asm_type == 'valve_screw':
                g.add((states[0],"grasp and remove screw from valve",(object_id,)))
        if tasks == ("insert screw in valve","release"):
            num_rotations = 0
            rotation_level = 4 - num_rotations # 4 = initial inserted, unscrewed
            g.add((states[0],"insert and screw valve",(rotation_level,)))
        if tasks == ("move arm and grasp","remove screw from valve"):
            object_id = args[0][1]
            asm_type = dict(states[0])[object_id]
            if asm_type == 'valve_screw':
                g.add((states[0],"grasp and remove screw from valve",(object_id,)))
    if len(v)==3:
        if tasks == ("move arm and grasp","move grasped object","release"):
            arm_0, object_id = args[0]
            arm_1, _, _, dt = args[1]
            arm_2, = args[2]
            asm_type = dict(states[0])[object_id]
            if (arm_0==arm_1) and (arm_1==arm_2) and (asm_type=="DockDrawer"):
                distance = sum([x**2 for (x,) in dt])**0.5
                if distance > 1:
                    g.add((states[0],"open dock drawer",(object_id, states[2])))
                else:
                    g.add((states[0],"close dock drawer",(object_id,)))
        if tasks in [("move arm and grasp","close ball","release"),("move arm and grasp","open ball","release")]:
            arm_0, object_id = args[0]
            arm_2, = args[2]
            asm_type = dict(states[0])[object_id]
            if (arm_0==arm_2) and (asm_type=="ball_swivel"):
                g.add((states[0],tasks[1],()))
        if tasks == ("insert screw in valve","screw valve","release"):
            num_rotations = args[1][1]
            rotation_level = 4 - num_rotations # 4 = initial inserted, unscrewed
            g.add((states[0],"insert and screw valve",(rotation_level,)))
        if tasks == ("move arm and grasp","screw valve","release"):
            arm_0, arm_1, arm_2 = args[0][0], args[1][0], args[2][0]
            if arm_0 == arm_1 and arm_1 == arm_2:
                screw_id = args[0][1]
                num_rotations = args[1][1]
                rotation_level = 4 - num_rotations # 4 = initial inserted, unscrewed
                g.add((states[0],"grasp and screw valve",(screw_id, rotation_level,)))
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
    from baxter_corpus.demo_replace_red_with_spare_1 import demo as w    
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

