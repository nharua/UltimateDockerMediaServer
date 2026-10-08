#!/bin/bash

# Set root directory
ROOT_DIR="./data"

# List of subdirectories to create
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

# Create directories
for dir in "${DIRS[@]}"; do
  mkdir -p "$dir"
done

# Set chmod and ACL permissions
sudo chmod 775 "$ROOT_DIR"
sudo setfacl -Rdm u:$USER:rwx "$ROOT_DIR"
sudo setfacl -Rm u:$USER:rwx "$ROOT_DIR"
sudo setfacl -Rdm g:docker:rwx "$ROOT_DIR"
sudo setfacl -Rm g:docker:rwx "$ROOT_DIR"

echo "✅ Directories created and permissions set successfully."

