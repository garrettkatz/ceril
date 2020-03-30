import parse_demo as pd
import copct as co
import planning as pl

def imitate(domain, demopath, state0, smile_scaling=1, verbose=0):
    
    # Load demonstration
    demo_states, actions = pd.parse_demo(demopath, scale=smile_scaling)
    demo_ops, demo_args = zip(*[(a["name"], a["args"]) for a in actions])
    demo_states = [s.tuplify() for s in demo_states]

    # Infer tasks with copct
    w = tuple(zip(demo_states, demo_ops, demo_args))
    status, tlcovs, g = co.explain(domain.causes, w, domain.M_causes, verbose=verbose>0)
    tlcovs_ml, ml = co.minCardinalityTLCovers(tlcovs)
    _, ops, args = zip(*tlcovs_ml[0][0]) # arbitrarily use first ML-cover
        
    # Plan tasks with pyhop
    tasks = [(o,) + a for (o, a) in zip(ops, args)]
    actions = pl.plan(domain, state0, tasks, verbose=verbose)

    # Execute plan
    success, states = pl.execute(state0, domain.htn_operators(), actions)
    
    return success, states, actions
    
if __name__ == "__main__":

    import panel_domain as domain
    import tiger_state as ts
    import smile_state as st
    import numpy as np
    import matplotlib.pyplot as pt

    # Run CERIL
    tiger = ts.TigerState()
    tiger.base_x, tiger.base_y, tiger.base_a = 0, -3, np.pi/2
    smile_scaling = .1
    demopath = "../demos/test/"
    state0 = pl.State(tiger, st.from_smile_txt(demopath + "0.txt", scale=smile_scaling))
    success, states, actions = imitate(domain, demopath, state0, smile_scaling=1, verbose=3)

    # Visualize execution    
    pt.ion()
    fig = pt.figure(figsize=(10,10))
    ax = fig.add_subplot(111, projection='3d')
    pt.show()
    for s, state in enumerate(states):
        print(actions[s])
        print(state.tree_string())
        ax.clear()
        state.render(ax)
        ax.set_xlim([-2.5, 2.5])
        ax.set_ylim([-2.5, 2.5])
        ax.set_zlim([-.5, 2.5])
        input('.')
        # pt.pause(1)
