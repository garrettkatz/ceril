import ur10
import numpy as np
import scipy.optimize as so
import torch as tr
import kinematic_chain as kc

class TigerState(object):
    def __init__(self):
        # mobile base
        self.base_bbox = np.array([[1, .75, .125]]).T
        self.wheel_bbox = np.array([[.25, .125, .25]]).T
        self.base_x, self.base_y, self.base_a = 0., 0., 0.
        self.base_z = self.wheel_bbox[2,0]/2

        # ur10 arm
        self.arm_joints = np.array(ur10.t0)
        self.kinematics = kc.Kinematics(tr.tensor(ur10.d), tr.tensor(ur10.r), tr.tensor(ur10.a))

    def __str__(self):
        return "TigerState at base=%s, joints=%s" % (
            (self.base_x, self.base_y, self.base_a), tuple(self.arm_joints))

    def render(self, ax, **kwargs):
        # draw on a matplotlib axis with style kwargs

        # default kwargs
        # _kwargs = {"marker":"o", "color":"black", "linestyle":"-"}
        _kwargs = {"color":"black", "linestyle":"-"}
        _kwargs.update(kwargs)

        # Cube vertices and edge indices
        V = (np.arange(2**3)[np.newaxis,:]/2**np.arange(3)[:,np.newaxis] % 2).astype(int)
        E = list(zip(*np.nonzero(np.triu(
            V[:,np.newaxis,:] == V[:,:,np.newaxis]).sum(axis=0) == 2)))
        V = V.astype(float)
        V -= V.mean(axis=1)[:,np.newaxis]

        # Rotation and translation of base
        R = np.array([
            [np.cos(self.base_a), -np.sin(self.base_a), 0],
            [np.sin(self.base_a),  np.cos(self.base_a), 0],
            [0,                    0,                   1]])
        t = np.array([[self.base_x, self.base_y, self.base_z]]).T
        
        # Base and wheel bboxes
        wheel_offsets = self.base_bbox[:2] * V[:2,:4]

        # Base and wheel offsets
        offsets = np.zeros((3,5))
        offsets[:2,1:] = wheel_offsets
        
        # Render base and wheels
        for i, bbox in enumerate([self.base_bbox] + 4*[self.wheel_bbox]):
            _V = R.dot(V*bbox + offsets[:,[i]]) + t
            for e in E: ax.plot(*_V[:,e], **_kwargs)
        ax.text(*(tuple(t.flatten()) + ("tiger",)))

        # Plot arm links
        T = self.kinematics.forward(tr.tensor(np.array(ur10.t0)+self.arm_joints).float())
        _V = T.detach().numpy()[:, :3, 3].T
        t[2] += self.base_bbox[2]/2
        _V = R.dot(_V) + t
        _kwargs.update({"marker":"o"})
        ax.plot(*_V, **_kwargs)

    def plan_motion(self, world, target, verbose=0):
    
        target = tr.tensor(target).float()

        def fun(s): # objective function
            # s =  [base_x, base_y, base_angle, ...joints...]
            (base_x, base_y, base_a), joints = s[:3], s[3:]
            base_x = tr.tensor(base_x, requires_grad=True)
            base_y = tr.tensor(base_y, requires_grad=True)
            base_a = tr.tensor(base_a, requires_grad=True)
            joints = tr.tensor(joints.astype(np.float32), requires_grad=True)

            zero, one = tr.tensor(0.), tr.tensor(1.)
            base_z = tr.tensor(self.base_z).float()
            B = tr.stack([
                    tr.stack([tr.cos(base_a), -tr.sin(base_a), zero, base_x]),
                    tr.stack([tr.sin(base_a),  tr.cos(base_a), zero, base_y]),
                    tr.stack([zero,            zero,           one,  base_z]),
                    tr.stack([zero,            zero,           zero, one   ]),])
            T = self.kinematics.forward(tr.tensor(ur10.t0).float() + joints)
            BT = tr.mm(B, T[-1,:,:])
            val = tr.sum((BT - target)**2)
            if verbose > 0: print(val.item())
            
            val.backward()
            jac = np.concatenate((
                np.array([base_x.grad.item(), base_y.grad.item(), base_a.grad.item()]),
                joints.grad.detach().numpy()))

            return val.item(), jac

        # # start at current base
        # base_x, base_y, base_a = self.base_x, self.base_y, self.base_a

        # start with base 1 unit behind target
        base_x = target[0,3] - 1*target[0,2]
        base_y = target[1,3] - 1*target[1,2]
        base_a = np.pi/2

        s0 = np.concatenate((
            np.array([base_x, base_y, base_a]),
            self.arm_joints)).astype(np.float32)
        soln = so.minimize(fun, s0, jac=True)
        success = soln.status == 0
        (base_x, base_y, base_a), joints = soln.x[:3], soln.x[3:]
        return (base_x, base_y, base_a), joints, success

if __name__ == "__main__":

    import matplotlib.pyplot as pt
    from mpl_toolkits.mplot3d import Axes3D

    state = TigerState()
    print(state)
    ax = pt.figure(figsize=(10,10)).add_subplot(111, projection='3d')
    state.render(ax)

    target = np.eye(4)
    target[2,3] = 1
    base, joints, success = state.plan_motion(None, target)
    state.base_x, state.base_y, state.base_a = base

    state.arm_joints = joints
    state.render(ax, marker='o', color='g')
    
    x, y, z = float(target[0,3]), float(target[1,3]), float(target[2,3])
    ax.scatter(x, y, z, color='r')
    ax.text(x, y, z, "target")
    ax.set_xlabel("x")
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-.5, 2])
    pt.show()

