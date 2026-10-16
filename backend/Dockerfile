# PyTorch wheels bundle CUDA: the host only needs the NVIDIA driver + container toolkit.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .
COPY docker-entrypoint.sh /usr/local/bin/

ENV YUI_DATA_DIR=/data \
    HF_HOME=/data/huggingface \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/system/status')"
ENTRYPOINT ["docker-entrypoint.sh"]
