# Sessions: Ultimate Docker Media Server (UDMS)

## 📌 Overview
**Ultimate Docker Media Server (UDMS)** is a homelab setup deploying a full-featured media management, streaming, downloading, and network infrastructure stack using Docker Compose with standardized volume layouts and security configurations.

---

## 🕒 Recent Session Summary (2026-10-28)

### Tasks Completed
1. **Debugged TheRARBG Custom Indexer in Prowlarr**:
   - Diagnosed `500 Internal Server Error` and UI validation failure (`System.ArgumentOutOfRangeException: Unknown Cardigann setting. (Parameter 'info_freeleech')`) when adding TheRARBG indexer via `therarbg.yml`.
   - Identified that Prowlarr's Cardigann schema parser does not support `type: info` in indexer settings (`info_freeleech`), causing `getUrls` and indexer testing to fail and leaving `Base Url` unpopulated.
   - Cleaned `appdata/prowlarr/Definitions/Custom/therarbg.yml` by removing the unsupported `info_freeleech` block.
   - Verified FlareSolverr proxy connectivity (`http://flaresolverr:8191/v1`) on `media_network` and restarted the `prowlarr` container to apply changes.

---

## 🕒 Previous Session Summary (2026-10-08)

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
| [`SESSIONS.md`](SESSIONS.md) | Updated | Project summary tracking architecture, recent changes, and next steps |

---

## 🚀 Next Steps / Recommendations

1. **Verify TheRARBG Indexer in Prowlarr**:
   - Re-open Prowlarr (`http://<HOST_IP>:9696`), navigate to **Add Indexer**, select **TheRARBG**, ensure `Base Url` is selected, and click **Save**.
   - Sync the indexer to downstream apps (Radarr, Sonarr) via **Settings > Apps**.
2. **Configure Bazarr+ In-App Settings**:
   - Complete first-run wizard or login to `http://<HOST_IP>:6767`.
   - In **Subtitle Hub > Provider Hub Marketplace**, configure OpenSubtitles.org with FlareSolverr URL `http://flaresolverr:8191/v1`.
3. **Monitor FlareSolverr Performance**:
   - Check container logs (`docker logs flaresolverr`) if any Cloudflare-protected indexers experience solver timeouts.

---

## Session 1 - 2026-11-02

### Task
Investigate Bazarr media access on the NAS, correct Radarr and Sonarr umask configuration, and migrate session logging to `SESSIONS.md`.

### What was done
- Connected to `mydocker` over SSH and confirmed Bazarr, Radarr, and Sonarr run as UID/GID `1001:1001`.
- Reproduced the Moana file access failure in Bazarr as `FileNotFoundError`. Its database path was correct, but its NAS bind mounts pointed to different directories than Radarr and Sonarr.
- Updated `/home/udms/compose/udms/bazarr.yml` on `mydocker` to mount `$DATADIR/Movies` at `/data/movies` and `$DATADIR/TVShows` at `/data/tv`. Saved a backup and recreated Bazarr with the existing image.
- Verified Bazarr could read Moana and its existing Vietnamese subtitle, create/write/delete a temporary file in the movie directory, and list the TV library. Bazarr reported healthy.
- Replaced `UMASK_SET: 002` with `UMASK: "002"` in Radarr and Sonarr Compose files in this repository and on `mydocker`. Saved backups on the server.
- Validated the repository Compose configuration. After the user recreated Radarr and Sonarr through sudo, verified both application processes use umask `0002`, retain UID/GID `1001:1001`, and return HTTP `200` from `/ping`.
- Renamed `PROJECT_SUMMARY.md` to `SESSIONS.md`, preserving previous history, and updated `AGENTS.md` to use `update-sessions` for requested session updates. Allowed `git status` within that workflow while retaining explicit permission for staging and commits.

### Files modified
- `compose/radarr.yml` - Use the supported `UMASK` variable with a quoted value.
- `compose/sonarr.yml` - Use the supported `UMASK` variable with a quoted value.
- `SESSIONS.md` - Renamed session history, updated its self-reference, and appended this entry.
- `AGENTS.md` - Reference `SESSIONS.md` and the `update-sessions` skill.
- On `mydocker`: `/home/udms/compose/udms/bazarr.yml`, `/home/udms/compose/udms/radarr.yml`, and `/home/udms/compose/udms/sonarr.yml`.

### TODO / Next Steps
- [ ] Retry a Moana subtitle search in the Bazarr UI to verify the provider search after correcting the mounts.
- [ ] Verify TheRARBG in Prowlarr and complete the Bazarr+ provider setup carried over from previous sessions.

### Notes
- Earlier entries retain their original format. Session 1 starts the numbered format used by `update-sessions`.
- The NAS uses CIFS with forced UID/GID `1001:1001` and file/directory modes `0755`. Media access checks passed without changing NAS ownership or modes.
- The Bazarr mount correction was applied on `mydocker`. This repository retains its generic `$DATADIR/media/movies` and `$DATADIR/media/tv` layout.
- The server's `.env` requires root access. The user entered sudo credentials directly in their terminal; credentials were not recorded.

---

## Session 2 - 2026-11-02

### Task
Update the session log using the `update-sessions` skill after migrating from `PROJECT_SUMMARY.md`.

### What was done
- Reviewed `git status`, `git diff --stat`, and the diffs for `AGENTS.md`, `compose/radarr.yml`, and `compose/sonarr.yml`.
- Confirmed Session 1 already records the Bazarr mount correction, Radarr/Sonarr umask changes, deployment checks, and session log migration.
- Reviewed the open TODOs. No new evidence confirms the Moana provider search or the Prowlarr/Bazarr+ setup, so those items remain open.
- Appended this entry without repeating the technical work documented in Session 1.

### Files modified
- `SESSIONS.md` - Added Session 2 with the log review and remaining follow-up tasks.

### TODO / Next Steps
- [ ] Complete the open TODOs in Session 1: retry the Moana subtitle search and verify the Prowlarr/Bazarr+ setup.

### Notes
- The earlier changes remain uncommitted. No files were staged and no commit was created.

---

## Session 3 - 2026-11-02

### Task
Prevent media mount mismatches on new deployments and document setup and diagnostics for existing servers.

### What was done
- Added `configure_storage.sh` and `check_storage.sh`, backed by `scripts/storage.py`, to configure shared Movies/TV/Downloads paths and verify host and container access.
- Preserved unrelated `.env` settings, added private backups and atomic updates, and parsed dotenv values through Compose without executing them in a shell.
- Added NAS mount identity checks, explicit creation of new local directories, application UID/GID and umask checks, shared-file probes, and an optional existing-media-file check.
- Converted affected Compose mounts to shared path variables and `create_host_path: false`. Updated downloader umask variables to `UMASK: "002"`.
- Changed initialization to refuse an existing `.env` and removed recursive media/NAS ACL changes. Replaced the old storage initializer with a compatibility entry point.
- Documented the command sequence for new servers and existing deployments in `README.md`.
- Passed 12 regression checks, including real Compose validation, missing or wrong NAS mounts, mismatched paths, dotenv literal handling, permission denial, umask mismatch, and probe cleanup. Shell syntax and whitespace checks passed.
- Tested file sharing on `mydocker` between Radarr/Bazarr, Sonarr/Bazarr, and qBittorrent/Radarr/Sonarr. All shared-file probes passed and were removed.

### Files modified
- `configure_storage.sh`, `check_storage.sh`, `scripts/storage.py` - Storage configuration and diagnostics.
- `tests/test_storage.py` - Storage and Compose regression checks.
- `compose/bazarr.yml`, `compose/radarr.yml`, `compose/sonarr.yml` - Shared media/download paths.
- `compose/qbittorrent.yml`, `compose/sabnzbd.yml` - Shared download paths and supported umask setting.
- `compose/jellyfin.yml`, `compose/filebrowser.yml`, `compose/lidarr.yml`, `compose/readarr.yml`, `compose/prowlarr.yml` - Consistent library or download sources.
- `init_udms.sh`, `setup_storage_dir.sh` - Separate initialization from storage configuration.
- `.gitignore` - Exclude private environment backups and Python caches.
- `README.md` - New-server setup, existing-server migration, and diagnostic commands.
- `SESSIONS.md` - Record the work and remaining deployment steps.

### TODO / Next Steps
- [ ] Migrate `mydocker` to the shared path variables and run the full preflight/runtime commands using its deployed Compose files.
- [ ] Recreate qBittorrent with the supported `UMASK: "002"` setting during migration. Its current application umask is `0022`.
- [ ] Complete the remaining Moana provider search and Prowlarr/Bazarr+ checks from Session 1.

### Notes
- Existing deployments must configure `MOVIES_DIR`, `TV_DIR`, and `DOWNLOADS_DIR` before using the updated Compose templates.
- The live checks used temporary files only. The new scripts and Compose settings have not been deployed to `mydocker`.
- NAS checks run on demand and do not monitor later disconnections.

---

## Session 4 - 2026-11-02

### Task
Separate FlareSolverr from the Bazarr Compose definition and load it from the root Compose file.

### What was done
- Moved the FlareSolverr service from `compose/bazarr.yml` to `compose/flaresolverr.yml`.
- Added the new file to the root Compose include list and documented the deployment/link requirement in `README.md`.
- Validated the complete Compose model and confirmed the resolved FlareSolverr service matches its previous configuration.
- Confirmed the existing initialization and link-sync scripts pick up the new `.yml` file automatically.

### Files modified
- `compose/bazarr.yml` - Remove the FlareSolverr definition.
- `compose/flaresolverr.yml` - Store the standalone FlareSolverr service.
- `docker-compose-udms.yml` - Include the new service file.
- `README.md` - Document the file split and existing-deployment requirement.
- `SESSIONS.md` - Record the change and verification.

### TODO / Next Steps
- [ ] Deploy or link `compose/flaresolverr.yml` on `mydocker` when migrating the Compose templates.

### Notes
- Image, ports, network address, environment, healthcheck, and security settings remain unchanged.
- The file split has not been applied to the running server.
