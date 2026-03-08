# =============================================================================
# Module 6: Cloud Run Deployment - Dockerfile
# =============================================================================
# Custom Dockerfile for deploying ADK agent to Cloud Run
# Use this when you need more control over the container build process
# =============================================================================

FROM python:3.12-slim

WORKDIR /app

# =============================================================================
# SECURITY: Create non-root user
# =============================================================================
# Running as non-root is a security best practice for containers
# =============================================================================
RUN adduser --disabled-password --gecos "" pirateuser
RUN chown -R pirateuser:pirateuser /app
USER pirateuser

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
# These environment variables configure ADK for Vertex AI
# =============================================================================
ENV PATH="/home/pirateuser/.local/bin:$PATH"

# Enable Vertex AI backend (required for GCP deployment)
ENV GOOGLE_GENAI_USE_VERTEXAI=1

# GCP Project and Region - REPLACE with your values or use build args
ARG GOOGLE_CLOUD_PROJECT=your-project-id
ARG GOOGLE_CLOUD_LOCATION=us-central1

ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
ENV GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}

# =============================================================================
# INSTALL DEPENDENCIES
# =============================================================================
# Install ADK first, then project-specific requirements
# =============================================================================
RUN pip install --no-cache-dir google-adk>=1.18.0

# Copy agent files
# Copy everything to /app/agents/ folder (ADK expects a folder structure)
COPY --chown=pirateuser:pirateuser . /app/agents/

# Install project requirements if they exist
RUN if [ -f /app/agents/requirements.txt ]; then \
        pip install --no-cache-dir -r /app/agents/requirements.txt; \
    fi

# =============================================================================
# EXPOSE PORT AND RUN
# =============================================================================
# Cloud Run uses port 8080 by default - we must match this!
# =============================================================================
EXPOSE 8080

# Start ADK web server
# --host=0.0.0.0 is required to accept connections from outside the container
# --port=8080 matches Cloud Run's default PORT environment variable
# Point to the /app/agents folder where agent.py is located
CMD ["adk", "web", "--port=8080", "--host=0.0.0.0", "/app/agents"]

