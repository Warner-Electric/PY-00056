
import tkinter as tk
from tkinter import ttk
import matplotlib
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class CoilInputs:
    inner_diameter_mm: float
    outer_diameter_mm: float
    bobbin_length_mm: float
    strand_diameter_mm: float
    strands_per_turn: int
    turns_per_layer: int
    total_turns: int
    insulation_factor: float = 1.08
    margin_mm: float = 0.75
    lead_slot_width_mm: float = 10.0
    lead_slot_depth_mm: float = 5.0
    horiz_pack_factor: float = .86
    vert_pack_factor: float = .77
    wire_type: str = 'Copper'

@dataclass
class CoilOutputs:
    window_width_mm: float
    window_height_mm: float
    layers: int
    strand_centers: List[Tuple[float, float]]
    strand_radius_mm: float
    fill_factor: float
    adjusted_turns: int


class CoilPackModel:
    def __init__(self, inputs: CoilInputs):
        self.inp = inputs

    def compute(self) -> CoilOutputs:
        p = self.inp
        radial_thickness = (p.outer_diameter_mm - p.inner_diameter_mm) / 2.0
        window_height = max(0.0, radial_thickness - 2 * p.margin_mm)
        window_width = max(0.0, p.bobbin_length_mm - 2 * p.margin_mm)
        d_eff = p.strand_diameter_mm * p.insulation_factor
        radius = d_eff / 2.0

        # If window dimensions invalid, return empty result
        if window_width <= 0 or window_height <= 0:
            return CoilOutputs(window_width, window_height, 0, [], radius, 0.0, 0)

        # Bundle and spacing
        bundle_w = p.strands_per_turn * d_eff
        spacing_x = bundle_w * p.horiz_pack_factor
        spacing_y = d_eff * p.vert_pack_factor

        centers_global = []
        remaining = p.total_turns
        layers = math.ceil(p.total_turns / max(1, p.turns_per_layer))

        # Horizontal alignment (no staggering)
        for ly in range(layers):
            turns_this_layer = min(p.turns_per_layer, remaining)
            for tx in range(turns_this_layer):
                base_x = p.margin_mm + tx * spacing_x
                base_y = p.margin_mm + ly * spacing_y
                for s in range(p.strands_per_turn):
                    lx = s * d_eff
                    centers_global.append((base_x + lx + radius, base_y + radius))
            remaining -= turns_this_layer
            if remaining <= 0:
                break

        # Compute fill factor
        left, right = p.margin_mm, p.margin_mm + window_width
        bottom, top = p.margin_mm, p.margin_mm + window_height
        in_window_count = sum(1 for (x, y) in centers_global if left <= x <= right and bottom <= y <= top)
        copper_area = in_window_count * math.pi * (radius ** 2)
        window_area = window_width * window_height
        fill_factor = (copper_area / window_area) * 100 if window_area > 0 else 0.0

        return CoilOutputs(window_width, window_height, layers, centers_global, radius, fill_factor, p.total_turns)



class CoilApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Coil Pack Designer with Auto-Scaling")
        master.geometry("1100x700")
        self.pack(fill="both", expand=True)
        self.is_metric = True
        self.inputs = CoilInputs(
            inner_diameter_mm=8.375 * 25.4,
            outer_diameter_mm=10.53 * 25.4,
            bobbin_length_mm=0.546 * 25.4,
            strand_diameter_mm=0.0337 * 25.4,
            strands_per_turn=3,
            turns_per_layer=5,
            total_turns=180,
        )
        self._build_widgets()
        self._draw()

    def _build_widgets(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=8, pady=8)

        def add_entry(label, var, row):
            ttk.Label(left, text=label).grid(row=row, column=0, sticky="w")
            entry = ttk.Entry(left, textvariable=var, width=12)
            entry.grid(row=row, column=1)
            return entry

        self.vars = {
            "inner_diameter": tk.DoubleVar(value=self.inputs.inner_diameter_mm),
            "outer_diameter": tk.DoubleVar(value=self.inputs.outer_diameter_mm),
            "bobbin_length": tk.DoubleVar(value=self.inputs.bobbin_length_mm),
            "strand_diameter": tk.DoubleVar(value=self.inputs.strand_diameter_mm),
            "strands_per_turn": tk.IntVar(value=self.inputs.strands_per_turn),
            "turns_per_layer": tk.IntVar(value=self.inputs.turns_per_layer),
            "total_turns": tk.IntVar(value=self.inputs.total_turns),
            "horiz_pack_factor": tk.DoubleVar(value=self.inputs.horiz_pack_factor),
            "vert_pack_factor": tk.DoubleVar(value=self.inputs.vert_pack_factor),
        }

        row = 0
        add_entry("Inner Diameter", self.vars["inner_diameter"], row); row += 1
        add_entry("Outer Diameter", self.vars["outer_diameter"], row); row += 1
        add_entry("Bobbin Length", self.vars["bobbin_length"], row); row += 1
        add_entry("Wire Diameter", self.vars["strand_diameter"], row); row += 1
        add_entry("Strands per Turn", self.vars["strands_per_turn"], row); row += 1
        add_entry("Turns per Layer", self.vars["turns_per_layer"], row); row += 1
        add_entry("Total Turns", self.vars["total_turns"], row); row += 1
        add_entry("Horiz. Pack Factor", self.vars["horiz_pack_factor"], row); row += 1
        add_entry("Vert. Pack Factor", self.vars["vert_pack_factor"], row); row += 1

        
        # Wire Type Dropdown
        self.wire_type_var = tk.StringVar(value=self.inputs.wire_type)
        ttk.Label(left, text='Wire Type').grid(row=row, column=0, sticky='w')
        wire_type_dropdown = ttk.Combobox(left, textvariable=self.wire_type_var, values=['Copper', 'Aluminum'])
        wire_type_dropdown.grid(row=row, column=1)
        row += 1
        self.unit_label = ttk.Label(left, text="Current Units: Metric (mm)")
        self.unit_label.grid(row=row, column=0, columnspan=2, pady=10); row += 1
        ttk.Button(left, text="Toggle Units", command=self.toggle_units).grid(row=row, column=0, columnspan=2); row += 1
        ttk.Button(left, text="Redraw", command=self._draw).grid(row=row, column=0, columnspan=2, pady=6)

        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True)
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def toggle_units(self):
        if self.is_metric:
            for key in ["inner_diameter", "outer_diameter", "bobbin_length", "strand_diameter"]:
                var = self.vars[key]
                var.set(round(var.get() / 25.4, 4))
            self.unit_label.config(text="Current Units: English (inches)")
        else:
            for key in ["inner_diameter", "outer_diameter", "bobbin_length", "strand_diameter"]:
                var = self.vars[key]
                var.set(round(var.get() * 25.4, 3))
            self.unit_label.config(text="Current Units: Metric (mm)")
        self.is_metric = not self.is_metric
        self._draw()

    def _get_inputs(self):
        factor = 25.4 if not self.is_metric else 1.0
        return CoilInputs(
            inner_diameter_mm=self.vars["inner_diameter"].get() * factor,
            outer_diameter_mm=self.vars["outer_diameter"].get() * factor,
            bobbin_length_mm=self.vars["bobbin_length"].get() * factor,
            strand_diameter_mm=self.vars["strand_diameter"].get() * factor,
            strands_per_turn=self.vars["strands_per_turn"].get(),
            turns_per_layer=self.vars["turns_per_layer"].get(),
            total_turns=self.vars["total_turns"].get(),
            horiz_pack_factor=self.vars["horiz_pack_factor"].get(),
            vert_pack_factor=self.vars["vert_pack_factor"].get(),
        wire_type=self.wire_type_var.get(),
        )

    def _draw(self):
        inputs = self._get_inputs()
        model = CoilPackModel(inputs)
        outs = model.compute()
        display_factor = 1.0 if self.is_metric else 1/25.4
        unit_label = "mm" if self.is_metric else "in"

        self.ax.clear()
        outer_width = inputs.bobbin_length_mm * display_factor
        outer_height = ((inputs.outer_diameter_mm - inputs.inner_diameter_mm) / 2.0) * display_factor
        self.ax.add_patch(matplotlib.patches.Rectangle((0, 0), outer_width, outer_height, edgecolor='black', facecolor='none', linewidth=2))

        margin_disp = inputs.margin_mm * display_factor
        inner_width = outs.window_width_mm * display_factor
        inner_height = outs.window_height_mm * display_factor
        self.ax.add_patch(matplotlib.patches.Rectangle((margin_disp, margin_disp), inner_width, inner_height, edgecolor='green', facecolor='none', linewidth=1.5))

        notch_w = inputs.lead_slot_width_mm * display_factor
        notch_d = inputs.lead_slot_depth_mm * display_factor
        self.ax.add_patch(matplotlib.patches.Rectangle((-notch_d, (outer_height - notch_w)/2), notch_d, notch_w, edgecolor='black', facecolor='none', linewidth=2))

        for (x, y) in outs.strand_centers:
            layer_index = int((y - inputs.margin_mm) / (inputs.strand_diameter_mm * inputs.insulation_factor * inputs.vert_pack_factor))
            color = '#f5b54b' if (layer_index % 2 == 0) else '#add8e6'
            circ = matplotlib.patches.Circle((x * display_factor, y * display_factor), outs.strand_radius_mm * display_factor, edgecolor='black', facecolor=color, linewidth=0.8)
            self.ax.add_patch(circ)

        
        # --- Enhanced Wire Bundle Illustration ---
        illustration_x = outer_width + (30 * display_factor)
        illustration_y = outer_height / 2.0

        d_eff = inputs.strand_diameter_mm * inputs.insulation_factor
        strand_radius_mm = d_eff / 2.0
        strands = inputs.strands_per_turn
        wire_type = inputs.wire_type

        # Draw strands horizontally
        for s in range(strands):
            lx = s * d_eff * display_factor
            circ_bundle = matplotlib.patches.Circle(
                (illustration_x + lx, illustration_y),
                strand_radius_mm * display_factor,
                edgecolor='black', facecolor='#add8e6', linewidth=1.2
            )
            self.ax.add_patch(circ_bundle)

        # Add label for wire bundle
        self.ax.text(illustration_x, illustration_y + 15 * display_factor,
                    f"Wire Bundle ({strands} strands)", fontsize=12, fontweight='bold')

        # Add wire type and diameter info
        self.ax.text(illustration_x, illustration_y - 20 * display_factor,
                    f"Type: {wire_type}\nDiameter per strand: {inputs.strand_diameter_mm:.2f} {unit_label}",
                    fontsize=10, color='darkblue')

        # Dimension arrow for bundle width
        arrow_start_x = illustration_x
        arrow_end_x = illustration_x + (strands - 1) * d_eff * display_factor
        self.ax.annotate("", xy=(arrow_start_x, illustration_y - 5 * display_factor),
                        xytext=(arrow_end_x, illustration_y - 5 * display_factor),
                        arrowprops=dict(arrowstyle='<->', color='black'))
        self.ax.text((arrow_start_x + arrow_end_x) / 2, illustration_y - 10 * display_factor,
                    f"Bundle width: {strands * inputs.strand_diameter_mm:.2f} {unit_label}", ha='center', fontsize=9)

        # Dimension arrow for strand diameter
        self.ax.annotate("", xy=(illustration_x + 20 * display_factor, illustration_y - strand_radius_mm * display_factor),
                        xytext=(illustration_x + 20 * display_factor, illustration_y + strand_radius_mm * display_factor),
                        arrowprops=dict(arrowstyle='<->', color='black'))
        self.ax.text(illustration_x + 22 * display_factor, illustration_y,
                    f"{inputs.strand_diameter_mm:.2f} {unit_label}", va='center', fontsize=9)
# Show fill factor and adjusted turns
        self.ax.text(outer_width/2, outer_height + (5 * display_factor), f"Fill Factor: {outs.fill_factor:.2f}%", fontsize=14, ha='center', color='red')
        self.ax.text(outer_width/2, outer_height + (12 * display_factor), f"Adjusted Turns: {outs.adjusted_turns}", fontsize=12, ha='center', color='blue')

        margin = max(outer_width, outer_height) * 0.15
        
        extra_space = illustration_x + (strands * d_eff * display_factor) + (50 * display_factor)
        self.ax.set_xlim(-notch_d - margin, extra_space)

        self.ax.set_ylim(-margin, outer_height + margin)
        self.ax.set_title(f'Rectangular Bobbin Cross-Section ({unit_label})')
        self.ax.set_xlabel(unit_label)
        self.ax.set_ylabel(unit_label)
        self.ax.set_aspect('equal', adjustable='box')
        self.fig.tight_layout()
        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = CoilApp(root)
    root.mainloop()
