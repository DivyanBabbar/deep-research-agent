FROM python:3.15-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && mkdir -p /app/data && chown -R 10001:10001 /app
EXPOSE 8000
USER 10001
CMD ["uvicorn", "research_agent.api:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src", "--proxy-headers"]
