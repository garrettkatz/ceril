import copy as cp
import glob as gb
import smile_state as st

def parse_demo(demo_path, scale=1):
    
    # Initialize first state and empty action list    
    states = [st.from_smile_txt(demo_path + "/0.txt", scale)]
    actions = []

    # Enumerate all demo files and process in order
    fnames = gb.glob(demo_path + "/*.txt")
    for n in range(1,len(fnames)):
        with open("%s/%d.txt" % (demo_path, n), "r") as f:
            lines = [line.strip().split(",") for line in f.readlines()]

        # Initialize current action and new state
        action = {"name": lines[0][1], "args": tuple(lines[0][2:])}
        new_state = cp.deepcopy(states[-1])

        # Update control states for all controls
        for line in lines[1:]:
            if line[1] != "changeControlState": continue
            name, control_state = line[2:4]
            new_state.controls[name] = control_state

        # Update pose information for all objects in new state (remaining move lines of demo file)
        for line in lines[1:]:
            if line[1] != "move": continue
            name = line[2]
            new_state.things[name].position = tuple(map(lambda x: scale*float(x), line[3:6]))
            new_state.things[name].rotation = tuple(map(float, line[6:9]))

        # Update grippers and object positions
        if action["name"] == "grasp":
            hand, name = action["args"]
            new_state.gripping[hand] = name
        if action["name"] == "release":
            hand, = action["args"]
            name = new_state.gripping[hand]
            new_state.gripping[hand] = "nothing"
            thing = new_state.things[name]
            action["args"] += (
                tuple(map(lambda x: scale*float(x), thing.position)),
                tuple(map(float, thing.rotation)))

        actions.append(action)
        states.append(new_state)
        
    # print(fnames)
    # print(initial_state.tree_string())
    
    return states, actions

if __name__ == "__main__":

    import matplotlib.pyplot as pt

    smile_scaling = .1 # used to globally rescale distance units in SMILE if needed
    states, actions = parse_demo("../demos/panel", scale=smile_scaling)

    # Prints all the states and actions in the demo
    print(states[0].tree_string())
    for t in range(len(actions)):
        print("Action: ", actions[t])
        print(states[t+1].tree_string())

    fig = pt.figure(figsize=(10,5))
    for sp, i in enumerate([0, -1]):
        ax = fig.add_subplot(1, 2, sp+1, projection='3d')
        states[i].render(ax)
        ax.set_xlim([-2.5, 2.5])
        ax.set_ylim([-2.5, 2.5])
        ax.set_zlim([-.5, 2.5])
    pt.show()
    
