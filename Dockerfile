FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[gateway]" && useradd -u 10001 -m app
USER 10001
EXPOSE 8080
CMD ["uvicorn", "sovereign_ai.gateway_app:app", "--host", "0.0.0.0", "--port", "8080"]
