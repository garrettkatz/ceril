import numpy as np

class TigerState(object):
    def __init__(self):
        self.base_position = np.eye(4)
        self.base_position[2,3] = 1
        self.arm_joints = np.zeros(7)
    def __str__(self):
        return "TigerState at base=%s, joints=%s" % (
            tuple(self.base_position[:3,3]), tuple(self.arm_joints))
    def render(self, ax, **kwargs):
        # draw on a matplotlib axis
        # for name, thing in self.things.items():
        #     thing.render(ax, **kwargs)
        #     ax.text(*(thing.position + (name,)))

        # default kwargs
        _kwargs = {"marker":"o", "color":"black", "linestyle":"-"}
        _kwargs.update(kwargs)

        # Cube vertices and edge indices
        V = (np.arange(2**3)[np.newaxis,:]/2**np.arange(3)[:,np.newaxis] % 2).astype(int)
        E = list(zip(*np.nonzero(np.triu(
            V[:,np.newaxis,:] == V[:,:,np.newaxis]).sum(axis=0) == 2)))
        V = V.astype(float)
        V -= V.mean(axis=1)[:,np.newaxis]


        # Rotation and translation of base
        R, t = self.base_position[:3,:3], self.base_position[:3,3:]
        
        # Base and wheel bboxes
        base_bbox = np.array([[3, 4, .5]]).T
        wheel_bbox = np.array([[.5, 1, 1]]).T

        # Base and wheel offsets
        offsets = [[0, 0], [1.5, 2], [-1.5, 2], [1.5, -2], [-1.5, -2]]
        
        # Render base and wheels
        for (bbox, offset) in zip([base_bbox] + 4*[wheel_bbox], offsets):
            _V = R.dot(V*bbox + np.array([offset + [0]]).T) + t
            for e in E: ax.plot(*_V[:,e], **_kwargs)

        ax.text(*(tuple(t.flatten()) + ("tiger",)))

        # Plot arm links
        arm_lengths = np.ones(len(self.arm_joints)).cumsum()[np.newaxis,:]
        arm_links = np.concatenate((np.zeros((2,len(self.arm_joints))), arm_lengths), axis=0)
        ax.plot(*arm_links, **_kwargs)

    def plan_motion(self, target):
        pass

if __name__ == "__main__":

    import matplotlib.pyplot as pt
    from mpl_toolkits.mplot3d import Axes3D

    state = TigerState()
    print(state)
    ax = pt.figure().add_subplot(111, projection='3d')
    state.render(ax)
    pt.show()

