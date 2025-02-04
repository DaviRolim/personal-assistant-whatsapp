# Personal Assistant Low-Level

An AI-powered personal assistant with tool integration built with FastAPI. Key features:
- Processes natural language requests through OpenAI's GPT-4o model
- Supports dynamic tool execution including Google Drive operations
- Manages conversational context with AI model interactions
- Implements tool calling architecture for extended functionality

## How to Run

### Prerequisites
- Python 3.9+
- OpenAI API key
- Google Service Account credentials (for Drive integration)

1. Clone the repository:
```bash
git clone https://github.com/your-username/personal-assistant-low-level.git
cd personal-assistant-low-level
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "GOOGLE_CREDENTIALS_PATH=path/to/your/service-account.json" >> .env
```

4. Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. For production deployment, add proper ASGI server configuration and environment management.
