# GIS Data Standardization Pipeline (ArcPy)

## 📌 Overview
This project automates geospatial data preprocessing using ArcPy in ArcGIS Pro.

It standardizes multi-source GIS datasets including raster and vector formats into a unified coordinate system and spatial extent.

---

## 🚀 Features

- CSV → Point feature conversion
- ECW raster mosaicking
- Extent polygon generation (no 3D Analyst dependency)
- Projection to NAD83 UTM Zone 10N
- DEM clipping using spatial extent
- Vector clipping automation
- Logging + error handling
- ArcGIS Script Tool integration (UI-based execution)

---

## 🛠️ Tech Stack

- ArcGIS Pro
- ArcPy (Python)
- File Geodatabase

---

## 📂 Project Structure
src/ → Python automation script
toolbox/ → ArcGIS Script Tool
sample_data/ → Example inputs
outputs/ → Screenshots + results

---

## ▶️ How to Run

### Option 1 — ArcGIS Tool (Recommended)

1. Open ArcGIS Pro
2. Add toolbox: `data_standardization_pipeline.atbx`
3. Run tool:
   - Base Folder → Project root folder
   - Output GDB → Target geodatabase

---

### Option 2 — Python Script

Run:

```bash
python pipeline_tool.py
```