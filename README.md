# 🎬 Ultimate Docker Media Server (UDMS)

**Ultimate Docker Media Server** là một dự án homelab cho phép bạn tự triển khai hệ thống media server tại nhà bằng Docker Compose. Hệ thống bao gồm đầy đủ các thành phần quản lý, theo dõi, phát và tải nội dung số — tất cả đều được quản lý qua các container độc lập, dễ mở rộng và bảo trì.

---

## 🚀 Mục tiêu của dự án

- Đơn giản hóa việc triển khai media server với một script duy nhất
- Cấu trúc folder rõ ràng, chuẩn hóa
- Dễ dàng tích hợp và thêm các dịch vụ khác
- Phù hợp cho cá nhân, gia đình hoặc homelab

---

## 🧩 Thành phần hệ thống

**1. Core Services**
| Service       | Mô tả                         |
|---------------|-------------------------------|
| `socket-proxy`| Reverse proxy bảo mật cho Docker socket |
| `portainer`   | Giao diện quản lý container Docker |
| `dozzle`      | Theo dõi logs các container theo thời gian thực |
| `homepage`    | Trang dashboard hiển thị toàn bộ dịch vụ |

**2. Media Services**
| Service   | Mô tả             |
|-----------|-------------------|
| `jellyfin`| Media server mã nguồn mở, stream phim/nhạc |

**3. Downloader Services**
| Service       | Mô tả                            |
|---------------|----------------------------------|
| `qbittorrent` | Trình tải torrent có giao diện web |

---

## 📁 Cấu trúc thư mục (sau khi chạy `init_udms.sh`)
```yaml
DOCKERDIR/
├── appdata/
│ └── jellyfin/
├── compose/
│ └── udms/
│ ├── socket-proxy.yml
│ ├── portainer.yml
│ ├── dozzle.yml
│ ├── homepage.yml
│ ├── jellyfin.yml
│ └── qbittorrent.yml
├── logs/
├── scripts/
├── secrets/
├── shared/
├── .env
├── docker-compose-udms.yml <- symlink

DATADIR/
├── media/
│ ├── movies/
│ ├── tv/
│ └── ...
├── torrents/
│ └── ...
└── usenet/
└── ...
```

## 🛠️ Yêu cầu hệ thống

- **Hệ điều hành**: Linux
- **RAM**: ≥ 4GB (khuyến nghị ≥ 8GB nếu dùng transcoding)
- **Phần mềm**: `docker`, `docker-compose`, `setfacl`, `bash`
- **Quyền**: Tài khoản có quyền `sudo`

---

## 📦 Cài đặt & Triển khai

### Bước 1: Clone repo
```bash
git clone <repo_url>
cd UltimateDockerMediaServer
```
### Bước 2: Cấp quyền thực thi cho script
```bash
chmod +x init_udms.sh
```
### Bước 3: Chạy script khởi tạo
```bash
./init_udms.sh
```
### Bước 4: Chạy Docker Compose
```bash
cd $DOCKERDIR
sudo docker-compose -f docker-compose-udms.yml up -d
```

