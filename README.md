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
- **Media paths**: Configure `MOVIES_DIR`, `TV_DIR`, and `DOWNLOADS_DIR` once with `configure_storage.sh`. Keep `/data/movies`, `/data/tv`, and `/data/downloads` consistent inside the containers.
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

## Directory structure
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

# Default local layout, created separately by configure_storage.sh
DATADIR/
├── media/
│   ├── books/
│   ├── movies/
│   ├── music/
│   ├── pictures/
│   └── tv/
└── downloads/
```

## System requirements

- Linux, Bash, Python 3.9+, and `findmnt` from util-linux.
- Docker Engine and the Docker Compose plugin, v2.20+ with `include` support. Commands below use `docker compose`.
- `setfacl` for the application-data setup in `init_udms.sh`.
- A user with sudo access. Run `init_udms.sh` as your normal login user; it calls sudo where needed.
- Mount NAS shares on the Docker host before configuring storage. Set up persistent mounts through your system's mount configuration.

## Shared storage configuration

The same `.env` variables supply every movie, TV, and download bind mount:

```dotenv
MOVIES_DIR="/mnt/nas/FamilyShare/Movies"
TV_DIR="/mnt/nas/FamilyShare/TVShows"
DOWNLOADS_DIR="/mnt/nas/Download"
PUID=1001
PGID=1001
```

Host folder names can be `Movies`, `TV_Series`, or any other name. Inside the applications, use these paths:

| Application | Library or download path |
|---|---|
| Radarr | `/data/movies`, `/data/downloads` |
| Sonarr | `/data/tv`, `/data/downloads` |
| Bazarr | `/data/movies`, `/data/tv` |
| qBittorrent / optional SABnzbd | `/data/downloads` |
| Jellyfin | `/data/movies`, `/data/tv`, `/t_downloads` |

`configure_storage.sh` asks for each directory, whether it is local or NAS storage, and the shared UID/GID. It saves the NAS mount target, source, and filesystem type for later comparison. On local storage, creating missing directories requires confirmation or `--create-local`. Existing directories keep their ownership and permissions. The script updates only storage settings and UID/GID in `.env`, preserving other variables and creating a private backup beside the file. `.env` and its backups contain secrets and must stay outside version control.

All affected Compose bind mounts use `create_host_path: false`. A missing directory causes an error instead of silently creating an empty library. The storage scripts never mount shares, recursively change media permissions, or restart containers.

## Deploy on a new server

Run these steps in order. Replace `/home/udms` with the `DOCKERDIR` you choose.

### 1. Clone and initialize the application configuration

```bash
git clone https://github.com/nharua/UltimateDockerMediaServer.git
cd UltimateDockerMediaServer
bash ./init_udms.sh
```

Enter absolute `DOCKERDIR` and `DATADIR` paths and a deployment hostname. `DATADIR` remains the default base for other media, such as music, books, and photos. Initialization creates application directories, a base `.env`, and Compose links. It does not create media libraries or alter NAS permissions. It refuses to overwrite an existing `.env`.

### 2. Mount storage, then configure the library paths

For NAS storage, mount the shares on the host first. Verify the actual share before continuing:

```bash
findmnt -T /mnt/nas/FamilyShare/Movies -o TARGET,SOURCE,FSTYPE
findmnt -T /mnt/nas/FamilyShare/TVShows -o TARGET,SOURCE,FSTYPE
findmnt -T /mnt/nas/Download -o TARGET,SOURCE,FSTYPE
sudo bash ./configure_storage.sh --env-file /home/udms/.env
```

Choose `nas` for each directory on a network share. If a share is missing, restore it before running the script. NAS mode rejects a local filesystem at the expected mount location, even if an empty directory exists there.

For a new local disk layout, the interactive script can create the directories after confirmation. The equivalent unattended command is:

```bash
sudo bash ./configure_storage.sh --env-file /home/udms/.env \
  --movies /srv/media/movies --tv /srv/media/tv \
  --downloads /srv/media/downloads --storage-type local \
  --puid 1001 --pgid 1001 --create-local --non-interactive
```

Use the intended host account's UID/GID from `id`, rather than copying `1001` blindly. This account needs access to the storage on the host and through the NAS mount.

### 3. Review the deployment settings and run the preflight check

```bash
sudoedit /home/udms/.env
sudo bash ./check_storage.sh --env-file /home/udms/.env
sudo docker compose --env-file /home/udms/.env \
  -f /home/udms/docker-compose-udms.yml config --quiet
```

Replace placeholder service credentials and review ports, network addresses, the macvlan parent interface in `docker-compose-udms.yml`, and hardware settings such as Jellyfin's `/dev/dri` device. Prepare any additional music, books, or photo directories needed by the other services. The storage checker covers the movie/TV/download pipeline.

The preflight check verifies directories, saved NAS mount identity, read/write access as `PUID:PGID`, and the resolved Compose mounts. It creates and removes small temporary files in the storage roots. It does not need running containers. Fix every `FAIL` before starting the services.

### 4. Start the stack and verify the running containers

```bash
sudo docker compose --env-file /home/udms/.env \
  -f /home/udms/docker-compose-udms.yml up -d
sudo bash ./check_storage.sh --env-file /home/udms/.env --runtime
```

Run the second command once the application processes have started. If they are still starting, wait and rerun it.

The runtime check inspects the actual bind mounts and application UID/GID. It verifies that a file created by Radarr is readable and writable by Bazarr, repeats that check for Sonarr, and tests download sharing between enabled download clients and Radarr/Sonarr. Probe files use unique names and are removed after the check.

### 5. Configure the applications

Set Radarr's root folder to `/data/movies`, Sonarr's to `/data/tv`, and download clients to `/data/downloads`. If both download clients are enabled, use separate subdirectories or categories under that download root. Connect Bazarr to Radarr and Sonarr. Matching container paths normally need no Bazarr path mapping.

For an existing media file, check the exact file and subtitle directory too:

```bash
sudo bash ./check_storage.sh --env-file /home/udms/.env --runtime \
  --sample '/data/movies/Moana (2016)/Moana 2016 720p BluRay DD5.1 x264-LoRD.mkv'
```

The sample check reads the file and creates/removes a probe in its parent directory. It does not modify the movie or existing subtitles. A successful storage check does not verify subtitle-provider credentials or connectivity; retry a subtitle search in Bazarr separately.

## Check or migrate an existing server

Do not rerun `init_udms.sh`. Preserve the current deployment and run these steps from your repository checkout.

### 1. Inspect the active mounts and record the correct library paths

```bash
for service in bazarr radarr sonarr qbittorrent; do
  sudo docker inspect "$service" --format \
    '{{.Name}}{{range .Mounts}}{{println}}{{.Source}} -> {{.Destination}}{{end}}'
done
```

Find the real library on the host, such as `/mnt/nas/FamilyShare/Movies`. A directory that merely exists may be an empty fallback created while the NAS was unmounted. Check its `findmnt` source and confirm it contains the expected media.

### 2. Save the shared paths in the existing environment file

```bash
sudo bash ./configure_storage.sh --env-file /home/udms/.env
```

Enter the actual paths, not an empty default directory. Select NAS/local separately for each root. Existing unrelated `.env` values are preserved. The script does not infer library paths from a running container, so review all three prompts.

### 3. Update the deployed Compose files

The deployed Bazarr, Radarr, Sonarr, and download-client files must use this repository's shared-variable mounts. Compare any server-specific Compose settings before replacing files. Changing `.env` alone cannot fix a Compose file with a hardcoded source path.

If the deployment already uses repository symlinks, the edited templates are used automatically. If it uses copies, merge the template changes while retaining server-specific settings. `sync_compose_links.sh` replaces deployed files with links to this checkout, so use it only after preserving and merging custom settings:

```bash
bash ./sync_compose_links.sh
```

Then run the preflight check:

```bash
sudo bash ./check_storage.sh --env-file /home/udms/.env
```

### 4. Recreate the affected services and run the runtime check

For the default pipeline:

```bash
sudo docker compose --env-file /home/udms/.env \
  -f /home/udms/docker-compose-udms.yml up -d --no-deps \
  bazarr radarr sonarr qbittorrent
sudo bash ./check_storage.sh --env-file /home/udms/.env --runtime
```

Include `sabnzbd` if you enabled it. Recreate other affected services, such as Jellyfin, Lidarr, Readarr, Prowlarr, and FileBrowser, if their media/download sources changed. A plain `restart` does not apply new mount sources or environment variables. Add `--pull never` to the `up` command if you want to retain locally available images.

To investigate one file, repeat the `--runtime --sample` command above using its path inside Bazarr. Inspect any custom Bazarr path mappings if the storage check passes but Bazarr still reports a missing file.

If a NAS is remounted after containers started, recreate the affected containers and rerun the checks. Container health alone does not prove that the media share is visible. These checks run on demand; they do not monitor later NAS disconnects.

## Storage script reference

| Command | Purpose |
|---|---|
| `configure_storage.sh --env-file PATH` | Prompt for paths and identity; back up and update `.env` |
| `check_storage.sh --env-file PATH` | Check mount identity, host access, and Compose configuration |
| `check_storage.sh --env-file PATH --runtime` | Also test actual containers and shared file visibility |
| `check_storage.sh --env-file PATH --runtime --sample PATH` | Also test an existing file and its subtitle directory |
| `setup_storage_dir.sh --env-file PATH` | Compatibility entry point for `configure_storage.sh` |

The checker accepts `--compose-file PATH` for a nonstandard Compose filename. Configuration accepts `--movies`, `--tv`, `--downloads`, `--puid`, `--pgid`, `--storage-type local` or `--storage-type nas`, `--create-local`, and `--non-interactive`. Use interactive mode when local and NAS directories are mixed. Run a script with `--help` for details. Paths must be absolute. Runtime checks require a local Docker Engine on the machine that owns the storage paths.

The checked LinuxServer services use `UMASK: "002"`. Umask affects newly created files; it does not repair old ownership or override NAS ACLs/CIFS mount modes. On permission failure, inspect the actual host file and its parent directories, the mount identity, and NAS-side write access. Keep `PUID`/`PGID` consistent and fix the specific cause before changing library permissions.

Run the storage regression checks from the repository root with:

```bash
python3 -m unittest discover -s tests -v
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
> - In Bazarr+, configure the FlareSolverr URL in the Provider Hub plugin (OpenSubtitles.org) to `http://flaresolverr:8191/v1`.
> - Default ports and IP addresses can be customized in the `.env` file generated by `init_udms.sh`.

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
