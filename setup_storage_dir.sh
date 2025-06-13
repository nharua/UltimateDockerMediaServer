#!/bin/bash

# Đặt thư mục gốc
ROOT_DIR="./data"

# Danh sách thư mục con cần tạo
DIRS=(
  "$ROOT_DIR/torrents/books"
  "$ROOT_DIR/torrents/movies"
  "$ROOT_DIR/torrents/music"
  "$ROOT_DIR/torrents/tv"
  "$ROOT_DIR/usenet/incomplete"
  "$ROOT_DIR/usenet/complete/books"
  "$ROOT_DIR/usenet/complete/movies"
  "$ROOT_DIR/usenet/complete/music"
  "$ROOT_DIR/usenet/complete/tv"
  "$ROOT_DIR/media/books"
  "$ROOT_DIR/media/movies"
  "$ROOT_DIR/media/music"
  "$ROOT_DIR/media/tv"
  "$ROOT_DIR/media/pictures"
)

# Tạo các thư mục
for dir in "${DIRS[@]}"; do
  mkdir -p "$dir"
done

# Cấp quyền chmod và ACL
sudo chmod 775 "$ROOT_DIR"
sudo setfacl -Rdm u:$USER:rwx "$ROOT_DIR"
sudo setfacl -Rm u:$USER:rwx "$ROOT_DIR"
sudo setfacl -Rdm g:docker:rwx "$ROOT_DIR"
sudo setfacl -Rm g:docker:rwx "$ROOT_DIR"

echo "✅ Thư mục đã được tạo và phân quyền thành công."

