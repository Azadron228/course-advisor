FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy only requirements first to leverage Docker cache
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv
# --system flag ensures it installs into the system site-packages (standard for simple Docker images)
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
