import numpy as np
import plotly.graph_objects as go

def normalize(v):
    return v / np.linalg.norm(v)

def cross_product(v1, v2):
    return np.cross(v1, v2)

def rotation_matrix(axis, theta):
    axis = normalize(axis)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    cross_prod_matrix = np.array([[0, -axis[2], axis[1]],
                                   [axis[2], 0, -axis[0]],
                                   [-axis[1], axis[0], 0]])
    rotation_mat = cos_theta * np.eye(3) + sin_theta * cross_prod_matrix + (1 - cos_theta) * np.outer(axis, axis)
    return rotation_mat

def find_atom_D_fixed(A, B, C, bond_length, bond_angle, torsion_angle):
    p = B - A
    q = C - B
    
    if np.allclose(cross_product(p, q), 0):
        n = np.array([0, 1, 0])
    else:
        n = normalize(cross_product(p, q))
        
    u = normalize(q)
    v = bond_length * u
    
    bond_angle_rad = np.pi - bond_angle
    rotation_matrix_1 = rotation_matrix(n, bond_angle_rad)
    v_rotated_1 = np.dot(rotation_matrix_1, v)
    
    torsion_angle_rad = torsion_angle
    rotation_matrix_2 = rotation_matrix(u, torsion_angle_rad)
    v_rotated_2 = np.dot(rotation_matrix_2, v_rotated_1)
    
    D = C + v_rotated_2
    return D

def load_inputs_from_file(filename):
    with open(filename, 'r') as file:
        data = file.readlines()
    
    inputs = {}
    for line in data:
        key, value = line.strip().split(': ')
        if key in ['A', 'B', 'C']:
            inputs[key] = np.array([float(x) for x in value.split()])
        else:
            inputs[key] = float(value)
    
    return inputs['A'], inputs['B'], inputs['C'], inputs['bond_length'], np.radians(inputs['bond_angle']), np.radians(inputs['torsion_angle'])

def calculate_atom_D(filename):
    A, B, C, bond_length, bond_angle, torsion_angle = load_inputs_from_file(filename)
    D = find_atom_D_fixed(A, B, C, bond_length, bond_angle, torsion_angle)

    output_filename = "output.txt"
    with open(output_filename, 'w') as f:
        f.write("The coordinates of atom D: {:.6f}, {:.6f}, {:.6f}\n".format(*D))
    
    return A, B, C, D

def plot_ball_and_stick(A, B, C, D):
    atom_colors = ['black', 'black', 'black', 'blue']
    atom_names = ['Atom A', 'Atom B', 'Atom C', 'Atom D']
    atom_size = 20
    bond_width = 10

    fig = go.Figure()

    for i, (r, name, color) in enumerate(zip([A, B, C, D], atom_names, atom_colors)):
        fig.add_trace(go.Scatter3d(
            x=[r[0]], y=[r[1]], z=[r[2]],
            mode='markers',
            marker=dict(size=atom_size, color=color),
            name=name,
            showlegend=True
        ))

    fig.add_trace(go.Scatter3d(
        x=[A[0], B[0], None, B[0], C[0], None, C[0], D[0]],
        y=[A[1], B[1], None, B[1], C[1], None, C[1], D[1]],
        z=[A[2], B[2], None, B[2], C[2], None, C[2], D[2]],
        mode='lines',
        line=dict(color='grey', width=bond_width),
        name='Bond',
        showlegend=True
    ))

    margin_factor = 0.5
    x_vals = [A[0], B[0], C[0], D[0]]
    y_vals = [A[1], B[1], C[1], D[1]]
    z_vals = [A[2], B[2], C[2], D[2]]

    x_range = [min(x_vals) - margin_factor, max(x_vals) + margin_factor]
    y_range = [min(y_vals) - margin_factor, max(y_vals) + margin_factor]
    z_range = [min(z_vals) - margin_factor, max(z_vals) + margin_factor]

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=x_range),
            yaxis=dict(range=y_range),
            zaxis=dict(range=z_range),
            aspectmode='cube'
        ),
        title='Ball and Stick Model',
        showlegend=True
    )
    
    fig.show()

if __name__ == "__main__":
    filename = "input_data.txt"
    A, B, C, D = calculate_atom_D(filename)
    plot_ball_and_stick(A, B, C, D)
