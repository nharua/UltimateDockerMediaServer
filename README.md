# 🎬 Ultimate Docker Media Server (UDMS)

**Ultimate Docker Media Server** is a homelab project that allows you to deploy your own media server system at home using Docker Compose. The system includes complete components for managing, monitoring, streaming, and downloading digital content — all managed through independent containers that are easy to scale and maintain.


This project is based on the [Docker Media Server](https://www.simplehomelab.com/docker-media-server-2024/) project, with the goal of simplifying the deployment process and providing a standardized folder structure for easy management.

---
## 🔧 Configuration Tips

### Initial Setup Order
1. **Start with Core Services**: Ensure Portainer, Dozzle, and Homepage are running first
2. **Configure Download Clients**: Set up qBittorrent and SABnzbd with proper download directories
3. **Configure Indexers**: Set up Prowlarr to sync indexers to Radarr, Sonarr, Lidarr, Readarr
4. **Set up PVR Services**: Configure Radarr and Sonarr to use your download clients and indexers
5. **Add Subtitle Management**: Configure Bazarr+ to work with Radarr and Sonarr; set FlareSolverr (`http://flaresolverr:8191/v1`) for OpenSubtitles Provider Hub plugin
6. **Configure Media Server**: Point Jellyfin to your organized media directories

### Common Configuration
- **Download Paths**: Configure consistent paths across all services (e.g., `/data/downloads`, `/data/usenet`)
- **Media Paths**: Ensure all services can access the same media directories (e.g., `/data/movies`, `/data/tv`)
- **User Permissions**: Make sure PUID and PGID are consistent across all services in your `.env` file

---

## 🚀 Project Goals

- Simplify media server deployment with a single script
- Clear, standardized folder structure
- Easy integration and addition of other services
- Suitable for individuals, families, or homelab environments

---

## 🧩 System Components

**1. Core Services**
| Service       | Description                   |
|---------------|-------------------------------|
| `socket-proxy`| Secure reverse proxy for Docker socket |
| `portainer`   | Docker container management interface |
| `dozzle`      | Real-time container log monitoring |
| `homepage`    | Dashboard displaying all services |

**2. Indexers**
| Service   | Description           |
|-----------|-----------------------|
| `prowlarr`| Indexer manager for Usenet and BitTorrent |

**3. Media Services**
| Service   | Description           |
|-----------|-----------------------|
| `jellyfin`| Open-source media server for streaming movies/music |

**4. Downloader Services**
| Service       | Description                      |
|---------------|----------------------------------|
| `qbittorrent` | Torrent client with web interface |
| `sabnzbd`     | Usenet newsgroup downloader with web interface |

**5. PVR Services (Personal Video Recorder)**
| Service   | Description           |
|-----------|-----------------------|
| `radarr`  | Movie collection manager for Usenet and BitTorrent users |
| `sonarr`  | TV series collection manager for Usenet and BitTorrent users |
| `lidarr`  | Music collection manager |
| `readarr` | Book and audiobook collection manager |

**6. Complementary Apps**
| Service       | Description           |
|---------------|-----------------------|
| `bazarr`      | Subtitle management for Radarr and Sonarr ([Bazarr+](https://lavx.github.io/bazarr/)) |
| `flaresolverr`| Proxy server to bypass Cloudflare protection for subtitle/indexer scrapers |

**7. Photo Management**
| Service   | Description           |
|-----------|-----------------------|
| `immich`  | High-performance self-hosted photo and video management solution |

**8. Utilities**
| Service       | Description                      |
|---------------|----------------------------------|
| `filebrowser` | Web-based file manager with sharing capabilities |

**9. Networking & DNS**
| Service    | Description           |
|------------|-----------------------|
| `twingate` | Zero Trust Network Access (ZTNA) connector |
| `pihole`   | Network-wide ad and tracker blocking via DNS sinkholing |
| `unbound`  | Validating, recursive, and caching DNS resolver |

**10. Maintenance**
| Service    | Description           |
|------------|-----------------------|
| `docker-gc`| Docker garbage collection for cleanup |

---

## 📁 Directory Structure (after running `init_udms.sh`)
```yaml
DOCKERDIR/
├── appdata/
│   ├── bazarr/
│   ├── jellyfin/
│   ├── prowlarr/
│   ├── radarr/
│   ├── sonarr/
│   └── ...
├── compose/
│   └── <HOSTNAME>/
│       ├── bazarr.yml
│       ├── dozzle.yml
│       ├── homepage.yml
│       ├── jellyfin.yml
│       ├── portainer.yml
│       ├── prowlarr.yml
│       ├── qbittorrent.yml
│       ├── radarr.yml
│       ├── socket-proxy.yml
│       ├── sonarr.yml
│       └── ...
├── logs/
├── scripts/
├── secrets/
├── shared/
├── .env
├── docker-compose-udms.yml <- symlink

DATADIR/
├── media/
│   ├── books/
│   ├── movies/
│   ├── music/
│   ├── pictures/
│   └── tv/
└── downloads/
```

## 🛠️ System Requirements

- **Operating System**: Linux
- **RAM**: ≥ 4GB (recommended ≥ 8GB if using transcoding)
- **Software**: `docker`, `docker-compose`, `setfacl`, `bash`
- **Permissions**: Account with `sudo` privileges

---

## 📦 Installation & Deployment

### Step 1: Clone the repository
```bash
git clone https://github.com/nharua/UltimateDockerMediaServer.git
cd UltimateDockerMediaServer
```

### Step 2: Grant execution permissions to the script
```bash
chmod +x init_udms.sh
```

### Step 3: Run the initialization script
```bash
./init_udms.sh
```

### Step 4: Run Docker Compose
```bash
cd $DOCKERDIR
sudo docker-compose -f docker-compose-udms.yml up -d
```

---
## 🌐 Accessing Your Services

After deployment, you can access your media server and management interfaces using the following default URLs (replace `localhost` with your server's IP if accessing remotely):

- **Homepage Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Jellyfin**: [http://localhost:8096](http://localhost:8096)
- **Portainer**: [http://localhost:9000](http://localhost:9000)
- **Dozzle**: [http://localhost:9999](http://localhost:9999)
- **qBittorrent Web UI**: [http://localhost:8081](http://localhost:8081)
- **Prowlarr**: [http://localhost:9696](http://localhost:9696)
- **Radarr**: [http://localhost:7878](http://localhost:7878)
- **Sonarr**: [http://localhost:8989](http://localhost:8989)
- **Lidarr**: [http://localhost:8686](http://localhost:8686)
- **Readarr**: [http://localhost:8787](http://localhost:8787)
- **Bazarr+**: [http://localhost:6767](http://localhost:6767)
- **FlareSolverr**: [http://localhost:8191](http://localhost:8191)
- **FileBrowser**: [http://localhost:8080](http://localhost:8080)
- **Immich**: [http://localhost:2283](http://localhost:2283)

> [!TIP]
> - Trong Bazarr+, cấu hình FlareSolverr URL trong plugin Provider Hub (OpenSubtitles.org) là `http://flaresolverr:8191/v1`.
> - Default ports và IP có thể tùy chỉnh trong file `.env` được tạo bởi `init_udms.sh`.

---
## ❓ Troubleshooting & FAQ

- **Permission Errors**: Ensure your user has `sudo` privileges and that Docker is installed correctly.
- **Port Conflicts**: If a service fails to start, check if the required port is already in use and adjust the port mapping in the relevant YAML file.
- **Directory Issues**: Make sure the `DOCKERDIR` and `DATADIR` directories exist and have the correct permissions.
- **Environment Variables**: Verify that the `.env` file is present and properly configured.
- **Service Not Accessible**: Check Docker container logs using `sudo docker ps` and `sudo docker logs <container_name>` for error messages.

For more help, please open an issue on the project's GitHub page.

---
## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
## 🤝 Contributions

Contributions are welcome! Please open issues or submit pull requests via GitHub. For major changes, open an issue first to discuss what you would like to change.
