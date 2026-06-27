# 01 - Provision a Hostinger VPS

This is the supporting material for the video: 01 - Provision a Hostinger VPS.

Reference for getting a Linux box stood up that the agents will run on.

## Why a VPS, not your laptop

Agents on your laptop only run when your laptop is on, run as you, and aren't accessible to anyone else. A VPS is always on, network-reachable, and shareable with your team. That's the whole point of treating agents as team members instead of personal assistants.

## Why Hostinger

Their KVM VPS plans hit a good sweet spot: cheap entry tier, decent specs, simple control panel (hPanel), Ubuntu 24.04 available, SSH key management built in.

Comparable alternatives: [Hetzner](https://www.hetzner.com/cloud/) (cheapest, EU-based), [DigitalOcean](https://www.digitalocean.com/) (best documentation), [Linode](https://www.linode.com/). Anything KVM-based on Ubuntu 24.04 works; the rest of this runbook is provider-agnostic from step 2 onwards.

## Pick a plan

For a small team running a handful of agents:

- **KVM 1** - entry tier, 1 vCPU, 4 GB RAM. Enough to start.
- **KVM 2** - 2 vCPU, 8 GB RAM. More headroom for parallel agent runs.

Start with KVM 1. Upgrade if you hit memory pressure once you're running multiple agents in parallel.

## Provision steps (Hostinger)

1. Sign in to Hostinger → hPanel → VPS → Get VPS
2. Pick a plan (KVM 1 or 2)
3. Datacenter: pick one close to where you live (latency to your VPS during setup matters more than to your users)
4. **Operating system**: Ubuntu 24.04 LTS (clean install, no panels)
5. **Hostname**: something memorable, e.g. `agents-vps`
6. **Root password**: set one, but you'll mostly use SSH keys
7. **SSH key**: upload your public key. If you don't have one yet:
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   cat ~/.ssh/id_ed25519.pub  # paste this into Hostinger's SSH key field
   ```
8. Confirm and let Hostinger provision (~1-2 minutes)
9. Note the public IP from hPanel → VPS → Overview

## First connection

```bash
ssh root@<your-vps-ip>
```

Should land you at a `root@` prompt. If it doesn't, your SSH key wasn't added correctly - check Hostinger's SSH Keys panel.

## Basic hardening (do this once)

```bash
# Update packages
apt update && apt upgrade -y

# Install ufw firewall
apt install -y ufw

# Allow SSH only (we'll add ports for Multica later)
ufw allow OpenSSH
ufw enable
ufw status

# Create a non-root user
adduser owain
usermod -aG sudo owain

# Copy your SSH key to the new user
mkdir -p /home/owain/.ssh
cp ~/.ssh/authorized_keys /home/owain/.ssh/
chown -R owain:owain /home/owain/.ssh
chmod 700 /home/owain/.ssh
chmod 600 /home/owain/.ssh/authorized_keys
```

From now on, SSH as your non-root user:

```bash
ssh owain@<your-vps-ip>
```

## Install base tooling

```bash
sudo apt install -y git curl python3 python3-pip ffmpeg

# Node.js LTS (for Claude Code)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# gh CLI (for Git operations)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
  sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
  sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install -y gh
```

Verify:

```bash
git --version
node --version
python3 --version
uv --version
gh --version
```

## Critical: there is no browser on the VPS

Anything that wants to open a browser for OAuth (Claude Code login, MCP servers like Notion, gh auth login without `--with-token`) will print a URL and a code to your terminal instead. You **copy the URL from the VPS terminal into your local browser**, complete the auth flow, and then **copy any token or code back into the VPS terminal**.

This is normal headless-OAuth flow. It bites everyone the first time. The next step covers the dance for Claude Code in detail.

## Next

[02 - Install Claude Code](../02-claude-code/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
