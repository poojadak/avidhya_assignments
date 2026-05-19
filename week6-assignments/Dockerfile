# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# We use the full Python image here to install dependencies.
# This stage does all the heavy lifting so the final image stays small.
FROM python:3.11 AS builder

WORKDIR /app

# Set environment variables to avoid writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies into a local folder so we can copy them cleanly later
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
# The slim image is much smaller — we only copy what we actually need to run.
FROM python:3.11-slim AS runtime

WORKDIR /app

# Keep the same env vars in the runtime image
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only the installed packages from the builder stage (no build tools)
COPY --from=builder /install /usr/local

# Copy the application code
COPY app/ ./app/
COPY plugins/ ./plugins/
COPY skills/ ./skills/
COPY CLAUDE.md .

# Create a non-root user for security — we never want to run as root in production
RUN useradd -m appuser
USER appuser

# Tell Docker the app listens on port 5000
EXPOSE 5000

# Health check so Docker (and docker-compose) knows when the container is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start the Flask app
CMD ["python", "-m", "flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
