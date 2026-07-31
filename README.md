# NPD Data Processor and GUI

A modern full-stack web application designed to upload, manage, and process Noise Power Density (NPD) test data.

This application provides an elegant, glassmorphic React frontend that guides users through selecting their testing mode (Upload or Access), choosing run/calibration files, configuring plotting parameters, and submitting them to a robust Python Flask backend. The backend utilizes `skrf`, `numpy`, and `pandas` to process raw S-Parameter (VSWR/S21) and NPD density data, outputting trace payloads to the frontend. The frontend uses `react-plotly.js` to render interactive SVG plots dynamically with built-in data thinning for large datasets.

## Features

- **Test Modes**: Supports Test 1 (Thermal NPD), Test 2 (Benchtop Single Run), Test 3 (Benchtop Array), Test 4 (Over-Temp Arrays), and Test 5 (Generic Plotter for ad-hoc CSV/S2P files).
- **File Upload & Navigation**: Users can browse the local file system or drag-and-drop entire run directories using native browser APIs.
- **Interactive Plotting**: Lightning fast, interactive plots rendered via Plotly on the frontend, avoiding heavy backend Matplotlib generation.
- **Plot Configuration**: Customizable frequency bounds, gain requirements, S21 bounds, and NPD bounds.
- **Dynamic Averaging**: Smart backend logic automatically detects frequency step sizes in NPD data and scales moving average smoothing windows for optimal plotting.
- **Python Data Engine**: Advanced signal processing, nan-filtering, array operations, and calibration line-loss subtractions.
- **Automated Routing**: Backend intelligently routes files into `SN`, `LMO`, and `Run` directory structures.

## Project Structure

- `frontend/`
  - React + Vite web application containing UI components and form states.
  - Developed with modern CSS, using fluid animations, dark modes, and dynamic designs.
- `backend/`
  - Python Flask application serving a REST API to interface with the frontend.
  - Contains the centralized plotting script: `plot_generator.py`.

## Getting Started

### Prerequisites
- Node.js (v16+)
- Python (3.9+)

### Installation
1. Install Python dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
2. Install Node dependencies:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

### Running the App
To run the application easily on Windows, execute the included batch script:
```bash
Run_App.bat
```
This script will start the backend server and serve the pre-built frontend via Flask on `http://127.0.0.1:5001`.

## Documentation

The Python backend files contain detailed docstrings summarizing function parameters and logic. See individual script headers for an overview of their plotting behaviors.
