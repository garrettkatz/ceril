import copy as cp
import pyhop as ph

def execute(state, operators, actions):
    """
    Execute sequence of actions starting from state
        operators: returned from pd.htn_operators()
        actions: [..., (name, arg1, arg2, ...), ...]
    returns
        success: boolean success flag
        states: list of states after each action is performed (up to failure)
    """
    success = True
    states = []
    for action in actions:
        name, args = action[0], action[1:]
        state = operators[name](cp.deepcopy(state), *args)
        if state == False:
            success = False
            break
        states.append(state)
    return success, states

if __name__ == "__main__":

    import smile_state as st
    import panel_domain as pd
    import matplotlib.pyplot as pt
    from mpl_toolkits.mplot3d import Axes3D

    ops = pd.htn_operators()
    methods = pd.htn_methods()

    ph.declare_operators(*ops.values())
    for name, fun in methods.items(): ph.declare_methods(name, fun) # one method per task name

    # state0 = st.SmileState()
    state0 = st.from_smile_txt("../demos/test/0.txt")

    # tasks = [
    #     ("trigger", "LeftHand", "toggle"),
    #     # ("loosen", "LeftHand", "", "", "", "tabletop"),
    #     ("grasp", "LeftHand", "tabletop"),
    #     ("release", "LeftHand", (10.,0.,0.), (0.,0.,0.)),
    # ]
    # tasks = [("unscrew", "LeftHand", "panelscrew"),]
    # tasks = [("discard_screw", "LeftHand", "panelscrew"),]
    tasks = [("retire_screw", "panelscrew"),]
    
    actions = ph.pyhop(state0, tasks, verbose=2)
    print(actions)

    success, states = execute(state0, ops, actions)
    print("Success: ", success)
    print(state0.tree_string())

    pt.ion()
    ax = pt.figure().add_subplot(111, projection='3d')
    pt.show()
    for s, state in enumerate(states):
        print(actions[s])
        print(state.tree_string())
        ax.clear()
        state.render(ax)
        pt.pause(1)

    if not success: print(actions[len(states)])
