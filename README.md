# Coil Pack Designer — README

## 📌 Overview
`coil_pack_app.py` is a **Tkinter-based GUI application** for designing and visualizing coil winding layouts on a bobbin. It calculates **packing efficiency**, **strand positions**, and provides a **graphical representation** of the coil cross-section.

---

## ✅ Features
- Interactive GUI with **metric/inch toggle**.
- Visual representation of:
  - Bobbin window
  - Coil strands
  - Wire bundle illustration
- Calculates:
  - **Fill Factor (%)**
  - **Adjusted Turns**
- Supports **multi-strand wires** and **packing factors**.

---

## ⚙️ Operation
1. **Run the app**:
   ```bash
   python coil_pack_app.py
   ```
2. **Enter coil parameters** in the left panel:
   - Inner/Outer diameter
   - Bobbin length
   - Wire diameter
   - Strands per turn
   - Turns per layer
   - Total turns
   - Horizontal & Vertical packing factors
   - Wire type (Copper/Aluminum)
3. Click **Redraw** to update visualization.
4. Use **Toggle Units** to switch between metric (mm) and English (inches).

---

## 🔑 Inputs
| Parameter                | Description                                  |
|-------------------------|----------------------------------------------|
| `inner_diameter_mm`    | Bobbin inner diameter (mm)                  |
| `outer_diameter_mm`    | Bobbin outer diameter (mm)                  |
| `bobbin_length_mm`     | Bobbin axial length (mm)                    |
| `strand_diameter_mm`   | Diameter of each wire strand (mm)           |
| `strands_per_turn`     | Number of strands in one turn               |
| `turns_per_layer`      | Turns per layer                             |
| `total_turns`          | Total number of turns                       |
| `horiz_pack_factor`    | Horizontal packing factor (default 0.86)    |
| `vert_pack_factor`     | Vertical packing factor (default 0.77)      |
| `wire_type`            | Copper or Aluminum                          |

---

## 📤 Outputs
| Output                  | Description                                  |
|-------------------------|----------------------------------------------|
| `window_width_mm`      | Effective winding window width (mm)         |
| `window_height_mm`     | Effective winding window height (mm)        |
| `layers`               | Number of layers                            |
| `strand_centers`       | List of (x, y) positions for each strand    |
| `strand_radius_mm`     | Radius of each strand (mm)                  |
| `fill_factor`          | Copper fill factor (%)                      |
| `adjusted_turns`       | Total turns considered                      |

---

## 📐 Theory & Equations

### 1. **Effective Window Dimensions**
```math
window_width = bobbin_length_mm - 2 × margin_mm
window_height = (outer_diameter_mm - inner_diameter_mm)/2 - 2 × margin_mm
```

### 2. **Effective Strand Diameter**
```math
d_eff = strand_diameter_mm × insulation_factor
strand_radius = d_eff / 2
```

### 3. **Spacing Between Turns**
```math
spacing_x = (strands_per_turn × d_eff) × horiz_pack_factor
spacing_y = d_eff × vert_pack_factor
```

### 4. **Fill Factor**
```math
fill_factor (%) = (Copper_Area / Window_Area) × 100
Copper_Area = N_strands_in_window × π × (strand_radius)^2
Window_Area = window_width × window_height
```

### 5. **Layer Calculation**
```math
layers = ceil(total_turns / turns_per_layer)
```

---

## 🖼 Visualization
- **Outer rectangle**: Bobbin cross-section
- **Inner rectangle**: Winding window
- **Circles**: Wire strands
- **Color coding**: Alternating layers for clarity
- **Bundle illustration**: Shows strand arrangement and dimensions

---

## ✅ Dependencies
- Python 3.x
- `tkinter`
- `matplotlib`

Install missing packages:
```bash
pip install matplotlib
```

---

## ▶️ Example
Default parameters:
- Inner Diameter: 8.375 in
- Outer Diameter: 10.53 in
- Bobbin Length: 0.546 in
- Wire Diameter: 0.0337 in
- Strands per Turn: 3
- Turns per Layer: 5
- Total Turns: 180

---

## ⚠️ Assumptions & Limitations
- No staggering of turns.
- Fixed insulation factor (default 1.08).
- Margins applied uniformly.
- Visualization is schematic, not to scale for manufacturing.

