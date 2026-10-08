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
   - Enabled and configured FlareSolverr service (`ghcr.io/flaresolverr/flaresolverr:latest`) directly in `compose/bazarr.yml` on `media_network`.
   - Assigned dedicated static IP `192.168.90.209` (configurable via `${FLARESOLVERR_IP}`) and exposed port `8191` (`${FLARESOLVERR_PORT}`).
   - Ready for integration with Bazarr+ Provider Hub plugin (OpenSubtitles.org) via `http://flaresolverr:8191/v1` and Prowlarr indexers.

3. **Updated Environment Generator (`init_udms.sh`)**:
   - Added `FLARESOLVERR_PORT="8191"` and `FLARESOLVERR_IP="192.168.90.209"` variables into the `.env` generation template.

4. **Updated Documentation (`README.md`)**:
   - Expanded System Components table to document Bazarr+, FlareSolverr, Prowlarr, Lidarr, Readarr, Immich, Twingate, Pi-hole, and Unbound.
   - Updated Setup Order and Tips for Bazarr+ & FlareSolverr.
   - Updated and corrected default web UI port listings (including Dozzle on `9999`).
   - Cleaned up markdown formatting and unclosed code blocks.

5. **Committed Changes**:
   - Committed changes adhering to Conventional Commits v1.0.0 (`feat(bazarr): update to bazarr+ and add flaresolverr configuration`, commit `80b98b2`).

---

## 📁 Modified / Created Files

| File | Status | Description |
|---|---|---|
| [`compose/bazarr.yml`](file:///home/rua/myWork/github/UltimateDockerMediaServer/compose/bazarr.yml) | Modified | Updated Bazarr to Bazarr+ with hardening & healthcheck; added configured FlareSolverr service |
| [`init_udms.sh`](file:///home/rua/myWork/github/UltimateDockerMediaServer/init_udms.sh) | Modified | Added `FLARESOLVERR_PORT` and `FLARESOLVERR_IP` to the `.env` generation block |
| [`README.md`](file:///home/rua/myWork/github/UltimateDockerMediaServer/README.md) | Modified | Updated components list, setup guidance, access URLs/ports, and formatting |
| [`PROJECT_SUMMARY.md`](file:///home/rua/myWork/github/UltimateDockerMediaServer/PROJECT_SUMMARY.md) | Created | Project summary tracking architecture, recent session changes, and next steps |

---

## 🚀 Next Steps / Recommendations

1. **Deploy / Restart Bazarr & FlareSolverr**:
   - If already running on host, recreate containers to apply image and hardening updates:
     ```bash
     cd $DOCKERDIR && sudo docker compose up -d bazarr flaresolverr
     ```
2. **Configure Bazarr+ In-App Settings**:
   - Complete first-run wizard or login to `http://<HOST_IP>:6767`.
   - In **Subtitle Hub > Provider Hub Marketplace**, install / configure the OpenSubtitles.org plugin and set FlareSolverr URL to `http://flaresolverr:8191/v1`.
3. **Optional Prowlarr Integration**:
   - In Prowlarr (`http://<HOST_IP>:9696`), add FlareSolverr (`http://flaresolverr:8191/v1`) under **Settings > Indexers > FlareSolverr** for indexers behind Cloudflare.
4. **Git Push**:
   - Push commit `80b98b2` to remote repository `origin/main` when ready.
