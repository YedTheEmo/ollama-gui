# Ollama Chat GUI

## Overview  
Ollama Chat GUI is a Streamlit-based web application that offers a clean and intuitive interface to chat with Ollama AI models running locally. It allows users to select different models, adjust parameters like temperature and max tokens, and interact with the AI in real-time.

## Features  
- Model selection from available Ollama models  
- Adjustable temperature and max token settings  
- Customizable system prompt to guide AI behavior  
- Persistent chat history with clear chat option  
- Styled chat messages for better readability  

## Dependencies  
- Python 3.7+  
- Streamlit  
- Requests  
- Ollama AI running locally and accessible via API  

## Usage  
1. Ensure Ollama AI service is installed and running locally on port 11434.  
2. Install Python dependencies:  
   ```bash  
   pip install streamlit requests  
   ```
3. Run the app:  
   ```bash  
   streamlit run app.py  
   ```

