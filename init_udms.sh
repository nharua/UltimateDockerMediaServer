#!/usr/bin/env bash
set -e

# Prompt user for input
read -rp "Enter DOCKERDIR path (e.g., /home/docker): " DOCKERDIR
read -rp "Enter DATADIR path (e.g., /home/storage): " DATADIR
read -rp "Enter HOSTNAME (e.g., udms): " HOSTNAME

# Resolve user info
USERID=$(id -u)
GROUPID=$(id -g)
USERNAME=$(id -un)
USERDIR=$HOME
TZ="Asia/Ho_Chi_Minh"

# Check RAM
TOTAL_RAM_GB=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
if [ "$TOTAL_RAM_GB" -ge 8 ]; then
  TRANSCODE="/dev/shm"
else
  TRANSCODE="$DOCKERDIR/appdata/transcode"
fi

echo -e "\n📁 Creating directories in DOCKERDIR..."
DOCKER_FOLDERS=(
  "$DOCKERDIR/appdata/jellyfin"
  "$DOCKERDIR/appdata/docker-gc"
  "$DOCKERDIR/compose/$HOSTNAME"
  "$DOCKERDIR/logs"
  "$DOCKERDIR/scripts"
  "$DOCKERDIR/secrets"
  "$DOCKERDIR/shared"
)

for folder in "${DOCKER_FOLDERS[@]}"; do
  if [ -d "$folder" ]; then
    echo "✅ Already exists: $folder"
  else
    sudo mkdir -p "$folder"
    sudo chown "$USERID:$GROUPID" "$folder"
    echo "📁 Created: $folder"
  fi
done

echo -e "\n📝 Creating empty docker-gc-exclude file at $DOCKERDIR/appdata/docker-gc/ ..."
sudo touch "$DOCKERDIR/appdata/docker-gc/docker-gc-exclude"
sudo chown "$USERID:$GROUPID" "$DOCKERDIR/appdata/docker-gc/docker-gc-exclude"

echo -e "\n📁 Creating data directories in DATADIR..."
DATA_FOLDERS=(
  "$DATADIR/media/books"
  "$DATADIR/media/movies"
  "$DATADIR/media/music"
  "$DATADIR/media/m_music"
  "$DATADIR/media/tv"
  "$DATADIR/media/pictures"
  "$DATADIR/downloads"
)

for folder in "${DATA_FOLDERS[@]}"; do
  if [ -d "$folder" ]; then
    echo "✅ Already exists: $folder"
  else
    sudo mkdir -p "$folder"
    sudo chown "$USERID:$GROUPID" "$folder"
    echo "📁 Created: $folder"
  fi
done

echo -e "\n🔐 Setting ACL permissions for $DATADIR ..."
sudo chmod 775 "$DATADIR"
sudo setfacl -Rdm u:$USERNAME:rwx "$DATADIR"
sudo setfacl -Rm u:$USERNAME:rwx "$DATADIR"
sudo setfacl -Rdm g:docker:rwx "$DATADIR"
sudo setfacl -Rm g:docker:rwx "$DATADIR"

echo -e "\n🔐 Setting ACL permissions for $DOCKERDIR ..."
sudo chmod 775 "$DOCKERDIR"
sudo setfacl -Rdm u:$USERNAME:rwx "$DOCKERDIR"
sudo setfacl -Rm u:$USERNAME:rwx "$DOCKERDIR"
sudo setfacl -Rdm g:docker:rwx "$DOCKERDIR"
sudo setfacl -Rm g:docker:rwx "$DOCKERDIR"

echo -e "\n📝 Creating .env file at $DOCKERDIR/.env ..."
cat <<EOF | sudo tee "$DOCKERDIR/.env" > /dev/null
PUID=$USERID
PGID=$GROUPID
TZ="$TZ"
USERDIR="$USERDIR"
DOCKERDIR="$DOCKERDIR"
DATADIR="$DATADIR"
HOSTNAME="$HOSTNAME"

# Socket Service
SOCKET_IP="192.168.91.254"

# Portainer
PORTAINER_PORT="9000"
PORTAINER_SOCKET_IP="192.168.91.253"

# Dozzle 
DOZZLE_PORT="9999"
DOZZLE_SOCKET_IP="192.168.91.252"
DOZZLE_IP="192.168.90.252"

# Homepage dashboard
HOMEPAGE_PORT="3000"
HOMEPAGE_SOCKET_IP="192.168.91.251"
HOMEPAGE_IP="192.168.90.251"

# Prowlarr
PROWLARR_PORT="9696"
PROWLARR_IP="192.168.90.200"

# Jellyfin
JELLYFIN_PORT="8096"
JELLYFIN_IP="192.168.90.201"

# qBittorrent
QBITTORRENT_PORT="8081"
QBITTORRENT_IP="192.168.90.202"

# Radarr
RADARR_PORT="7878"
RADARR_IP="192.168.90.203"

# Sonarr
SONARR_PORT="8989"
SONARR_IP="192.168.90.204"

# Lidarr
LIDARR_PORT="8686"
LIDARR_IP="192.168.90.205"

# Readarr
READARR_PORT="8787"
READARR_IP="192.168.90.206"

# Bazarr
BAZARR_PORT="6767"
BAZARR_IP="192.168.90.207"

# FlareSolverr
FLARESOLVERR_PORT="8191"
FLARESOLVERR_IP="192.168.90.209"

# FileBrowser
FILEBROWSER_PORT="8080"
FILEBROWSER_IP="192.168.90.208"

# Immich server
IMMICH_VERSION=release
IMMICH_IP=192.168.90.213
IMMICH_PORT=2283

# Machine Learning
IMMICH_ML_IP=192.168.90.217

# Database
IMMICH_DB_IP=192.168.90.214
IMMICHDB_POSTGRESQL_PASSWORD=your-postgresql-password

# Redis
IMMICH_REDIS_IP=192.168.90.218
REDIS_PORT=6379

# TWINGATE
TWINGATE_NETWORK=nharua
TWINGATE_CONNECTOR=your-connector-name
TWINGATE_ACCESS_TOKEN=your-access-token
TWINGATE_REFRESH_TOKEN=your-refresh-token
TWINGATE_IP=192.168.100.7

# UNBOUND
UNBOUND_IP=192.168.100.36

# PIHOLE
PIHOLE_IP=192.168.100.35
PIHOLE_WEB_PW=your-pihole-web-password

# Jellyfin Transcode Config
TRANSCODE=$TRANSCODE
EOF

# Special permissions for secrets and .env
sudo chown root:root "$DOCKERDIR/secrets"
sudo chmod 600 "$DOCKERDIR/secrets"
sudo chown root:root "$DOCKERDIR/.env"
sudo chmod 600 "$DOCKERDIR/.env"

echo -e "\n🔗 Creating symlink docker-compose-udms.yml → $DOCKERDIR/docker-compose-udms.yml ..."
if [ -f "./docker-compose-udms.yml" ]; then
  ln -sf "$(realpath ./docker-compose-udms.yml)" "$DOCKERDIR/docker-compose-udms.yml"
  echo "✅ Symlink created"
else
  echo "⚠️ docker-compose-udms.yml not found!"
fi

echo -e "\n🔗 Creating symlinks for compose/*.yml → $DOCKERDIR/compose/$HOSTNAME/"
if [ -d "./compose" ]; then
  for file in ./compose/*.yml; do
    [ -e "$file" ] || continue
    ln -sf "$(realpath "$file")" "$DOCKERDIR/compose/$HOSTNAME/"
    echo "🔗 Linked: $file → $DOCKERDIR/compose/$HOSTNAME/"
  done
else
  echo "⚠️ Directory ./compose not found!"
fi

echo -e "\n✅ Completed!"

