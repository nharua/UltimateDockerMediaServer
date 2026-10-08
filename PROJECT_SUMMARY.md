# Project Summary: Ultimate Docker Media Server (UDMS)

## 📌 Overview
**Ultimate Docker Media Server (UDMS)** is a homelab setup deploying a full-featured media management, streaming, downloading, and network infrastructure stack using Docker Compose with standardized volume layouts and security configurations.

---

## 🕒 Recent Session Summary (2026-10-08)

### Tasks Completed
1. **Migrated to Bazarr+**:
   - Replaced legacy `lscr.io/linuxserver/bazarr` image with official `ghcr.io/lavx/bazarr:latest` ([Bazarr+](https://lavx.github.io/bazarr/)).
   - Implemented container hardening per guide: `read_only: true`, `tmpfs: [/tmp:size=512m]`, dropped all caps except `CHOWN`, `SETUID`, `SETGID`, and `security_opt: [no-new-privileges:true]`.
   - Configured supervisor healthcheck (`http://localhost:6767/_supervisor/status`).
   - Added host timezone mount `/etc/localtime:/etc/localtime:ro`.

2. **Added & Configured FlareSolverr**:
   - Enabled and configured FlareSolverr service (`ghcr.io/flaresolverr/flaresolverr:latest`) in `compose/bazarr.yml` on `media_network`.
   - Assigned dedicated static IP `192.168.90.209` (via `${FLARESOLVERR_IP}`) and exposed port `8191` (`${FLARESOLVERR_PORT}`).
   - Ready for integration with Bazarr+ Provider Hub plugin (OpenSubtitles.org) via `http://flaresolverr:8191/v1` and Prowlarr indexers.

3. **Updated Environment Generator (`init_udms.sh`)**:
   - Added `FLARESOLVERR_PORT="8191"` and `FLARESOLVERR_IP="192.168.90.209"` variables into the `.env` generation template.

4. **Updated Documentation (`README.md`)**:
   - Expanded System Components table to document Bazarr+, FlareSolverr, Prowlarr, Lidarr, Readarr, Immich, Twingate, Pi-hole, and Unbound.
   - Updated Setup Order and Tips for Bazarr+ & FlareSolverr.
   - Corrected default web UI port listings (including Dozzle on `9999`).
   - Fixed unclosed code blocks and cleaned up formatting.

5. **Added Agent Workflow Rules**:
   - Added `AGENTS.md` and symlinked `GEMINI.md` defining session logging and unslop writing style rules.

6. **Repository-Wide English Translation**:
   - Scanned all codebase files and translated all Vietnamese comments, logs, interactive prompts, and documentation to English (`README.md`, `init_udms.sh`, `sync_compose_links.sh`, `setup_storage_dir.sh`, `compose/bazarr.yml`, `compose/radarr.yml`, `compose/filebrowser.yml`, `compose/immich.yml`).

---

## 📁 Key Project Files

| File | Status | Description |
|---|---|---|
| [`compose/bazarr.yml`](file:///home/rua/myWork/github/UltimateDockerMediaServer/compose/bazarr.yml) | Modified | Updated to Bazarr+ with hardening & healthcheck; added FlareSolverr service |
| [`compose/radarr.yml`](file:///home/rua/myWork/github/UltimateDockerMediaServer/compose/radarr.yml) | Modified | Translated volume comments to English |
| [`compose/filebrowser.yml`](file:///home/rua/myWork/github/UltimateDockerMediaServer/compose/filebrowser.yml) | Modified | Translated port comment and startup log to English |
| [`compose/immich.yml`](file:///home/rua/myWork/github/UltimateDockerMediaServer/compose/immich.yml) | Modified | Translated profile comment to English |
| [`init_udms.sh`](file:///home/rua/myWork/github/UltimateDockerMediaServer/init_udms.sh) | Modified | Added FlareSolverr variables; translated prompts, logs, and comments to English |
| [`sync_compose_links.sh`](file:///home/rua/myWork/github/UltimateDockerMediaServer/sync_compose_links.sh) | Modified | Translated prompts, logs, and comments to English |
| [`setup_storage_dir.sh`](file:///home/rua/myWork/github/UltimateDockerMediaServer/setup_storage_dir.sh) | Modified | Translated section comments and completion message to English |
| [`README.md`](file:///home/rua/myWork/github/UltimateDockerMediaServer/README.md) | Modified | Updated stack documentation, ports, tips, and translated notes to English |
| [`AGENTS.md`](file:///home/rua/myWork/github/UltimateDockerMediaServer/AGENTS.md) | Created | Agent behavioral rules and project session logging guidelines |
| [`GEMINI.md`](file:///home/rua/myWork/github/UltimateDockerMediaServer/GEMINI.md) | Created | Symlink to `AGENTS.md` |
| [`PROJECT_SUMMARY.md`](file:///home/rua/myWork/github/UltimateDockerMediaServer/PROJECT_SUMMARY.md) | Updated | Project summary tracking architecture, recent changes, and next steps |

---

## 🚀 Next Steps / Recommendations

1. **Deploy / Restart Services**:
   - Recreate containers to apply image and configuration updates:
     ```bash
     cd $DOCKERDIR && sudo docker compose up -d bazarr flaresolverr
     ```
2. **Configure Bazarr+ In-App Settings**:
   - Complete first-run wizard or login to `http://<HOST_IP>:6767`.
   - In **Subtitle Hub > Provider Hub Marketplace**, configure OpenSubtitles.org with FlareSolverr URL `http://flaresolverr:8191/v1`.
3. **Optional Prowlarr Integration**:
   - In Prowlarr (`http://<HOST_IP>:9696`), add FlareSolverr (`http://flaresolverr:8191/v1`) under **Settings > Indexers > FlareSolverr**.
4. **Git Push**:
   - Push recent commits to `origin/main` when ready.
