#!/bin/bash
set -euo pipefail

# Wait for cloud-init to settle
sleep 5

# Install Docker
apt-get update && apt-get upgrade -y
apt-get install -y ca-certificates curl git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add ubuntu to docker group
usermod -aG docker ubuntu

# Clone repo if not present
mkdir -p /home/ubuntu/apps
if [ ! -d "${app_dir}" ]; then
  git clone --branch "${branch}" "${repo_url}" "${app_dir}"
else
  cd "${app_dir}" && git fetch --all && git checkout "${branch}" && git pull origin "${branch}" || true
fi
chown -R ubuntu:ubuntu /home/ubuntu/apps

# Create .env if example exists
if [ ! -f "${app_dir}/.env" ] && [ -f "${app_dir}/.env.example" ]; then
  cp "${app_dir}/.env.example" "${app_dir}/.env"
  chown ubuntu:ubuntu "${app_dir}/.env"
fi

# Enable and start Docker (it will be active for next sessions)
systemctl enable docker || true
