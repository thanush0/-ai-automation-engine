# AI Automation Engine

An intelligent automation system that uses AI (OpenAI GPT or local LLM) to parse natural language commands and execute browser and system automation tasks.

## 🌟 Features

- **Natural Language Processing**: Convert plain English commands into executable automation tasks
- **Browser Automation**: Control Chrome browser with Selenium for web interactions
- **System Control**: Execute system-level tasks (open apps, keyboard/mouse control, screenshots)
- **Dual AI Support**: Use OpenAI API or local Ollama LLM
- **WebSocket Interface**: Real-time communication via FastAPI backend
- **Task Management**: Queue and track automation tasks with status monitoring

## 🏗️ Architecture

The system consists of several core components:

- **`main.py`**: FastAPI server with REST API and WebSocket endpoints
- **`ai_parser.py`**: AI-powered command parser (supports OpenAI and Ollama)
- **`automation_engine.py`**: Executes parsed actions and manages workflow
- **`browser_controller.py`**: Selenium-based web browser automation
- **`system_controller.py`**: PyAutoGUI-based system control
- **`task_manager.py`**: Task queue management and status tracking
- **`config.py`**: Configuration management with environment variables

## 📋 Requirements

- Python 3.8+
- Chrome browser
- OpenAI API key (optional, for GPT) or Ollama (for local LLM)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Project-auto
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key or configure local LLM
```

## ⚙️ Configuration

Edit `.env` file:

```env
# Use OpenAI GPT
OPENAI_API_KEY=your_api_key_here
USE_LOCAL_LLM=false

# Or use local Ollama
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Browser settings
HEADLESS_BROWSER=false
BROWSER_TIMEOUT=30

# System control
ENABLE_SYSTEM_CONTROL=true
REQUIRE_CONFIRMATION=false
```

## 🎯 Usage

### Start the server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Execute Command
```bash
POST /api/command
Content-Type: application/json

{
  "command": "open youtube and search for python tutorials"
}
```

#### WebSocket for real-time updates
```javascript
ws://localhost:8000/ws
```

### Example Commands

- **Browser Automation**:
  - `"open youtube and search for songs"`
  - `"open chrome and go to google.com"`
  - `"search for AI on youtube and play first video"`

- **System Control**:
  - `"open notepad"`
  - `"open calculator"`
  - `"take a screenshot"`

## 📚 Supported Actions

### Browser Actions
- `open_browser`: Launch Chrome browser
- `navigate`: Go to specific URL
- `search_web`: Search on websites (YouTube, Google)
- `click`: Click elements
- `type_text`: Fill form fields
- `close_browser`: Close browser

### System Actions
- `open_app`: Launch applications (notepad, calculator, etc.)
- `press_key`: Press keyboard keys
- `hotkey`: Press key combinations
- `screenshot`: Capture screen
- `type_text`: Type text
- `wait`: Pause execution

## 🔧 Development

### Project Structure
```
Project-auto/
├── main.py                    # FastAPI application
├── ai_parser.py              # NLP command parser
├── automation_engine.py      # Action executor
├── browser_controller.py     # Browser automation
├── system_controller.py      # System control
├── task_manager.py           # Task queue manager
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
└── README.md                # Documentation
```

### Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `selenium` - Browser automation
- `webdriver-manager` - ChromeDriver management
- `pyautogui` - System automation
- `pywinauto` - Windows automation
- `openai` - OpenAI API client
- `langchain` - LLM framework
- `chromadb` - Vector database

## 🛡️ Safety Features

- Configurable confirmation prompts
- Failsafe mode for PyAutoGUI
- Error handling and logging
- Task status tracking

## ⚠️ Limitations

- Windows-specific system control features
- Chrome browser required
- Some websites may block automation
- Local LLM may have lower accuracy than GPT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🔒 Security Notes

- Keep your `.env` file secure and never commit it
- Use API keys responsibly
- Be cautious with system control permissions
- Test automation scripts in safe environments

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.
"# social-media-automation-lab" 
