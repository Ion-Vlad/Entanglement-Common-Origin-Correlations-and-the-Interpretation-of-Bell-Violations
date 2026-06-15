import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# ----------------------------
# Figure and axis setup
# ----------------------------
fig, ax = plt.subplots(figsize=(10, 6.5))
plt.subplots_adjust(bottom=0.18)  # More room for two buttons

# Configure axes
ax.set_xlim(-5, 185)
ax.set_ylim(-1.2, 1.2)
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_xlabel("Angle θ (degrees)", fontsize=14)
ax.set_ylabel("Correlation E(θ)", fontsize=14)
ax.set_title("Quantum vs Classical Correlation", fontsize=16, pad=20)

# Reference lines
ax.axhline(0, color='gray', linewidth=1)
ax.axhline(-1, color='gray', linewidth=1, linestyle=':')
ax.axhline(1, color='gray', linewidth=1, linestyle=':')

# Plot objects
# Minimum information: Cyan solid line
trail_line_m, = ax.plot([], [], 'c-', linewidth=3, label="Minimal information")
# Quantum: Blue solid line
trail_line_qm, = ax.plot([], [], 'b-', linewidth=3, label="Quantum (E=-cos θ)")
# Classical: Red dashed line
trail_line_cl, = ax.plot([], [], 'r-', linewidth=3, label="Classical (Linear)")
# Violation Zone: gold
ax.fill_between([], [], [], color="gold", alpha=0.15, label='Violation Zone')
# Marker: red
marker_qm, = ax.plot([], [], 'ro', markersize=12, zorder=5)

ax.legend(loc='upper left')

# ----------------------------
# PRE-CALCULATE STATIC DATA
# ----------------------------
all_theta = np.arange(0, 181)
cl_vals = np.where(all_theta <= 90, 
                   -1 + (all_theta / 90.0), 
                   (all_theta - 90) / 90.0)

# ----------------------------
# Animation functions
# ----------------------------
def animate_minimal_only(event=None):
    """Animation for Minimal (Cyan) line only"""
    reset_plot()
    trail_x = []
    trail_y_cl = []

    # Clear any existing fill collections for Violation Zone from previous runs
    if len(ax.collections) > 0:
        for coll in ax.collections:
            coll.remove()
            
    for theta in range(181):
        y_cl = cl_vals[theta]
        
        trail_x.append(theta)
        trail_y_cl.append(0)  # horizontal line
        
        # Update Classical Line ONLY
        trail_line_m.set_data(trail_x, trail_y_cl)
        trail_line_cl.set_data([], [])  # Clear classic
        trail_line_qm.set_data([], [])  # Clear quantum
        
        # Clear marker since we're not showing quantum
        marker_qm.set_data([], [])
        
        # Title update
        ax.set_title(
            f"Minimal Model Only\nCurrent Angle: {theta:3d}°\n"
            f"E_M(θ) = {y_cl:.4f}",
            fontsize=14, color='cyan'
        )
        
        plt.draw()
        plt.pause(0.01)
        
def animate_classical_only(event=None):
    """Animation for Classical (Red) line only"""
    reset_plot()
    trail_x = []
    trail_y_cl = []
    
    # Clear any existing fill collections for Violation Zone from previous runs
    if len(ax.collections) > 0:
        for coll in ax.collections:
            coll.remove()
            
    for theta in range(181):
        y_cl = cl_vals[theta]
        
        trail_x.append(theta)
        trail_y_cl.append(y_cl)
        
        # Update Classical Line ONLY
        trail_line_cl.set_data(trail_x, trail_y_cl)
        trail_line_m.set_data([], [])   # Clear minimal
        trail_line_qm.set_data([], [])  # Clear quantum
        
        # Clear marker since we're not showing quantum
        marker_qm.set_data([], [])
        
        # Title update
        ax.set_title(
            f"Classical Model Only\nCurrent Angle: {theta:3d}°\n"
            f"E_CL(θ) = {y_cl:.4f}",
            fontsize=14, color='red'
        )
        
        plt.draw()
        plt.pause(0.01)

def animate_both_lines(event=None):
    """Animation for Both Quantum and Classical lines"""
    reset_plot()
    trail_x = []
    trail_y_qm = []
    trail_y_cl = []

    # Clear any existing fill collections from previous runs
    if len(ax.collections) > 0:
        for coll in ax.collections:
            coll.remove()
    
    for theta in range(181):
        # Calculate Quantum Value
        y_qm = -math.cos(math.radians(theta))
        y_cl = cl_vals[theta]
        
        trail_x.append(theta)
        trail_y_qm.append(y_qm)
        trail_y_cl.append(y_cl)

        # 4. CRITICAL FIX: Convert Python lists to NumPy 1D arrays
        x_arr = np.array(trail_x)
        y_qm_arr = np.array(trail_y_qm)
        y_cl_arr = np.array(trail_y_cl)
        
        
        # Update Both Lines
        trail_line_qm.set_data(trail_x, trail_y_qm)
        trail_line_cl.set_data(trail_x, cl_vals[:theta+1])
        trail_line_m.set_data([], [])   # Clear minimal
        
        # Update Marker (for Quantum)
        marker_qm.set_data([theta], [y_qm])
        
        # Title update
        ax.set_title(
            f"Both Models\nCurrent Angle: {theta:3d}°\n"
            f"E_QM = {y_qm:.4f} | E_CL = {y_cl:.4f}",
            fontsize=14
        )

        #  Remove old fill collection (to prevent memory buildup)
        if len(ax.collections) > 0:
            ax.collections[-1].remove()
        
        #  Fill between curves with correct 1D arrays
        ax.fill_between(x_arr, y_cl_arr, y_qm_arr, color="gold",
                        alpha=0.15, label="Violation Zone")
        
        plt.draw()
        plt.pause(0.01)

def reset_plot():
    """Clear all plots and restore default title"""
    trail_line_m.set_data([], [])
    trail_line_qm.set_data([], [])
    trail_line_cl.set_data([], [])
    marker_qm.set_data([], [])
    
    ax.set_title("Quantum vs Classical Correlation", fontsize=16, pad=20)
    plt.draw()

# ----------------------------
# Button setup
# ----------------------------
# Position: [x0, y0, width, height] in normalized figure coordinates
button_ax_1 = plt.axes([0.73, 0.12, 0.20, 0.05])
button_classical = Button(button_ax_1, "Classical Only (Red)", color='lightcoral')
button_classical.on_clicked(lambda event: (animate_classical_only()))

button_ax_2 = plt.axes([0.73, 0.05, 0.20, 0.05])
button_both = Button(button_ax_2, "Both Lines (QM + CL)", color='lightgreen')
button_both.on_clicked(lambda event: (animate_both_lines()))

# Also add a "Minimal information" button
button_ax_3 = plt.axes([0.57, 0.05, 0.15, 0.05])
button_minimal = Button(button_ax_3, "Minimal information", color='lightcyan')
button_minimal.on_clicked(lambda event: (animate_minimal_only()))

# Initial run - start with both lines
animate_both_lines()

plt.show()
