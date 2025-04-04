# Blueprint Analysis Application

A powerful desktop application for processing AutoCAD blueprints to automatically detect materials, symbols, and generate tasks.

## Overview

This application helps construction professionals and engineers process blueprint documents through computer vision and machine learning techniques. It allows users to upload blueprint files, identify and link symbols from the legend, detect those symbols throughout the document, and automatically generate related tasks.

## Features

- **Blueprint Image Processing**: Upload and process AutoCAD blueprints in various formats
- **Legend Detection**: Interactively select and analyze the legend section
- **Symbol Recognition**: Detect various types of symbols (colors, shapes, patterns)
- **Text Recognition**: Extract and link text labels with corresponding symbols
- **Symbol Mapping**: Locate all instances of legend symbols throughout the blueprint
- **Task Generation**: Automatically create tasks based on detected materials and components
- **Interactive Navigation**: Zoom, pan, and navigate large blueprint documents
- **Session Management**: Save and restore analysis sessions

## Installation

### Prerequisites

- Python 3.8+
- OpenCV
- Tesseract OCR
- Tkinter

### Setup

#### Clone the repository:

   ```bash
   git clone https://github.com/Dr2xU/BuildVisionAI.git BuildVisionAI
   cd BuildVisionAI
   ```

#### Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

#### Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

#### Ensure Tesseract OCR is installed on your system:
   - Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

## Usage

#### Launch the application:

   ```bash
   python main.py
   ```

#### Upload a blueprint file through the welcome screen

#### Select the legend area in the blueprint

#### Link symbols to their text descriptions

#### Analyze the full blueprint to detect all symbol instances

#### Review and customize generated tasks

#### Export tasks to your preferred format

## Project Structure

   ```bash
   .
   ├── main.py                     # Application entry point
   ├── ui/                         # User interface components
   │   ├── welcome.py              # Welcome and file upload screen
   │   ├── legend_selector.py      # Legend area selection component
   │   ├── symbol_linker.py        # Symbol to text linking component
   │   ├── blueprint_analyzer.py   # Full blueprint analysis component
   │   ├── task_generator.py       # Task generation component
   │   └── workflow_manager.py     # Workflow orchestration
   ├── utils/                      # Utility functions
   │   ├── image_tools.py          # Image processing utilities
   │   └── ocr_helpers.py          # OCR enhancement utilities
   ├── models/                     # Data models
   ├── legend_symbols/             # Directory for storing legend data
   └── symbol_links/               # Directory for storing symbol links
   ```

## Development

### Key Technologies

- **Tkinter**: GUI framework for the desktop application
- **OpenCV**: Computer vision library for image processing and symbol detection
- **PyTesseract**: OCR engine for text recognition
- **NumPy**: Numerical operations on image data

### Future Development

- Web version integration (Kotlin)
- Mobile application integration (Expo)
- Enhanced machine learning for symbol recognition
- Cloud storage for projects and tasks

## License

[MIT License](LICENSE.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- OpenCV Community
- Tesseract OCR Project
- Python Tkinter Documentation
