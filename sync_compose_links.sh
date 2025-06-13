#!/usr/bin/env bash
set -e

echo -e "\n🧩 Đồng bộ các file compose..."

# Hỏi thông tin nếu không lấy từ .env
read -rp "Nhập tên HOSTNAME (ví dụ: udms): " HOSTNAME
read -rp "Nhập đường dẫn DOCKERDIR (ví dụ: /home/docker): " DOCKERDIR

SOURCE_DIR="./compose"
DEST_DIR="$DOCKERDIR/compose/$HOSTNAME"

# Kiểm tra folder compose có tồn tại không
if [ ! -d "$SOURCE_DIR" ]; then
  echo "❌ Không tìm thấy thư mục $SOURCE_DIR, hãy chạy từ root dự án!"
  exit 1
fi

# Duyệt từng file .yml trong ./compose
echo -e "\n🔗 Tạo symlink cho các file *.yml..."
for file in "$SOURCE_DIR"/*.yml; do
  [ -e "$file" ] || continue
  base=$(basename "$file")
  target="$DEST_DIR/$base"

  # Nếu đã link đúng thì bỏ qua
  if [ -L "$target" ] && [ "$(readlink -f "$target")" == "$(realpath "$file")" ]; then
    echo "✅ Đã tồn tại đúng: $target"
  else
    ln -sf "$(realpath "$file")" "$target"
    echo "🔗 Đã link: $base → $DEST_DIR/"
  fi
done

echo -e "\n✅ Đồng bộ hoàn tất!"

