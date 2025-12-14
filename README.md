# DeepSeek-OCR Clipboard

A modern, frameless, and efficient desktop application that automatically monitors your clipboard for images and performs OCR using the DeepSeek-OCR API. 

Built with Python and CustomTkinter for a sleek, dark-mode UI.

![DeepSeek OCR](assets/screenshot.png)

## Features

- **Automatic Detection**: Instantly detects new images copied to the clipboard.
- **High-Accuracy OCR**: Uses DeepSeek's Multimodal LLM capabilities for precise text extraction.
- **Modern UI**: Frameless, dark-themed design with CustomTkinter.
- **Auto-Copy**: Switch to automatically copy OCR results back to the clipboard.
- **Floating Window**: "Pin" mode to keep the window always on top.
### ⚠️ Privacy Warning

**Please Ensure:** Do NOT use this application when your clipboard contains sensitive information (e.g., passwords, personal data, confidential documents).
* All images detected in the clipboard will be automatically uploaded to the API provider (SiliconFlow) for processing.
* Ensure you trust the API provider and handle sensitive data with caution.

## Prerequisites

- Python 3.8+
- An API Key from [SiliconFlow](https://siliconflow.cn) (Model: `deepseek-ai/DeepSeek-OCR` or compatible)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DeepSeek-OCR-Clipboard.git
   cd DeepSeek-OCR-Clipboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: If `requirements.txt` is missing, install manually: `pip install requests pillow customtkinter`)*

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. **Configuration**:
   - Click **Settings** in the top right.
   - Enter your **API Key** (and API URL/Model if different from default).
   - Click **Save**.

3. **Start OCR**:
   - Take a screenshot or copy an image.
   - The app will display the image and the extracted text.

## Configuration

The application creates a `config.cfg` file in the root directory. This file contains your API credentials and settings.
**Note**: `config.cfg` is ignored by git to protect your API key.

## Development

- **`main.py`**: UI entry point and logic.
- **`ocr_engine.py`**: Handles API communication and image processing.
- **`clipboard_monitor.py`**: Background thread for polling clipboard changes.
- **`config_manager.py`**: Simple JSON-based config loader.

## License

[MIT License](LICENSE)
