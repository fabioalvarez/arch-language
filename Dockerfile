FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir textX==4.3.0
ENTRYPOINT ["python", "generation.py"]
