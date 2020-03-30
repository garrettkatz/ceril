import numpy as np
import geom as gm

class Assembly(object):
    def __init__(self,category="",sub_assemblies=[],name="",position=(0,0,0),rotation=(0,0,0),bbox=(1,1,1)):

        self.category = category
        self.sub_assemblies = tuple(sub_assemblies)
        self.name = name
        self.position = position
        self.rotation = rotation
        self.bbox = bbox
        self.grasp = gm.plane_rotation(np.pi, 1, 2, 4)
    
    def __str__(self):
        s = "Assembly<%s>" % self.category
        if self.name != "": s += " " + self.name
        return s

    def render(self, ax, **kwargs):
        """ render wireframe on  a matplotlib axis3d """
        
        # default kwargs
        # _kwargs = {"marker":"o", "color":"black", "linestyle":"-"}
        _kwargs = {"color":"black", "linestyle":"-"}
        _kwargs.update(kwargs)

        # Cube vertices and edge indices
        V = (np.arange(2**3)[np.newaxis,:]/2**np.arange(3)[:,np.newaxis] % 2).astype(int)
        E = list(zip(*np.nonzero(np.triu(
            V[:,np.newaxis,:] == V[:,:,np.newaxis]).sum(axis=0) == 2)))

        # Transform to origin-centered bbox
        V = V.astype(float)*np.array([self.bbox]).T
        V -= V.mean(axis=1)[:,np.newaxis]

        # Rotation and translation
        R = gm.smile_rotation(self.rotation)
        t = np.array([self.position]).T
        
        # Transform and plot edges
        V = R.dot(V) + t
        for e in E: ax.plot(*V[:,e], **_kwargs)

        # Transform and plot grasp
        V = R.dot(self.grasp[:3,:]) + t
        E = [(i,3) for i in range(3)]
        for e in E: ax.plot(*V[:,e], linestyle='-', color='r')

def from_smile_txt(line_tokens, scale=1):
    """ line_tokens: a tuple of tokens on a "create" line of a SMILE demo txt file """
    kwargs = {"name": line_tokens[2]}
    def lookup(key): return line_tokens[line_tokens.index(key)+1]
    if "category" in line_tokens: kwargs["category"] = lookup("category")
    if "bboxx" in line_tokens:
        kwargs["bbox"] = tuple(scale*float(lookup("bbox"+k)) for k in "xyz")
    return Assembly(**kwargs)

if __name__ == "__main__":
    
    blk = Assembly("custom", [], name="garrett", rotation=(10,10,10))
    print(blk)

    import matplotlib.pyplot as pt
    from mpl_toolkits.mplot3d import Axes3D
    ax = pt.figure().add_subplot(111, projection='3d')
    blk.render(ax)
    pt.show()

