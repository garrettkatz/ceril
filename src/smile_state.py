import assembly as asm
import matplotlib.pyplot as pt
from mpl_toolkits.mplot3d import Axes3D

class SmileState(object):

    def __init__(self):

        tabletop = asm.Assembly(name="tabletop", position=(0,0,-1), bbox=(20,12,2))

        self.things = {"tabletop": tabletop}
        self.gripping = {"LeftHand": "nothing", "RightHand": "nothing"}
        self.controls = {}
        self.__name__ = "" # for pyhop compatibility
    
    def tree_string(self):
        s = "%s in left, %s in right" % (self.gripping["LeftHand"], self.gripping["RightHand"])
        for name, thing in self.things.items():
            s += "\n%s at %s" % (thing, thing.position)
        # for name, control_state in self.controls.items():
        #     s += "\n%s state is %s" % (name, control_state)
        s += "\n" + str(self.controls)
        return s
    
    def tuplify(self):
        # Unique hashable state representation (tuples of tuples)
        hands = ["LeftHand", "RightHand"]
        things = sorted(self.things.keys())
        controls = sorted(self.controls.keys())
        return tuple(
            tuple((k,d[k]) for k in sorted(d.keys()))
            for d in [self.gripping, self.things, self.controls])

    def render(self, ax, **kwargs):
        # draw on a matplotlib axis
        for name, thing in self.things.items():
            thing.render(ax, **kwargs)
            ax.text(*(thing.position + (name,)))

def from_tuple(tup):
    state = SmileState()
    state.gripping = {k:v for (k,v) in tup[0]}
    state.things = {k:v for (k,v) in tup[1]}
    state.controls = {k:v for (k,v) in tup[2]}
    return state

def from_smile_txt(fname):

    # Initialize state and file lines
    state = SmileState()
    with open(fname,"r") as f:
        lines = [line.strip().split(",") for line in f.readlines()]

    # First pass: create objects
    for line in lines:
        if line[1] != "create": continue
        assembly = asm.from_smile_txt(line)
        state.things[assembly.name] = assembly
        # name, object_type = line[2], line[4]
        # state.things[name] = asm.Assembly(object_type, [], name)

    # Next pass: initialize controls
    for line in lines:
        if line[1] != "initializeControl": continue
        name, control_state = line[2], line[5]
        state.controls[name] = control_state

    # Next pass: position objects
    for line in lines:
        if line[1] != "move": continue
        name = line[2]
        state.things[name].position = tuple(map(float, line[3:6]))
        state.things[name].rotation = tuple(map(float, line[6:9]))

    return state


if __name__ == "__main__":

    # print(SmileState())
    state = from_smile_txt("../demos/test/0.txt")
    print(state.tree_string())
    print(state.tuplify())
    s = set([state.tuplify()])
    print(from_tuple(state.tuplify()).tree_string())

    ax = pt.figure().add_subplot(111, projection='3d')
    state.render(ax)
    pt.show()

