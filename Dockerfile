FROM python:3.11-slim

# System deps for Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libgbm1 libasound2 libxcomposite1 libxdamage1 \
    libxrandr2 libpango-1.0-0 libcairo2 libcups2 \
    libdbus-1-3 libexpat1 libxfixes3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY pyproject.toml ./
RUN pip install --no-cache-dir . && \
    pip install --no-cache-dir playwright && \
    playwright install chromium

# Copy source
COPY . .

# Re-install to register entry point
RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["agentic-playwright-mcp"]
