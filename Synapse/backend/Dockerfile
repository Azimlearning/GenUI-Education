# Synapse backend (FastAPI + LangGraph). Build: docker build -t synapse-backend .
# Run:   docker run -p 8000:8000 --env-file .env synapse-backend
# The app runs scripted with no keys; set ANTHROPIC_API_KEY (and optionally OPENAI_API_KEY)
# in the env file to go live. Not deployed yet — pick a host (Render / Railway / Fly / Vercel
# functions) when ready (see ../decisions.md P-a).

FROM python:3.13-slim

WORKDIR /app

# uv resolves and installs from the committed lockfile.
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

ENV PORT=8000 LEARNER_STORE=sqlite LEARNER_STORE_PATH=/data/synapse.sqlite3
RUN mkdir -p /data

EXPOSE 8000
# Shell form so ${PORT} expands (hosts like Render inject their own port).
CMD uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
