# Lab 6: Production Dockerfile for TechCorp AI Service
# This is the skeleton file - merge with ../extra/lab6-Dockerfile to complete

# Multi-stage build for production optimization
FROM python:3.11-slim as base

# TODO: Add enterprise base configuration
# TODO: Setup security hardening
# TODO: Create non-root user
# TODO: Setup working directory structure

FROM base as dependencies

# TODO: Install system dependencies
# TODO: Copy and install Python requirements
# TODO: Optimize dependency installation

FROM dependencies as production

# TODO: Copy application code
# TODO: Setup health check endpoints
# TODO: Configure monitoring and logging
# TODO: Setup production entrypoint
# TODO: Add security and resource constraints

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# TODO: Setup proper user, expose ports, and define startup command