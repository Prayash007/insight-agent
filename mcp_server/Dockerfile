FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY mcp_server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server /app/mcp_server
COPY backend/catalog /app/backend/catalog

EXPOSE 8001

CMD ["python", "-m", "mcp_server.server"]
