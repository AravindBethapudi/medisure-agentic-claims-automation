FROM python:3.12-slim

# Install curl + gcc
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set work directory
WORKDIR /app

# Install Python packages
COPY backend/requirements.txt ./backend/
COPY streamlit_app/requirements.txt ./streamlit_app/
RUN pip install --no-cache-dir -r backend/requirements.txt -r streamlit_app/requirements.txt

# Copy code
COPY . .

# Create Streamlit secrets in the correct location (/root/.streamlit/)
RUN mkdir -p /root/.streamlit && \
    printf '[general]\nBACKEND_URL = "http://localhost:8000"\n' > /root/.streamlit/secrets.toml

# Make Python find your modules
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000 8501 11434

# Startup script
RUN printf '#!/bin/bash\n\
set -e\n\
echo "Starting Ollama service..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
echo "Waiting for Ollama to be ready..."\n\
for i in {1..30}; do\n\
  if ollama list >/dev/null 2>&1; then\n\
    echo "Ollama is ready!"\n\
    break\n\
  fi\n\
  echo "Waiting for Ollama... ($i/30)"\n\
  sleep 2\n\
done\n\
\n\
echo "Pulling llama3.2:1b model..."\n\
ollama pull llama3.2:1b || echo "Warning: Failed to pull model"\n\
\n\
echo "Starting backend API..."\n\
cd /app && uvicorn backend.main:app --host 0.0.0.0 --port 8000 &\n\
\n\
echo "Starting Streamlit app..."\n\
streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true\n' > start.sh \
    && chmod +x start.sh

CMD ["/bin/bash", "/app/start.sh"]