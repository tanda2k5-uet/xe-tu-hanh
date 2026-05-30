import numpy as np

# turn node position into pixel position (Caro style, center of cell)
def turn2pixel(map, height, width, row_position, col_position): 
    cell_w = width / len(map[0])
    cell_h = height / len(map)
    x_pixel = col_position * cell_w + cell_w / 2
    y_pixel = row_position * cell_h + cell_h / 2
    return [x_pixel, y_pixel]

# turn pixel position to node position (Caro style)
def turn2node(map, width, height, x_pixel, y_pixel): 
    cell_w = width / len(map[0])
    cell_h = height / len(map)
    col = int(x_pixel / cell_w)
    row = int(y_pixel / cell_h)
    
    # Clamp to valid map bounds
    col = max(0, min(len(map[0]) - 1, col))
    row = max(0, min(len(map) - 1, row))
    return (row, col)

def transformationMatrix2d(scale=(1.0, 1.0), rotation_deg=0.0, translation=(0.0, 0.0)):
    """
    Create a 3x3 2D transformation matrix for scaling, rotation, and translation.
    Order of operations: Scale -> Rotate -> Translate.
    
    Parameters:
        scale (tuple): (sx, sy) scaling factors.
        rotation_deg (float): Rotation angle in degrees (counterclockwise).
        translation (tuple): (tx, ty) translation values.
    
    Returns:
        np.ndarray: 3x3 transformation matrix.
    """
    sx, sy = scale
    tx, ty = translation
    theta = np.deg2rad(rotation_deg)

    # Scaling matrix
    S = np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ])

    # Rotation matrix
    R = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0,              0,             1]
    ])

    # Translation matrix
    T = np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1 ]
    ])

    # Combined transformation: T * R * S
    return T @ R @ S


def apply_transformation(points, matrix):
    """
    Apply a 3x3 transformation matrix to a set of 2D points.
    
    Parameters:
        points (np.ndarray): Nx2 array of (x, y) points.
        matrix (np.ndarray): 3x3 transformation matrix.
    
    Returns:
        np.ndarray: Transformed Nx2 points.
    """
    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("Points must be an Nx2 array.")

    # Convert to homogeneous coordinates
    ones = np.ones((points.shape[0], 1))
    homogeneous_points = np.hstack([points, ones])

    # Apply transformation
    transformed = homogeneous_points @ matrix.T

    # Convert back to 2D
    return transformed[:, :2]
