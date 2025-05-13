# API Model Assessor (AMM) Requirements Document

## Document Types and Requirements

### 1. Text Documents
**Supported Extensions:** `.txt`, `.md`, `.rtf`
**Data Type:** Plain text
**Maximum Size:** No hard limit, but token limits apply
**Example:**
```
This is a sample text document.
It can contain multiple paragraphs and basic formatting.
Special characters are supported: !@#$%^&*()
```

### 2. Code Files
**Supported Extensions:** 
- `.py` (Python)
- `.js` (JavaScript)
- `.cpp`, `.c` (C/C++)
- `.java` (Java)
- `.rb` (Ruby)
- `.go` (Go)
- `.rs` (Rust)
- `.ts` (TypeScript)
- `.php` (PHP)
- `.cs` (C#)
- `.swift` (Swift)
- `.kt` (Kotlin)
- `.scala` (Scala)
- `.sh` (Shell)
- `.bat` (Batch)
- `.pl` (Perl)
- `.r` (R)
- `.jl` (Julia)
- `.lua` (Lua)
- `.sql` (SQL)
- `.html` (HTML)
- `.css` (CSS)
- `.json` (JSON)
- `.xml` (XML)
- `.yaml`, `.yml` (YAML)
- `.ipynb` (Jupyter Notebook)

**Data Type:** Plain text with syntax highlighting
**Maximum Size:** No hard limit, but token limits apply
**Example:**
```python
def hello_world():
    print("Hello, World!")
    return True
```

### 3. Image Files
**Supported Extensions:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.ico`
**Data Type:** Binary
**Maximum Size:** No hard limit, but model-specific limits apply
**Requirements:**
- Must be a valid image file
- Must be readable by PIL (Python Imaging Library)
- Must not be corrupted

### 4. Video Files
**Supported Extensions:** `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.mkv`, `.webm`
**Data Type:** Binary
**Maximum Size:** No hard limit, but model-specific limits apply
**Requirements:**
- Must be a valid video file
- Must be playable by standard video players
- Must not be corrupted

### 5. Audio Files
**Supported Extensions:** `.mp3`, `.wav`, `.aac`, `.ogg`, `.flac`, `.m4a`
**Data Type:** Binary
**Maximum Size:** No hard limit, but model-specific limits apply
**Requirements:**
- Must be a valid audio file
- Must be playable by standard audio players
- Must not be corrupted

### 6. PDF Documents
**Supported Extensions:** `.pdf`
**Data Type:** Binary
**Maximum Size:** No hard limit, but model-specific limits apply
**Requirements:**
- Must be a valid PDF file
- Must be readable by standard PDF readers
- Must not be corrupted

### 7. Archive Files
**Supported Extensions:** `.zip`, `.rar`, `.7z`, `.tar`, `.gz`
**Data Type:** Binary
**Maximum Size:** No hard limit, but model-specific limits apply
**Requirements:**
- Must be a valid archive file
- Must be extractable by standard archive tools
- Must not be corrupted

## Model Requirements

### Text Processing Models
- Must support text input/output
- Must have defined input and output token costs
- Must have a maximum token limit per call
- Must be able to process plain text and code files

### Image Processing Models
- Must support image input
- Must have defined image cost per image
- Must have defined output token cost for image analysis
- Must be able to process standard image formats

### Video Processing Models
- Must support video input
- Must have defined cost per minute of video
- Must be able to process standard video formats

### Audio Processing Models
- Must support audio input
- Must have defined cost per minute of audio
- Must be able to process standard audio formats

### Multi-modal Models
- Must support multiple input types (text, image, video, audio)
- Must have defined costs for each supported input type
- Must have defined output token costs
- Must be able to process all supported formats for their type

## Cost Calculation

### Text and Code
- Input cost = (input tokens / 1,000,000) * input_cost_per_1M
- Output cost = (output tokens / 1,000,000) * output_cost_per_1M
- Total cost = input cost + output cost

### Images
- Base cost = image_cost_per_image
- Output cost = (output tokens / 1,000,000) * output_cost_per_1M
- Total cost = base cost + output cost

### Video
- Cost = (video duration in minutes) * video_cost_per_minute

### Audio
- Cost = (audio duration in minutes) * audio_cost_per_minute

## Notes
1. All costs are in USD
2. Token estimates are approximate and may vary by model
3. Some models may have additional requirements or limitations
4. File size limits may be imposed by the API provider
5. Processing times may vary based on file size and model capabilities 

## CSV Reference File Format

### Required Fields

| Field Name | Data Type | Allowed Characters | Description |
|------------|-----------|-------------------|-------------|
| Company | String | A-Z, a-z, 0-9, spaces, hyphens, periods | Name of the company providing the model |
| Model | String | A-Z, a-z, 0-9, spaces, hyphens, periods | Name of the model |
| Version | String | A-Z, a-z, 0-9, periods, hyphens | Version number of the model |
| API Types | String | Comma-separated list of: "Text", "Code", "Image", "Video", "Audio", "Multi-modal" | Types of content the model can process |
| Max Tokens per Call | Integer | 0-9 | Maximum number of tokens the model can process in a single call |
| Input Token Cost ($ per 1M) | Decimal | 0-9, decimal point | Cost per million input tokens in USD |
| Output Token Cost ($ per 1M) | Decimal | 0-9, decimal point | Cost per million output tokens in USD |

### Optional Fields

| Field Name | Data Type | Allowed Characters | Description |
|------------|-----------|-------------------|-------------|
| Video Cost ($ per minute) | Decimal | 0-9, decimal point | Cost per minute of video processing in USD |
| Audio Cost ($ per minute) | Decimal | 0-9, decimal point | Cost per minute of audio processing in USD |
| Image Cost ($ per image) | Decimal | 0-9, decimal point | Cost per image processing in USD |
| Flat File Cost | Decimal | 0-9, decimal point | Flat rate cost for file processing in USD |
| Notes | String | Any printable ASCII characters | Additional information about the model |

### CSV Format Rules
1. File must be UTF-8 encoded
2. Fields must be comma-separated
3. Text fields containing commas must be enclosed in double quotes
4. Decimal numbers must use period (.) as decimal separator
5. No currency symbols ($) should be included in cost fields
6. Empty fields should be left blank (no "N/A" or other placeholders)
7. Boolean values should be represented as "true" or "false" (lowercase)
8. Dates should be in ISO 8601 format (YYYY-MM-DD)

### Example CSV Row
```
Company,Model,Version,API Types,Max Tokens per Call,Input Token Cost ($ per 1M),Output Token Cost ($ per 1M),Video Cost ($ per minute),Audio Cost ($ per minute),Image Cost ($ per image),Flat File Cost,Notes
OpenAI,GPT-4,4.0,"Text,Code,Image",8192,0.03,0.06,0.05,0.02,0.01,,"Latest version with improved image understanding"
``` 