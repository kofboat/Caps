FROM python:3.12-slim

WORKDIR /app

# Install runtime deps (none needed beyond Python stdlib for these libs)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY main.py ./

# Copy env file if provided at build time (optional)
# However, prefer passing env at runtime

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]