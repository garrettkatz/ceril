import glob as gb
import smile_state as ss

def parse_demo(demo_path):
    
    
    states = [ss.load_from_smile_txt(demo_path + "/0.txt")]
    actions = []

    fnames = gb.glob(demo_path + "/*.txt")
    for n in range(1,len(fnames)):
        with open("%s/%d.txt" % (demo_path, n), "r") as f:
            lines = [line.strip().split(",") for line in f.readlines()]

        print(lines[0])
        action = {"name": lines[0][1], "args": lines[0][2:]}
        actions.append(action)

        new_state = states[-1].copy()

        if action["name"] == "grasp":

            hand, thing = action["args"]
            new_state.gripping[hand] = thing
            new_state.support[thing] = hand

        if action["name"] == "release":

            hand, = action["args"]
            thing = new_state.gripping[hand]
            new_state.gripping[hand] = "nothing"
            new_state.support[thing] = "nothing"

        states.append(new_state)
        
    # print(fnames)
    # print(initial_state.tree_string())
    
    return states, actions

if __name__ == "__main__":
    states, actions = parse_demo("demos/test")
    print(states[0].tree_string())
    for t in range(len(actions)):
        print(actions[t])
        print(states[t].tree_string())
