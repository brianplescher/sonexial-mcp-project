# Deployment Guide

## VPS Deployment (Ubuntu/Debian)

### Prerequisites

- Ubuntu 22.04+ or Debian 12+
- Domain name pointing to your server
- At least 512MB RAM, 1 vCPU

### Step 1: Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Log out and back in for group changes to take effect
```

### Step 2: Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url> sonexial-mcp
cd sonexial-mcp

# Create environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Important settings for production:
```
SONEXIAL_MCP_ENV=production
SONEXIAL_MCP_API_KEY=<generate-a-strong-random-string>
AUTH_DISABLED=false
```

Generate a secure API key:
```bash
openssl rand -hex 32
```

### Step 3: Deploy with Docker

```bash
# Build and start
docker compose up -d --build

# Check logs
docker compose logs -f

# Verify health
curl http://localhost:8080/healthz
```

### Step 4: Set Up Reverse Proxy (Caddy)

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Configure Caddy
sudo cp Caddyfile.example /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile
# Change mcp.yourdomain.com to your actual domain

# Restart Caddy
sudo systemctl restart caddy
```

Caddy will automatically obtain TLS certificates from Let's Encrypt.

### Step 5: Firewall

```bash
# Enable UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Note: Don't expose port 8080 directly if using Caddy as reverse proxy.

### Step 6: Verify

```bash
# Test the health endpoint
curl https://mcp.yourdomain.com/healthz

# Test a tool call
curl -X POST https://mcp.yourdomain.com/mcp \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tool": "ping", "arguments": {}}'
```

## Systemd Alternative (without Docker)

If you prefer to run without Docker:

```bash
# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3-pip -y

# Create app directory
sudo mkdir -p /opt/sonexial-mcp
sudo chown $USER:$USER /opt/sonexial-mcp

# Copy files
cp -r . /opt/sonexial-mcp/
cd /opt/sonexial-mcp

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy systemd service
sudo cp deploy/systemd/sonexial-mcp.service.example /etc/systemd/system/sonexial-mcp.service
sudo nano /etc/systemd/system/sonexial-mcp.service
# Adjust paths and user

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable sonexial-mcp
sudo systemctl start sonexial-mcp
```

## Backup

### SQLite Backup

```bash
# Simple backup script
#!/bin/bash
BACKUP_DIR="/opt/backups/sonexial"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Copy database file (safe while server is running with WAL mode)
cp /opt/sonexial-mcp/data/sonexial.db $BACKUP_DIR/sonexial_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "sonexial_*.db" -mtime +7 -delete
```

### PostgreSQL Backup

```bash
pg_dump -U sonexial sonexial_mcp > backup_$(date +%Y%m%d).sql
```

## Updating

```bash
cd /opt/sonexial-mcp  # or your project directory

# Pull latest code
git pull origin main

# Rebuild and restart
docker compose up -d --build

# Or for systemd:
# source .venv/bin/activate
# pip install -r requirements.txt
# sudo systemctl restart sonexial-mcp
```

## Monitoring

Check logs:
```bash
docker compose logs -f sonexial-mcp
# or
journalctl -u sonexial-mcp -f
```

Check resource usage:
```bash
docker stats sonexial-mcp
```

## Troubleshooting

- **Port already in use**: Check `sudo lsof -i :8080`
- **Database locked**: Ensure only one process is writing to SQLite
- **Auth failures**: Verify API key matches between client and server
- **CORS errors**: Check CORS_ORIGINS setting
