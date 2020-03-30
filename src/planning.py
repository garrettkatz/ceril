import copy as cp
import pyhop as ph

class State(object):
    def __init__(self, robot_state, smile_state):
        self.robot = robot_state
        self.smile = smile_state
        self.__name__ = "" # for pyhop compatibility
    def tree_string(self):
        return self.smile.tree_string()
    def render(self, ax, **kwargs):
        self.robot.render(ax, **kwargs)
        self.smile.render(ax, **kwargs)

def plan(domain, state0, tasks, verbose=0):

    # Register planning operations with pyhop
    ops = domain.htn_operators()
    methods = domain.htn_methods()
    ph.declare_operators(*ops.values())
    for name, fun in methods.items(): ph.declare_methods(name, fun) # one method per task name
    
    # Run pyhop planner
    actions = ph.pyhop(state0, tasks, verbose=verbose)
    return actions

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
    import tiger_state as ts
    import panel_domain as domain
    import matplotlib.pyplot as pt
    from mpl_toolkits.mplot3d import Axes3D

    tiger = ts.TigerState()
    tiger.base_x, tiger.base_y = 0, -3
    smile_scaling = .1
    state0 = State(tiger, st.from_smile_txt("../demos/test/0.txt", scale=smile_scaling))
    tasks = [("retire_screw", "panelscrew"),]
    
    actions = plan(domain, state0, tasks, verbose=2)
    print(actions)

    success, states = execute(state0, domain.htn_operators(), actions)
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
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        ax.set_zlim([-5, 5])
        input('.')
        # pt.pause(1)

    if not success: print(actions[len(states)])
