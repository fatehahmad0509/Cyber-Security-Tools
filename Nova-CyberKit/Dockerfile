# Render's native (non-Docker) Python runtime does not allow installing
# system packages with apt-get. Since nmap and phoneinfoga are system
# binaries, this service must be deployed on Render with the "Docker"
# runtime (Render Dashboard -> service -> Settings ->
# Build & Deploy -> Runtime: Docker).

FROM python:3.12-slim

# --- System dependencies ---
# nmap: for the /nmap command
# curl, ca-certificates: to download the phoneinfoga binary
RUN apt-get update && apt-get install -y --no-install-recommends \
        nmap \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- PhoneInfoga (Go binary) installation ---
# GitHub's stable "latest/download" URL always redirects to the latest
# release's Linux x86_64 package, with no API query needed.
RUN set -eux; \
    curl -fsSL "https://github.com/sundowndev/phoneinfoga/releases/latest/download/phoneinfoga_Linux_x86_64.tar.gz" -o /tmp/phoneinfoga.tar.gz; \
    tar -xzf /tmp/phoneinfoga.tar.gz -C /usr/local/bin phoneinfoga; \
    chmod +x /usr/local/bin/phoneinfoga; \
    rm /tmp/phoneinfoga.tar.gz

WORKDIR /app

# Copying and installing dependencies first prevents the Docker layer
# cache from being invalidated when the code changes (holehe included,
# it is in requirements.txt).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render injects the PORT environment variable itself; main.py already
# reads os.environ["PORT"] and binds to it (see main.py).
EXPOSE 8080

CMD ["python", "main.py"]
