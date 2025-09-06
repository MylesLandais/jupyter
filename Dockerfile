FROM quay.io/jupyter/base-notebook:python-3.11
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    yt-dlp \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /home/jovyan/work && chown ${NB_UID}:${NB_GID} /home/jovyan/work
RUN mkdir -p /home/jovyan/downloads/ytdlp && chown ${NB_UID}:${NB_GID} /home/jovyan/downloads/ytdlp
USER ${NB_UID}:${NB_GID}
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt
EXPOSE 8888

WORKDIR /home/jovyan/workspaces

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
