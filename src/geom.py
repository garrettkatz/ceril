import numpy as np

def plane_rotation(ang, i, j, d):
    """
    D-dimensional transformation matrix for rotation within a given axis-aligned plane.
      ang : The angle of rotation, in radians
      i, j : The two axis indices specifying the plane of rotation
      d : the dimension of the matrix
    """
    R = np.eye(d)
    R[[i, i, j, j], [i, j, i, j]] = [np.cos(ang), -np.sin(ang), np.sin(ang), np.cos(ang)]
    return R    

def smile_rotation(rotation, d=3):
    """
    Transformation matrix for rotation 3-tuples in SMILE
    can pass d=4 for homogenous coordinates
    """
    Rx = plane_rotation(rotation[0]*np.pi/180,1,2,d);
    Ry = plane_rotation(rotation[1]*np.pi/180,2,0,d);
    Rz = plane_rotation(rotation[2]*np.pi/180,0,1,d);
    R = Rz.dot(Ry).dot(Rx)
    return R
    

if __name__ == "__main__":

    # R = plane_rotation(np.pi/2, 0, 1, 2)
    R = smile_rotation((np.pi/2, 0, 0))
    print(R)
    print(R.dot(np.array([[1,0]]).T))

