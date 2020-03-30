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
    def forward(self, t, T0=None):
        # (t)heta: list of joint angles
        # T0: initial 4x4 transformation matrix of chain root (defaults to identity)
        # DH Z matrix
        if T0 is None: T0 = tr.eye(4)
        zero, one, cos, sin = tr.zeros(t.shape), tr.ones(t.shape), tr.cos(t), tr.sin(t)
        Z = tr.stack([
            tr.stack([cos,  -sin,  zero, zero  ]),
            tr.stack([sin,   cos,  zero, zero  ]),
            tr.stack([zero,  zero, one,  self.d]),
            tr.stack([zero,  zero, zero, one   ]),
        ]).permute(2,0,1)
        # Compose transforms
        ZX = tr.matmul(Z, self.X)
        T = [T0]
        for j in range(len(self.d)): T.append( T[j].mm(ZX[j]) )
        return tr.stack(T)
        
if __name__ == "__main__":
    
    import ur10
    d = tr.tensor(ur10.d)
    r = tr.tensor(ur10.r)
    a = tr.tensor(ur10.a)
    t0 = tr.tensor(ur10.t0)
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
