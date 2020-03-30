import numpy as np
import torch as tr

class Kinematics(object):
    """
    Models simple kinematic chains with DH parameters
    Uses pytorch for gradients for IK
    https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters
    """
    def __init__(self, d, r, a):
        # (d)elta, r, (a)lpha (lists)
        self.d = d
        # DH X matrix
        zero, one, cos, sin = tr.zeros(a.shape), tr.ones(a.shape), tr.cos(a), tr.sin(a)
        self.X = tr.stack([
            tr.stack([one,  zero,  zero, r   ]),
            tr.stack([zero, cos,  -sin,  zero]),
            tr.stack([zero, sin,   cos,  zero]),
            tr.stack([zero, zero,  zero, one ]),
        ]).permute(2,0,1)
    def forward(self, t):
        # (t)heta: list of joint angles
        # DH Z matrix
        zero, one, cos, sin = tr.zeros(t.shape), tr.ones(t.shape), tr.cos(t), tr.sin(t)
        Z = tr.stack([
            tr.stack([cos,  -sin,  zero, zero]),
            tr.stack([sin,   cos,  zero, zero]),
            tr.stack([zero,  zero, one,  d   ]),
            tr.stack([zero,  zero, zero, one ]),
        ]).permute(2,0,1)
        # Compose transforms
        ZX = tr.matmul(Z, self.X)
        T = [tr.eye(4)]
        for j in range(len(self.d)): T.append( T[j].mm(ZX[j]) )
        return tr.stack(T)

if __name__ == "__main__":
    
    # ur10 kinematics
    # http://rsewiki.elektro.dtu.dk/index.php/UR10
    d = tr.tensor([.1273, .0, .0, .163941, .1157, .0922])
    r = tr.tensor([.0, -.612, -.5723, .0, .0, .0])
    a = tr.tensor([np.pi/2, 0, 0, np.pi/2, -np.pi/2, 0])
    t0 = tr.tensor([.0, -np.pi/2, .0, -np.pi/2, .0, .0])
    ur10 = Kinematics(d, r, a)

    target = np.eye(4)
    target[:3,3] = [.5, -.5, .5]
    target = tr.tensor(target).float()
    t = t0.clone().detach().requires_grad_(True)

    import matplotlib.pyplot as pt
    from mpl_toolkits.mplot3d import Axes3D
    ax = pt.figure().add_subplot(111, projection='3d')
    pt.ion()

    for n in range(100):

        # t = (t0 + n/100.).clone().detach().requires_grad_(True)
        T = ur10.forward(t)
        # tr.sum((T[-1,:,:] - target)**2).backward()
        tr.sum((T[-1,:3,3:] - target[:3,3:])**2).backward()
        print(t.grad)
        t.data -= 0.1*t.grad
        t.grad *= 0

        V = T.detach().numpy()[:, :3, 3].T
        V_targ = target.detach().numpy()[:3, 3:]
        ax.clear()
        ax.plot(*V_targ, marker='o', color='r')
        ax.plot(*V, marker='o')
        ax.set_xlim([-2, 2])
        ax.set_ylim([-2, 2])
        ax.set_zlim([-2, 2])
        pt.show()
        pt.pause(0.01)
        # break

    input('.')
