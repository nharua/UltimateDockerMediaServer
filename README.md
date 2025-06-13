# 🎬 Ultimate Docker Media Server (UDMS)

**Ultimate Docker Media Server** is a homelab project that allows you to deploy your own media server system at home using Docker Compose. The system includes complete components for managing, monitoring, streaming, and downloading digital content — all managed through independent containers that are easy to scale and maintain.
This project is based on the [Docker Media Server](https://www.simplehomelab.com/docker-media-server-2024/) project, with the goal of simplifying the deployment process and providing a standardized folder structure for easy management.

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

**2. Media Services**
| Service   | Description           |
|-----------|-----------------------|
| `jellyfin`| Open-source media server for streaming movies/music |

**3. Downloader Services**
| Service       | Description                      |
|---------------|----------------------------------|
| `qbittorrent` | Torrent client with web interface |

---

## 📁 Directory Structure (after running `init_udms.sh`)
```yaml
DOCKERDIR/
├── appdata/
│ └── jellyfin/
├── compose/
│ └── udms/
│   ├── socket-proxy.yml
│   ├── portainer.yml
│   ├── dozzle.yml
│   ├── homepage.yml
│   ├── jellyfin.yml
│   └── qbittorrent.yml
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

- **Jellyfin**: [http://localhost:8096](http://localhost:8096)
- **Portainer**: [http://localhost:9000](http://localhost:9000)
- **Dozzle**: [http://localhost:8082](http://localhost:8082)
- **Homepage Dashboard**: [http://localhost:3000](http://localhost:3000)
- **qBittorrent Web UI**: [http://localhost:8081](http://localhost:8081)

> Default ports can be changed in the respective compose YAML files under `compose/udms/`.

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
```

