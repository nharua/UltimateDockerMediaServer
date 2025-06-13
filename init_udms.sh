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

echo -e "\n📁 Tạo các thư mục dữ liệu trong DATADIR..."
DATA_FOLDERS=(
  "$DATADIR/media/books"
  "$DATADIR/media/movies"
  "$DATADIR/media/music"
  "$DATADIR/media/m_music"
  "$DATADIR/media/tv"
  "$DATADIR/media/pictures"
  "$DATADIR/torrents/books"
  "$DATADIR/torrents/movies"
  "$DATADIR/torrents/music"
  "$DATADIR/torrents/m_music"
  "$DATADIR/torrents/tv"
  "$DATADIR/usenet/incomplete"
  "$DATADIR/usenet/complete/books"
  "$DATADIR/usenet/complete/movies"
  "$DATADIR/usenet/complete/music"
  "$DATADIR/usenet/complete/m_music"
  "$DATADIR/usenet/complete/tv"
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

