FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY jira_mcp_server.py .

# Run as non-root user
RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

# Set environment
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "jira_mcp_server.py"]
