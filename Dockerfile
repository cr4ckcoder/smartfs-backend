FROM python:3.12-slim

# System deps for WeasyPrint (minimal set)
RUN apt-get update && apt-get install -y \
    build-essential libffi-dev libpango-1.0-0 libpangoft2-1.0-0 \
    libcairo2 libcairo2-dev libgdk-pixbuf-2.0-0 shared-mime-info fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]