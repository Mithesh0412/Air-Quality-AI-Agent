# Air Quality AI Agent - Backend

This repository provides a simple AI agent that can fetch real-time and historical air quality data using OpenAQ.

## Installation & Setup

1. **Install dependencies**  
    Make sure you have Python 3.13+ and a virtual environment activated, then run:  
    ```bash
    pip install -r requirements.txt
2. **Set up environment variables**  
    Create a `.env` file in the root directory and add your Google and OpenAQ API key:  
    ```env
    GOOGLE_API_KEY=your_api_key_here
    OPENAQ_API_KEY=your_api_key_here
3. **Start the FastAPI server with Uvicorn:**
    ```bash
    uvicorn main:app --reload
