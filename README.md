# Phone Number Extractor

Extract phone numbers from WhatsApp contact list screen recordings using Google's Gemini AI.

## Overview

This tool processes a video recording of scrolling through a WhatsApp contact list and extracts all visible phone numbers into a CSV file. It uses computer vision to extract frames from the video and Gemini's multimodal AI to recognize and extract contact information.

## Features

- 🎬 **Video Frame Extraction** - Automatically extracts frames from video at configurable intervals
- 🤖 **AI-Powered OCR** - Uses Gemini 2.5 Flash for accurate contact extraction
- 🔄 **API Key Rotation** - Supports multiple API keys with automatic failover on rate limits
- 📊 **Deduplication** - Outputs only unique phone numbers
- 📁 **CSV Export** - Clean output format ready for import

## Installation

1. Clone the repository:
```bash
git clone https://github.com/IshatV412/phone_number_extractor.git
cd phone_number_extractor
```

2. Create and activate a virtual environment:
```bash
python3 -m venv ph_no
source ph_no/bin/activate
```

3. Install dependencies:
```bash
pip install opencv-python google-genai pyyaml pillow
```

4. Configure your API key(s) in `config.yaml`:
```yaml
api_keys:
  - "YOUR_GEMINI_API_KEY"
  - "OPTIONAL_BACKUP_KEY"

model: "gemini-2.5-flash"
rate: 100  # Extract every Nth frame
```

## Usage

### Quick Start

1. Place your WhatsApp screen recording in the `videos/` folder
2. Update the video path in `main.py` or pass it as an argument
3. Run the pipeline:

```bash
python3 main.py "videos/your_video.mp4"
```

### Command Line Options

```bash
# Run with default video
python3 main.py

# Run with a specific video
python3 main.py "path/to/video.mp4"

# Skip image extraction (reuse existing frames)
python3 main.py --skip-extract

# Clean images folder before processing
python3 main.py --clean
```

### Running Individual Steps

Each module can be run independently:

```bash
# Step 1: Extract frames from video
python3 extract_images.py

# Step 2: Extract contacts using Gemini API
python3 extract_contacts.py

# Step 3: Process and save to CSV
python3 post_process.py
```

## Project Structure

```
PhNoExtractor/
├── main.py              # Main pipeline orchestrator
├── extract_images.py    # Video frame extraction
├── extract_contacts.py  # Gemini API contact extraction
├── post_process.py      # JSON to CSV conversion & deduplication
├── config.yaml          # Configuration (API keys, model, rate)
├── videos/              # Input video files
├── images/              # Extracted frames (auto-generated)
├── contacts.json        # Raw API responses (intermediate)
└── contacts.csv         # Final output with unique contacts
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api_keys` | List of Gemini API keys | Required |
| `model` | Gemini model to use | `gemini-2.5-flash` |
| `rate` | Extract every Nth frame | `100` |

### API Key Rotation

The tool supports multiple API keys for handling rate limits. When a request fails due to:
- Rate limiting (429)
- Quota exceeded
- Invalid API key

It automatically switches to the next available key and retries.

## Output Format

The final `contacts.csv` contains:

| Name | Phone |
|------|-------|
| John Doe | 9876543210 |
| | 8765432109 |

- Phone numbers are cleaned (no `+91`, no spaces)
- Only unique numbers are included
- Names may be empty for unsaved contacts

## Requirements

- Python 3.8+
- OpenCV
- Google GenAI SDK
- PyYAML
- Pillow

## License

MIT License
