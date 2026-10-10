# PyTorch wheels bundle CUDA: the host only needs the NVIDIA driver + container toolkit.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
# Bake YuE2 into the image so a first start does not download it; the startup updater
# then only upgrades when a newer release exists. Set INSTALL_YUE=false for mock-only images.
ARG INSTALL_YUE=true
RUN if [ "$INSTALL_YUE" = "true" ]; then pip install --no-cache-dir ".[yue]"; else pip install --no-cache-dir .; fi

ENV YUI_DATA_DIR=/data \
    HF_HOME=/data/huggingface \
    PYTHONUNBUFFERED=1
VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
