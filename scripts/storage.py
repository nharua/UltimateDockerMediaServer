#!/usr/bin/env python3
"""Configure and verify shared media storage. Requires Docker Compose v2+."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime
import uuid


LIBRARIES = {
    'MOVIES': ('/data/movies', 'radarr'),
    'TV': ('/data/tv', 'sonarr'),
    'DOWNLOADS': ('/data/downloads', 'qbittorrent'),
}
NETWORK_FS = {'cifs', 'smb3', 'nfs', 'nfs4', 'ceph', 'glusterfs', 'fuse.sshfs'}


class StorageError(Exception):
    pass


def run(args, *, input=None):
    try:
        result = subprocess.run(args, input=input, text=True, capture_output=True, timeout=45)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StorageError(f'Cannot run {args[0]}: {type(exc).__name__}') from exc
    if result.returncode:
        # Compose errors can contain interpolated secrets. Never echo its output.
        raise StorageError(f'{args[0]} command failed. Check access, configuration, and service readiness.')
    return result.stdout


def compose(env_file, compose_file, *args):
    return run(['docker', 'compose', '--env-file', str(env_file), '-f', str(compose_file), *args])


def environment(env_file):
    if not env_file.is_file():
        raise StorageError(f'Environment file not found: {env_file}. Run init_udms.sh first.')
    # Let Compose parse dotenv quoting/interpolation; never source/eval the file.
    with tempfile.TemporaryDirectory(prefix='udms-env-') as folder:
        minimal = Path(folder) / 'compose.yml'
        minimal.write_text('services: {}\n')
        output = compose(env_file, minimal, 'config', '--environment')
    return dict(line.split('=', 1) for line in output.splitlines() if '=' in line)


def require_local_docker():
    endpoint = os.environ.get('DOCKER_HOST')
    if not endpoint:
        endpoint = json.loads(run(['docker', 'context', 'inspect', '--format', '{{json .Endpoints.docker.Host}}']))
    if not endpoint.startswith('unix://'):
        raise StorageError('Use a local Docker socket. Run these scripts on the host that owns the storage.')


def absolute_directory(value):
    if not value or any(ord(c) < 32 for c in value):
        raise StorageError('Storage paths must be nonempty and contain no control characters.')
    path = Path(value)
    if not path.is_absolute() or path == Path('/'):
        raise StorageError(f'Use an absolute library path other than /: {value}')
    return path.resolve()


def identity(uid, gid):
    for value in (uid, gid):
        if not re.fullmatch(r'[0-9]+', str(value)) or not 0 < int(value) < 2**32 - 1:
            raise StorageError('PUID and PGID must be numeric, non-root IDs.')
    return str(int(uid)), str(int(gid))


def mount_info(path):
    data = json.loads(run(['findmnt', '--json', '--target', str(path),
                           '--output', 'TARGET,SOURCE,FSTYPE,OPTIONS']))['filesystems'][0]
    if 'ro' in data['options'].split(','):
        raise StorageError(f'Storage is mounted read-only: {path}')
    return {key: data[key] for key in ('target', 'source', 'fstype')}


def check_mount(prefix, path, values):
    info = mount_info(path)
    kind = values.get(prefix + '_STORAGE')
    if kind == 'nas':
        if info['fstype'] not in NETWORK_FS:
            raise StorageError(f'{prefix}: expected a mounted NAS filesystem at {path}; found {info["fstype"]}.')
        for key in ('target', 'source', 'fstype'):
            expected = values.get(prefix + '_MOUNT_' + key.upper())
            if not expected or info[key] != expected:
                raise StorageError(f'{prefix}: NAS mount {key} differs from the saved configuration. Restore the mount or reconfigure storage.')
    elif kind == 'local':
        if info['fstype'] in NETWORK_FS:
            raise StorageError(f'{prefix}: a network filesystem requires NAS mode.')
    else:
        raise StorageError(f'{prefix}: storage mode missing. Run configure_storage.sh.')
    return info


def prompt(label, default, non_interactive):
    if non_interactive:
        return str(default)
    answer = input(f'{label} [{default}]: ').strip()
    return answer or str(default)


def quote_env(value):
    # Dotenv double quotes support JSON escapes; $$ prevents Compose interpolation.
    return json.dumps(str(value), ensure_ascii=False).replace('$', '$$')


def save_environment(path, updates):
    before = path.read_text()
    lines = before.splitlines(keepends=True)
    result, seen = [], set()
    for line in lines:
        match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
        key = match.group(1) if match else None
        if key in updates:
            if key not in seen:
                result.append(f'{key}={quote_env(updates[key])}\n')
                seen.add(key)
        else:
            result.append(line)
    if result and not result[-1].endswith('\n'):
        result[-1] += '\n'
    result.extend(f'{key}={quote_env(value)}\n' for key, value in updates.items() if key not in seen)
    after = ''.join(result)
    if after == before:
        print('Storage configuration is unchanged.')
        return
    # mkstemp creates private files. Backup contains the entire secret-bearing .env.
    fd, backup_name = tempfile.mkstemp(prefix=path.name + '.backup-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '-', dir=path.parent)
    with os.fdopen(fd, 'w') as backup:
        backup.write(before)
    fd, temp_name = tempfile.mkstemp(prefix='.udms-env-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as temp:
            temp.write(after)
            temp.flush()
            os.fsync(temp.fileno())
        stat = path.stat()
        os.chown(temp_name, stat.st_uid, stat.st_gid)
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f'Updated {path}. Private backup: {backup_name}')


def configure(args):
    require_local_docker()
    values = environment(args.env_file)
    uid, gid = identity(
        prompt('Shared PUID', args.puid or values.get('PUID', os.environ.get('SUDO_UID', os.getuid())), args.non_interactive),
        prompt('Shared PGID', args.pgid or values.get('PGID', os.environ.get('SUDO_GID', os.getgid())), args.non_interactive))
    updates = {'PUID': uid, 'PGID': gid}
    create = []
    for prefix in LIBRARIES:
        default = values.get(prefix + '_DIR')
        if not default:
            base = values.get('DATADIR', '/srv/udms/data')
            default = str(Path(base) / {'MOVIES': 'media/movies', 'TV': 'media/tv', 'DOWNLOADS': 'downloads'}[prefix])
        path = absolute_directory(prompt(prefix + ' directory', getattr(args, prefix.lower()) or default, args.non_interactive))
        kind = prompt(prefix + ' storage type (local/nas)', args.storage_type or values.get(prefix + '_STORAGE', 'local'), args.non_interactive)
        if kind not in ('local', 'nas'):
            raise StorageError('Storage type must be local or nas.')
        if not path.is_dir():
            if path.exists() or kind == 'nas':
                raise StorageError(f'Directory not found: {path}. Mount NAS storage before configuration.')
            allow_create = args.create_local
            if not args.non_interactive and not allow_create:
                allow_create = input(f'Create new local directory {path}? [y/N]: ').strip().lower() == 'y'
            if not allow_create:
                raise StorageError(f'Directory not found: {path}. Use --create-local for new local storage.')
            create.append(path)
        # Inspect the nearest existing ancestor before creating anything.
        existing = path
        while not existing.exists():
            existing = existing.parent
        info = mount_info(existing)
        if (info['fstype'] in NETWORK_FS) != (kind == 'nas'):
            raise StorageError(f'{prefix}: selected {kind} but found filesystem {info["fstype"]}. Mount the NAS first or select the correct storage type.')
        updates[prefix + '_DIR'] = str(path)
        updates[prefix + '_STORAGE'] = kind
        for key in ('target', 'source', 'fstype'):
            updates[prefix + '_MOUNT_' + key.upper()] = info[key] if kind == 'nas' else ''
        print(f'{prefix}: {path} -> {LIBRARIES[prefix][0]} ({kind}, {info["fstype"]})')
    if len({updates[key + '_DIR'] for key in LIBRARIES}) != len(LIBRARIES):
        raise StorageError('Movies, TV, and downloads must use different directories.')
    print(f'Shared application UID:GID = {uid}:{gid}')
    if not args.non_interactive and input('Save storage configuration? [y/N]: ').strip().lower() != 'y':
        print('Cancelled. No configuration or directories changed.')
        return
    for path in create:
        path.mkdir(parents=True, exist_ok=False, mode=0o775)
        os.chown(path, int(uid), int(gid))
        os.chmod(path, 0o2775)
    save_environment(args.env_file, updates)


def expected_mounts(values):
    return {
        'radarr': {'/data/movies': values['MOVIES_DIR'], '/data/downloads': values['DOWNLOADS_DIR']},
        'sonarr': {'/data/tv': values['TV_DIR'], '/data/downloads': values['DOWNLOADS_DIR']},
        'bazarr': {'/data/movies': values['MOVIES_DIR'], '/data/tv': values['TV_DIR']},
        'qbittorrent': {'/data/downloads': values['DOWNLOADS_DIR']},
        'sabnzbd': {'/data/downloads': values['DOWNLOADS_DIR']},
    }


def verify_mounts(service, mounts, expected, *, rendered):
    index = {m.get('target' if rendered else 'Destination'): m for m in mounts}
    for target, source in expected.items():
        mount = index.get(target, {})
        actual = mount.get('source' if rendered else 'Source', '')
        if mount.get('type' if rendered else 'Type') != 'bind' or not actual or Path(actual).resolve() != Path(source).resolve():
            raise StorageError(f'{service}: {target} must bind {source}; found {actual or "no bind mount"}.')
        if (mount.get('read_only', False) if rendered else not mount.get('RW', False)):
            raise StorageError(f'{service}: {target} must be writable.')
        if rendered and mount.get('bind', {}).get('create_host_path', True):
            raise StorageError(f'{service}: {target} must set bind.create_host_path: false.')


def configuration(args):
    require_local_docker()
    values = environment(args.env_file)
    identity(values.get('PUID', ''), values.get('PGID', ''))
    for prefix in LIBRARIES:
        path = absolute_directory(values.get(prefix + '_DIR', ''))
        if not path.is_dir():
            raise StorageError(f'{prefix}: directory does not exist: {path}')
        check_mount(prefix, path, values)
        check_host_access(path, values['PUID'], values['PGID'])
        print(f'PASS {prefix}: directory and storage mount')
    config_file = args.compose_file or Path(values.get('DOCKERDIR', str(args.env_file.parent))) / 'docker-compose-udms.yml'
    model = json.loads(compose(args.env_file, config_file, 'config', '--format', 'json'))
    services = model.get('services', {})
    for name in ('radarr', 'sonarr', 'bazarr'):
        if name not in services:
            raise StorageError(f'Required service missing from Compose: {name}')
    for name, mounts in expected_mounts(values).items():
        if name not in services:
            continue
        service = services[name]
        verify_mounts(name, service.get('volumes', []), mounts, rendered=True)
        env = service.get('environment', {})
        if any(str(env.get(key)) != values[key] for key in ('PUID', 'PGID')):
            raise StorageError(f'{name}: PUID/PGID differ from shared storage identity.')
        if name != 'bazarr' and (env.get('UMASK') != '002' or 'UMASK_SET' in env):
            raise StorageError(f'{name}: configure UMASK: "002" and remove UMASK_SET.')
        print(f'PASS {name}: Compose mounts and identity')
    return values, services, config_file


def check_host_access(path, uid, gid):
    code = '''import os, sys, tempfile
uid, gid = int(sys.argv[2]), int(sys.argv[3])
if os.geteuid() == 0:
    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)
elif (os.geteuid(), os.getegid()) != (uid, gid):
    sys.exit(1)
with os.scandir(sys.argv[1]) as entries:
    next(entries, None)
with tempfile.NamedTemporaryFile(prefix='.udms-storage-check-', dir=sys.argv[1]) as f:
    f.write(b'host-access-check')
    f.flush()
    os.fsync(f.fileno())
'''
    try:
        run([sys.executable, '-c', code, str(path), uid, gid])
    except StorageError as exc:
        raise StorageError(f'Cannot list/create/write/delete in {path} as {uid}:{gid}. Run the checker with sudo and check host/NAS permissions.') from exc


def exec_container(container, uid_gid, script, *arguments):
    return run(['docker', 'exec', '--user', uid_gid, container, 'sh', '-c', script, 'udms-storage', *arguments])


def application_identity(container, name, uid, gid):
    # Read the application process, not root's init process or docker exec's shell.
    patterns = {'bazarr': 'python*', 'radarr': 'Radarr', 'sonarr': 'Sonarr',
                'qbittorrent': 'qbittorrent-nox', 'sabnzbd': 'python*'}
    code = """awk -v wanted="$1" '
FNR == 1 { name=""; uid=""; gid=""; mask="" }
$1 == "Name:" { name=$2 }
$1 == "Umask:" { mask=$2 }
$1 == "Uid:" { uid=$3 }
$1 == "Gid:" {
    gid=$3
    if ((wanted == "python*" && name ~ /^python/) || name == wanted) {
        print uid ":" gid ":" mask
        found=1
        exit
    }
}
END { if (!found) exit 1 }
' /proc/[0-9]*/status"""
    actual, mask = exec_container(container, f'{uid}:{gid}', code, patterns[name]).strip().rsplit(':', 1)
    if actual != f'{uid}:{gid}':
        raise StorageError(f'{name}: application runs as {actual}, expected {uid}:{gid}.')
    if name != 'bazarr' and mask not in ('0002', '002'):
        raise StorageError(f'{name}: application umask is {mask}, expected 0002. Recreate the container with UMASK="002".')


def cross_check(containers, uid_gid, writer, reader, target):
    filename = '.udms-storage-check-' + uuid.uuid4().hex
    token = uuid.uuid4().hex
    path = target + '/' + filename
    made = False
    try:
        exec_container(containers[writer], uid_gid,
                       'set -eu; umask 002; set -C; printf "%s" "$2" > "$1"', path, token)
        made = True
        actual = exec_container(containers[reader], uid_gid, 'set -eu; cat -- "$1"', path)
        if actual != token:
            raise StorageError(f'{writer} -> {reader}: different content at {target}.')
        exec_container(containers[reader], uid_gid, 'set -eu; printf "%s" "$2" >> "$1"', path, '-subtitle')
        actual = exec_container(containers[writer], uid_gid, 'set -eu; cat -- "$1"', path)
        if actual != token + '-subtitle':
            raise StorageError(f'{reader} -> {writer}: write not visible at {target}.')
    except StorageError as exc:
        raise StorageError(f'{writer} <-> {reader}: shared-file probe failed at {target}. Check both mounts and read/write permissions.') from exc
    finally:
        if made:
            exec_container(containers[writer], uid_gid, 'rm -- "$1"', path)
    print(f'PASS {writer} <-> {reader}: same file, read/write/delete at {target}')


def runtime(args, values, services, config_file):
    ids = compose(args.env_file, config_file, 'ps', '--all', '--quiet').split()
    if not ids:
        raise StorageError('No containers found. Start the Compose services first.')
    containers = {}
    for info in json.loads(run(['docker', 'inspect', *ids])):
        name = info['Config'].get('Labels', {}).get('com.docker.compose.service')
        if name not in expected_mounts(values) or name not in services:
            continue
        if not info['State'].get('Running'):
            raise StorageError(f'{name}: container is not running.')
        verify_mounts(name, info['Mounts'], expected_mounts(values)[name], rendered=False)
        env = dict(item.split('=', 1) for item in info['Config'].get('Env', []) if '=' in item)
        if any(env.get(key) != values[key] for key in ('PUID', 'PGID')):
            raise StorageError(f'{name}: running PUID/PGID differ from .env. Recreate the container.')
        if name != 'bazarr' and (env.get('UMASK') != '002' or 'UMASK_SET' in env):
            raise StorageError(f'{name}: running UMASK differs from Compose. Recreate the container.')
        application_identity(info['Id'], name, values['PUID'], values['PGID'])
        containers[name] = info['Id']
        print(f'PASS {name}: running mounts and application UID/GID')
    needed = {'radarr', 'sonarr', 'bazarr'} | ({'qbittorrent', 'sabnzbd'} & services.keys())
    missing = needed - containers.keys()
    if missing:
        raise StorageError('Services not running: ' + ', '.join(sorted(missing)))
    uid_gid = values['PUID'] + ':' + values['PGID']
    cross_check(containers, uid_gid, 'radarr', 'bazarr', '/data/movies')
    cross_check(containers, uid_gid, 'sonarr', 'bazarr', '/data/tv')
    for downloader in ('qbittorrent', 'sabnzbd'):
        if downloader in containers:
            for reader in ('radarr', 'sonarr'):
                cross_check(containers, uid_gid, downloader, reader, '/data/downloads')
    if args.sample:
        if not (args.sample.startswith('/data/movies/') or args.sample.startswith('/data/tv/')) or '..' in Path(args.sample).parts:
            raise StorageError('--sample must be a file under /data/movies/ or /data/tv/.')
        exec_container(containers['bazarr'], uid_gid,
                       '''set -eu; test -f "$1"; head -c 1 -- "$1" >/dev/null
p=$(mktemp "$(dirname -- "$1")/.udms-storage-check-XXXXXXXX")
trap 'rm -f -- "$p"' EXIT
printf '%s' subtitle-check > "$p"''', args.sample)
        print('PASS Bazarr: sample file readable and its parent directory writable')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('configure', 'check'))
    parser.add_argument('--env-file', type=lambda p: Path(p).absolute(), required=True)
    parser.add_argument('--compose-file', type=lambda p: Path(p).absolute())
    parser.add_argument('--runtime', action='store_true', help='also test running services using disposable files')
    parser.add_argument('--sample', help='existing media file path inside Bazarr; requires --runtime')
    parser.add_argument('--movies')
    parser.add_argument('--tv')
    parser.add_argument('--downloads')
    parser.add_argument('--puid')
    parser.add_argument('--pgid')
    parser.add_argument('--storage-type', choices=('local', 'nas'))
    parser.add_argument('--create-local', action='store_true', help='allow creation of missing local library directories')
    parser.add_argument('--non-interactive', action='store_true', help='save supplied/default values without prompts')
    args = parser.parse_args()
    try:
        if args.sample and not args.runtime:
            raise StorageError('--sample requires --runtime.')
        if args.action == 'configure':
            configure(args)
        else:
            values, services, config_file = configuration(args)
            if args.runtime:
                runtime(args, values, services, config_file)
            print('Storage checks passed.' + ('' if args.runtime else ' Run again with --runtime after starting services.'))
    except (StorageError, OSError, ValueError, KeyError, EOFError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
