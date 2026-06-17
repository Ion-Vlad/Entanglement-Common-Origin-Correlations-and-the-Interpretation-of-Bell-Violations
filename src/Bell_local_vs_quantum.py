import tkinter as tk
import matplotlib.pyplot as plt
from math import cos, pi, sin, acos, asin
from random import random, uniform
from tkinter import filedialog

from reportlab.platypus import (SimpleDocTemplate, Paragraph,
        Spacer, Image,)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Preformatted

trials_per_pair = 100_000

settings_degrees = {
    "A": 0,
    "A'": 90,
    "B": 45,
    "B'": -45,
}

setting_pairs = [
    ("A", "B"),
    ("A", "B'"),
    ("A'", "B"),
    ("A'", "B'"),
]

def export_results():

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate("Appendix_A.pdf")

    story = []

    story.append(Paragraph("<b>Bell Local vs Quantum Simulation</b>",
            styles["Title"],))
    story.append(Spacer(1,12))
    story.append(Paragraph(f"Trials per setting: {trials_per_pair}",
            styles["Normal"],))
    story.append(Spacer(1,12))
    story.append(Preformatted(local_text.get("1.0", "end"),
            styles["Code"],))
    story.append(Spacer(1,12))
    story.append(Preformatted(quantum_text.get("1.0", "end"),
            styles["Code"],))
    story.append(Spacer(1,12))
    
    # add image if needed - MUST be in the same folder
    
    # story.append(Image("correlation_comparison.png",width=420,
    #        height=240,))

    doc.build(story)


def degrees_to_radians(degrees):
    return degrees * pi / 180


def local_spin_result(measurement_angle, hidden_angle):
    """
    A simple local hidden-variable spin model.

    The particle carries a hidden direction. The measurement returns +1
    if the setting lies on the same half-plane as the hidden direction,
    otherwise -1.
    """
    return 1 if cos(measurement_angle - hidden_angle) >= 0 else -1


def local_hidden_spin_trial(alice_angle, bob_angle):
    """
    A local model with shared origin.

    Alice and Bob receive opposite hidden directions. Alice's result depends
    only on Alice's setting and Alice's hidden direction. Bob's result depends
    only on Bob's setting and Bob's hidden direction.
    """
    hidden_angle = uniform(0, 2 * pi)
    alice_hidden_angle = hidden_angle
    bob_hidden_angle = hidden_angle + pi

    return (
        local_spin_result(alice_angle, alice_hidden_angle),
        local_spin_result(bob_angle, bob_hidden_angle),
    )


def quantum_spin_trial(alice_angle, bob_angle):
    """
    Quantum singlet model.

    This directly uses the quantum same/opposite probability:
        E = -cos(θ)
        P(same) = (1 + E) / 2
    """
    expected_correlation = -cos(alice_angle - bob_angle)
    probability_same = (1 + expected_correlation) / 2

    alice_result = 1 if random() < 0.5 else -1
    bob_result = alice_result if random() < probability_same else -alice_result

    return alice_result, bob_result


def calculate_correlation(records):
    return sum(alice * bob for alice, bob in records) / len(records)


def run_model(model_name, trial_function):
    measured = {}
    lines = [model_name, "~" * 66,]

    for alice_setting, bob_setting in setting_pairs:
        alice_angle = degrees_to_radians(settings_degrees[alice_setting])
        bob_angle = degrees_to_radians(settings_degrees[bob_setting])

        records = [
            trial_function(alice_angle, bob_angle)
            for _ in range(trials_per_pair)
        ]
        same = sum(1 for alice, bob in records if alice == bob)
        opposite = len(records) - same
        correlation = calculate_correlation(records)
        measured[(alice_setting, bob_setting)] = correlation

        lines.extend(
            [
                f"Settings {alice_setting}, {bob_setting}:",
                f"  same results     = {same}",
                f"  opposite results = {opposite}",
                f"  measured E       = {correlation:.3f}",
                "",
            ]
        )
    global s    
    s = (
        measured[("A", "B")]
        + measured[("A", "B'")]
        + measured[("A'", "B")]
        - measured[("A'", "B'")]
    )

    lines.extend(
        [
            f"S = {s:.3f}",
            f"|S| = {abs(s):.3f}",
            "",
        ]
    )

    return lines

def comparison_header():
    return "\n".join(
        [
            
            "            Angles:                                                 "
            "      100 000 trials, same angles, two different models. Angles alone "
            "do not create a Bell violation.",
            "  Alice A  = 0 degrees                                            "
            "The violation appears when we use the quantum probability rule: "
            "E = -cos(θ).",
            "  Alice A' = 90 degrees                                         "
            " Values are rounded to 3 decimals. Small deviations near the local "
            "bound represent normal finite-sample fluctuations; ",
            "  Bob   B  = 45 degrees                                         "
            "however, |S| remains consistently below 2.02 for classical cases, "
            "whereas it exceeds 2.8 in the quantum model ",
            "  Bob   B' = -45 degrees                                        "
            "due to angular dependence of the quantum correlation."   
        ]
    )

def run_comparison():
    local_lines = run_model("               Local Hidden Spin Model" + "\n" +
                            "This model uses shared hidden directions and "
                            "local measurements." + "\n" + "It does NOT use the quantum "
                            "probability rule.", local_hidden_spin_trial)
    quantum_lines = run_model("             Quantum Singlet Probability Model" +
                            "\n" + "This model uses the quantum spin-singlet "
                            "probability rule: " + "\n" + "E = -cos(θ).",
                            quantum_spin_trial)

    return "\n".join(local_lines), "\n".join(quantum_lines)

def update_output():
    run_button.config(state=tk.DISABLED, text="Running...")
    root.update_idletasks()

    local_output, quantum_output = run_comparison()

    for widget, text in (
        (local_text, local_output),
        (quantum_text, quantum_output),
    ):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)


        # Define a red and blue text tags for |S|
        widget.tag_configure("red", foreground="red")
        widget.tag_configure("blue", foreground="blue")
        widget.tag_configure("green", foreground="green")

        for line in text.splitlines():   # text colour red / blue for |S|
            if line.startswith("|S| ="):
                # extract |S| from the string and convert it to a number
                if float(line[-5:]) > 2 and float(line[-5:]) < 2.2:
                    widget.insert(tk.END, line, "red")
                    widget.insert(tk.END, " - A finite simulation may introduce "
                                  "random sampling" + "\n" + "noise while increasing the "
                                  "number of trials will slow down the" + "\n" + "script.",
                                  "green")
                else:
                    if float(line[-5:]) > 2.7:
                        widget.insert(tk.END,  line + " - Within the interpretation "
                                      "proposed in this work, " + "\n" + "this reflects "
                                      "the angular dependence of the quantum correlation " +
                                      "\n" + "function E(θ)=−cosθ.", "blue")
                    else:
                        widget.insert(tk.END, line + "\n", "red")
            else:
                widget.insert(tk.END, line + "\n")
                
    widget.config(state=tk.DISABLED)
    run_button.config(state=tk.NORMAL, text="Run again")

root = tk.Tk()
root.title("Bell Angles: Local vs Quantum")
root.geometry("1120x760")

main = tk.Frame(root, padx=16, pady=16)
main.pack(fill=tk.BOTH, expand=True)

# Buttons Frame
btn_frame = tk.Frame(main)
btn_frame.pack(fill=tk.X, pady=(0, 12))

run_button = tk.Button(btn_frame, text="Run again", command=update_output)
run_button.pack(side=tk.LEFT, padx=(0, 10))

export_button = tk.Button(btn_frame, text="Export Results (PDF/PNG)",
                          command=export_results, bg='#e0f0ff')
export_button.pack(side=tk.LEFT)

header_label = tk.Label(main, text=comparison_header(), justify=tk.LEFT, anchor=tk.W)
header_label.pack(fill=tk.X, pady=(0, 12))

panels = tk.Frame(main)
panels.pack(fill=tk.BOTH, expand=True)
panels.columnconfigure(0, weight=1)
panels.columnconfigure(1, weight=1)
panels.rowconfigure(1, weight=1)

local_label = tk.Label(panels, text="Local", anchor=tk.W)
local_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))

quantum_label = tk.Label(panels, text="Quantum", anchor=tk.W)
quantum_label.grid(row=0, column=1, sticky="ew", padx=(8, 0))

local_text = tk.Text(panels, wrap=tk.WORD, height=34, width=54,
                     font=('Consolas', 15))
local_text.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

local_text.config(state=tk.DISABLED)

quantum_text = tk.Text(panels, wrap=tk.WORD, height=34, width=54,
                       font=('Consolas', 15))
quantum_text.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
quantum_text.config(state=tk.DISABLED)

update_output()
root.mainloop()
