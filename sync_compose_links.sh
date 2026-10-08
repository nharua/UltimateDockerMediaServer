#!/usr/bin/env bash
set -e

echo -e "\n🧩 Syncing compose files..."

# Prompt for info if not loaded from .env
read -rp "Enter HOSTNAME (e.g., udms): " HOSTNAME
read -rp "Enter DOCKERDIR path (e.g., /home/docker): " DOCKERDIR

SOURCE_DIR="./compose"
DEST_DIR="$DOCKERDIR/compose/$HOSTNAME"

# Check if compose directory exists
if [ ! -d "$SOURCE_DIR" ]; then
  echo "❌ Directory $SOURCE_DIR not found, please run from project root!"
  exit 1
fi

# Loop through each .yml file in ./compose
echo -e "\n🔗 Creating symlinks for *.yml files..."
for file in "$SOURCE_DIR"/*.yml; do
  [ -e "$file" ] || continue
  base=$(basename "$file")
  target="$DEST_DIR/$base"

  # Skip if symlink is already correct
  if [ -L "$target" ] && [ "$(readlink -f "$target")" == "$(realpath "$file")" ]; then
    echo "✅ Already linked correctly: $target"
  else
    ln -sf "$(realpath "$file")" "$target"
    echo "🔗 Linked: $base → $DEST_DIR/"
  fi
done

echo -e "\n✅ Sync completed!"

