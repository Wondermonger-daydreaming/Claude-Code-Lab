# Secure OpenClaw Deployment Guide

*January 30, 2026 — Created in response to the Clawdbot vulnerability disclosure*

## Context: The Butler Problem

This deployment guide was created after analyzing a security disclosure about Clawdbot—an AI agent gateway that was found widely exposed on the public internet. Hundreds of instances were discovered with:
- No authentication required
- Full conversation history exposed
- API keys and credentials readable
- Command execution as root

**The core issue:** AI agents need broad access to be useful (credentials, message history, shell execution), but that access creates massive attack surface when the agent infrastructure is misconfigured.

This guide configures OpenClaw to avoid those vulnerabilities.

---

## Configuration Summary

| Setting | Value |
|---------|-------|
| **Infrastructure** | Local machine (dev/testing) |
| **Platform** | WhatsApp |
| **Network access** | Tailscale |
| **Tool permissions** | Allowlist + prompt on miss |

---

## How This Plan Addresses the Butler Problem

### Vulnerability → Mitigation Mapping

| Clawdbot Vulnerability | OpenClaw Mitigation |
|------------------------|---------------------|
| **Localhost auto-approve behind reverse proxy** | Gateway binds to `127.0.0.1:18789` ONLY. No reverse proxy. Access via Tailscale mesh eliminates the proxy pattern entirely. |
| **Control UI exposed to public internet** | Local machine not exposed. Tailscale provides encrypted access only from your devices. |
| **Credential concentration** | `.env` file with restricted permissions. Log redaction patterns strip `sk-.*`, `pat_.*`, `Bearer.*` |
| **Conversation history exposure** | Data stored locally with restricted permissions. WhatsApp allowlist limits who can interact. |
| **Command execution as root** | Docker with non-root user, `cap_drop: ALL`, `read_only: true`. Sandbox mode enabled. |
| **No authentication required** | `gateway.auth.token` required. Device pairing requires explicit approval. |
| **Debug mode exposing data** | Production config: `level: info`, no debug mode. |
| **Perception attacks** | Partially addressed via allowlists. Inherent risk remains when agent mediates communication. |

---

## WhatsApp-Specific Security Considerations

⚠️ **WhatsApp uses device linking** (like Signal in the original disclosure). The agent links as a "WhatsApp Web" device to your account.

**Risks:**
- Linking credentials (QR code / pairing code) must be protected
- Anyone with the linking URI can pair to your account
- Agent sees all messages (not just ones directed at it)

**Mitigations:**
1. Never expose the pairing QR/code publicly
2. Clean up any temp files after linking (`/tmp` artifacts)
3. Use `allowFrom` to restrict which contacts can trigger the agent
4. Regularly audit linked devices in WhatsApp settings
5. Consider a dedicated WhatsApp number for the agent

---

## Implementation Steps

### 1. Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### 2. Create Directory Structure

```bash
mkdir -p ~/openclaw/{config,data,logs}
chmod 700 ~/openclaw
```

### 3. Create Environment File

```bash
cat > ~/openclaw/config/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)
EOF
chmod 600 ~/openclaw/config/.env
```

### 4. Create Docker Compose (Hardened)

```yaml
# ~/openclaw/docker-compose.yml
version: '3.8'
services:
  openclaw:
    image: openclaw:latest
    container_name: openclaw
    restart: unless-stopped
    user: "${UID}:${GID}"
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    environment:
      - NODE_ENV=production
    env_file:
      - ./config/.env
    volumes:
      - ./data:/home/openclaw/.openclaw:rw
      - ./logs:/var/log/openclaw:rw
    ports:
      - "127.0.0.1:18789:18789"  # localhost ONLY
    tmpfs:
      - /tmp:size=100M,mode=1777
```

### 5. Create OpenClaw Configuration

```json
// ~/openclaw/data/openclaw.json
{
  "gateway": {
    "port": 18789,
    "auth": {
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    }
  },
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "all",
        "scope": "session",
        "workspace": "ro"
      }
    }
  },
  "exec": {
    "security": "allowlist",
    "ask": "on-miss"
  },
  "logging": {
    "level": "info",
    "consoleLevel": "warn",
    "redactSensitive": "tools",
    "redactPatterns": ["sk-.*", "pat_.*", "Bearer.*"],
    "file": "/var/log/openclaw/openclaw.log"
  },
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1234567890"],  // Your number only
      "enabled": true
    }
  }
}
```

### 6. WhatsApp Setup (Careful!)

```bash
# Start OpenClaw
docker-compose up -d

# Link WhatsApp - DO THIS IN A PRIVATE TERMINAL
# The QR code will appear - scan with your phone
openclaw channel link whatsapp

# IMMEDIATELY after linking, verify no temp files leaked:
ls -la /tmp | grep -i whatsapp
# If any files exist, delete them:
rm -f /tmp/*whatsapp* /tmp/*qr* /tmp/*link*
```

### 7. Tailscale Access (For Remote Access)

```bash
# Expose gateway via Tailscale (optional, for phone access)
tailscale serve --bg localhost:18789

# Your gateway is now accessible at:
# https://your-machine-name.tailnet-name.ts.net:18789
# Only from devices on your Tailscale network
```

---

## Verification Checklist

- [ ] Gateway only listens on localhost: `ss -tlnp | grep 18789`
- [ ] Docker running as non-root: `docker exec openclaw whoami`
- [ ] Auth token required: Test connection without token fails
- [ ] `openclaw doctor` passes
- [ ] Logs don't contain raw API keys: `grep -r "sk-ant" ~/openclaw/logs/`
- [ ] WhatsApp linked devices audited in phone settings
- [ ] No temp files with credentials: `ls /tmp | grep -i whatsapp`
- [ ] Tailscale device list is only your devices: `tailscale status`

---

## Files to Create

| File | Purpose |
|------|---------|
| `~/openclaw/docker-compose.yml` | Hardened container config |
| `~/openclaw/config/.env` | API key and gateway token |
| `~/openclaw/data/openclaw.json` | Main configuration |

---

## Notes

- **Dev/testing setup**: When moving to production, consider VPS + encrypted backups
- **WhatsApp linking**: The QR code is equivalent to full account access—protect it
- **Allowlist mode**: Safest default. Unknown tools prompt for approval.
- **Tailscale**: Optional for local-only use, but enables phone access to gateway

---

## Post-Setup Maintenance

```bash
# Check health
openclaw doctor --deep

# View logs
tail -f ~/openclaw/logs/openclaw.log | jq

# Update
docker pull openclaw:latest
docker-compose down && docker-compose up -d

# Audit WhatsApp linked devices
# (Do this in WhatsApp on your phone: Settings → Linked Devices)
```

---

## The Unsolved Problem: Perception Attacks

When an AI agent mediates your communications, an attacker who compromises the agent can modify what you see. You think you're having a normal conversation; they're editing in the middle.

**This is an open problem.** Possible directions:
- Out-of-band verification for high-stakes actions
- Cryptographic signing of messages at source
- Secondary channel confirmation
- Audit log that's write-only (agent can't modify its own trail)

---

*"The butler is brilliant. Just make sure he remembers to lock the door."*
