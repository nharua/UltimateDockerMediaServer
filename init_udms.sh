#!/usr/bin/env bash
set -e

# Prompt user for input
read -rp "Nhập đường dẫn DOCKERDIR (ví dụ: /home/docker): " DOCKERDIR
read -rp "Nhập đường dẫn DATADIR (ví dụ: /home/storage): " DATADIR
read -rp "Nhập tên HOSTNAME (ví dụ: udms): " HOSTNAME

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

echo -e "\n📁 Tạo các thư mục trong DOCKERDIR..."
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
    echo "✅ Đã tồn tại: $folder"
  else
    sudo mkdir -p "$folder"
    sudo chown "$USERID:$GROUPID" "$folder"
    echo "📁 Đã tạo: $folder"
  fi
done

echo -e "\n📝 Tạo file rỗng docker-gc-exclude tại $DOCKERDIR/appdata/docker-gc/ ..."
sudo touch "$DOCKERDIR/appdata/docker-gc/docker-gc-exclude"
sudo chown "$USERID:$GROUPID" "$DOCKERDIR/appdata/docker-gc/docker-gc-exclude"

echo -e "\n📁 Tạo các thư mục dữ liệu trong DATADIR..."
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
    echo "✅ Đã tồn tại: $folder"
  else
    sudo mkdir -p "$folder"
    sudo chown "$USERID:$GROUPID" "$folder"
    echo "📁 Đã tạo: $folder"
  fi
done

echo -e "\n🔐 Thiết lập quyền ACL cho $DATADIR ..."
sudo chmod 775 "$DATADIR"
sudo setfacl -Rdm u:$USERNAME:rwx "$DATADIR"
sudo setfacl -Rm u:$USERNAME:rwx "$DATADIR"
sudo setfacl -Rdm g:docker:rwx "$DATADIR"
sudo setfacl -Rm g:docker:rwx "$DATADIR"

echo -e "\n🔐 Thiết lập quyền ACL cho $DOCKERDIR ..."
sudo chmod 775 "$DOCKERDIR"
sudo setfacl -Rdm u:$USERNAME:rwx "$DOCKERDIR"
sudo setfacl -Rm u:$USERNAME:rwx "$DOCKERDIR"
sudo setfacl -Rdm g:docker:rwx "$DOCKERDIR"
sudo setfacl -Rm g:docker:rwx "$DOCKERDIR"

echo -e "\n📝 Tạo file .env tại $DOCKERDIR/.env ..."
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
# FileBrowser
FILEBROWSER_PORT="8080"
FILEBROWSER_IP="192.168.90.208"

# Jellyfin Transcode Config
TRANSCODE=$TRANSCODE
EOF

# Phân quyền đặc biệt cho secrets và .env
sudo chown root:root "$DOCKERDIR/secrets"
sudo chmod 600 "$DOCKERDIR/secrets"
sudo chown root:root "$DOCKERDIR/.env"
sudo chmod 600 "$DOCKERDIR/.env"

echo -e "\n🔗 Tạo symlink docker-compose-udms.yml → $DOCKERDIR/docker-compose-udms.yml ..."
if [ -f "./docker-compose-udms.yml" ]; then
  ln -sf "$(realpath ./docker-compose-udms.yml)" "$DOCKERDIR/docker-compose-udms.yml"
  echo "✅ Symlink đã tạo"
else
  echo "⚠️ Không tìm thấy docker-compose-udms.yml!"
fi

echo -e "\n🔗 Tạo symlink các file compose/*.yml → $DOCKERDIR/compose/$HOSTNAME/"
if [ -d "./compose" ]; then
  for file in ./compose/*.yml; do
    [ -e "$file" ] || continue
    ln -sf "$(realpath "$file")" "$DOCKERDIR/compose/$HOSTNAME/"
    echo "🔗 Linked: $file → $DOCKERDIR/compose/$HOSTNAME/"
  done
else
  echo "⚠️ Không tìm thấy thư mục ./compose"
fi

echo -e "\n✅ Hoàn tất!"

