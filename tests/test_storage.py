"""Storage regression checks. Run with python3 -m unittest discover -s tests -v."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from string import Template
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('storage', Path(__file__).resolve().parents[1] / 'scripts/storage.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)

    def test_dotenv_roundtrip_preserves_literals_and_secrets(self):
        env = self.root / '.env'
        marker = self.root / 'must-not-exist'
        secret_line = 'EXISTING_SECRET="keep-this-value"\n'
        env.write_text(secret_line + 'PUID=1001\n')
        path = str(self.root / f"Movie's \\ folder $HOME $(touch {marker})")
        storage.save_environment(env, {'MOVIES_DIR': path, 'PUID': '1001'})
        self.assertEqual(storage.environment(env)['MOVIES_DIR'], path)
        self.assertIn(secret_line, env.read_text())
        self.assertFalse(marker.exists())
        self.assertEqual(env.stat().st_mode & 0o777, 0o600)
        backups = list(self.root.glob('.env.backup-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), secret_line + 'PUID=1001\n')
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o600)
        storage.save_environment(env, {'MOVIES_DIR': path, 'PUID': '1001'})
        self.assertEqual(len(list(self.root.glob('.env.backup-*'))), 1)

    def test_nas_missing_or_different_source_is_rejected(self):
        values = {'MOVIES_STORAGE': 'nas', 'MOVIES_MOUNT_TARGET': '/mnt/nas',
                  'MOVIES_MOUNT_SOURCE': '//nas/FamilyShare', 'MOVIES_MOUNT_FSTYPE': 'cifs'}
        for info in ({'target': '/', 'source': '/dev/sda1', 'fstype': 'ext4'},
                     {'target': '/mnt/nas', 'source': '//nas/WrongShare', 'fstype': 'cifs'}):
            with self.subTest(info=info), patch.object(storage, 'mount_info', return_value=info):
                with self.assertRaises(storage.StorageError):
                    storage.check_mount('MOVIES', Path('/mnt/nas/Movies'), values)

    def test_mismatched_or_auto_created_compose_mount_is_rejected(self):
        expected = {'/data/movies': '/mnt/nas/Movies'}
        for source, automatic in [('/mnt/nas/media/movies', False), ('/mnt/nas/Movies', True)]:
            with self.subTest(source=source, automatic=automatic):
                mounts = [{'type': 'bind', 'source': source, 'target': '/data/movies',
                           'bind': {'create_host_path': automatic}}]
                with self.assertRaises(storage.StorageError):
                    storage.verify_mounts('bazarr', mounts, expected, rendered=True)

    def test_short_mount_source_must_exist_with_real_compose(self):
        env = self.root / '.env'
        env.write_text('PUID=1001\nPGID=1001\n')
        file = self.root / 'compose.yml'
        file.write_text('services:\n  bazarr:\n    image: unused\n    volumes:\n      - type: bind\n        source: ${MOVIES_DIR:?Set MOVIES_DIR}\n        target: /data/movies\n        bind:\n          create_host_path: false\n')
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(storage.StorageError):
                storage.compose(env, file, 'config', '--format', 'json')

    def test_cross_container_probe_detects_different_directories_and_cleans_up(self):
        first, second = self.root / 'first', self.root / 'second'
        first.mkdir()
        second.mkdir()
        roots = {'radarr': first, 'bazarr': second}

        def local_exec(container, uid_gid, script, *arguments):
            translated = [str(roots[container]) + arg[len('/data/movies'):] if arg.startswith('/data/movies/') else arg for arg in arguments]
            result = subprocess.run(['sh', '-c', script, 'udms-storage', *translated], capture_output=True, text=True)
            if result.returncode:
                raise storage.StorageError('probe failed')
            return result.stdout

        with patch.object(storage, 'exec_container', side_effect=local_exec):
            with self.assertRaises(storage.StorageError):
                storage.cross_check({'radarr': 'radarr', 'bazarr': 'bazarr'}, '1001:1001', 'radarr', 'bazarr', '/data/movies')
            self.assertEqual(list(first.iterdir()), [])
            roots['bazarr'] = first
            storage.cross_check({'radarr': 'radarr', 'bazarr': 'bazarr'}, '1001:1001', 'radarr', 'bazarr', '/data/movies')
            self.assertEqual(list(first.iterdir()), [])

    def test_configuration_does_not_create_directory_when_nas_is_unmounted(self):
        env = self.root / '.env'
        env.write_text('PUID=1001\nPGID=1001\n')
        missing = self.root / 'nas' / 'Movies'
        args = argparse.Namespace(env_file=env, puid=None, pgid=None, movies=str(missing),
                                  tv=None, downloads=None, storage_type='nas', create_local=True, non_interactive=True)
        with self.assertRaises(storage.StorageError):
            storage.configure(args)
        self.assertFalse(missing.exists())
        self.assertFalse(list(self.root.glob('.env.backup-*')))

    def test_local_creation_is_explicit_and_configuration_is_repeatable(self):
        env = self.root / '.env'
        env.write_text('PUID=' + str(os.getuid() or 1001) + '\nPGID=' + str(os.getgid() or 1001) + '\n')
        paths = [self.root / name for name in ('Movies with spaces', 'TV', 'Downloads')]
        args = argparse.Namespace(env_file=env, puid=None, pgid=None,
                                  movies=str(paths[0]), tv=str(paths[1]), downloads=str(paths[2]),
                                  storage_type='local', create_local=False, non_interactive=True)
        with self.assertRaises(storage.StorageError):
            storage.configure(args)
        args.create_local = True
        storage.configure(args)
        storage.configure(args)
        self.assertTrue(all(p.is_dir() for p in paths))
        values = storage.environment(env)
        self.assertEqual(values['MOVIES_DIR'], str(paths[0]))
        self.assertEqual(values['TV_STORAGE'], 'local')
        self.assertEqual(len(list(self.root.glob('.env.backup-*'))), 1)

    def test_repository_compose_preflight_uses_shared_paths(self):
        repo = Path(__file__).resolve().parents[1]
        deployment = self.root / 'deployment'
        links = deployment / 'compose' / 'test'
        links.mkdir(parents=True)
        for file in (repo / 'compose').glob('*.yml'):
            (links / file.name).symlink_to(file)
        (deployment / 'docker-compose-udms.yml').symlink_to(repo / 'docker-compose-udms.yml')
        template = (repo / 'init_udms.sh').read_text().split('cat <<EOF | sudo tee "$DOCKERDIR/.env" > /dev/null\n', 1)[1].split('\nEOF', 1)[0]
        env = deployment / '.env'
        uid, gid = str(os.getuid() or 1001), str(os.getgid() or 1001)
        env.write_text(Template(template).substitute(USERID=uid, GROUPID=gid, TZ='UTC',
            USERDIR=str(self.root), DOCKERDIR=str(deployment), DATADIR=str(self.root / 'data'),
            HOSTNAME='test', TRANSCODE='/tmp'))
        args = argparse.Namespace(env_file=env, puid=uid, pgid=gid,
            movies=str(self.root / 'Movies'), tv=str(self.root / 'TV'), downloads=str(self.root / 'Downloads'),
            storage_type='local', create_local=True, non_interactive=True, compose_file=None)
        storage.configure(args)
        values, services, config = storage.configuration(args)
        self.assertEqual(services['bazarr']['volumes'][1]['source'], values['MOVIES_DIR'])
        model = json.loads(storage.compose(env, config, 'config', '--format', 'json'))
        self.assertEqual(model['services']['radarr']['environment']['UMASK'], '002')

    def test_process_identity_checks_effective_ids_and_umask(self):
        # Execute the actual /proc inspection shell against this Python process.
        def proc_exec(container, uid_gid, script, *arguments):
            return subprocess.check_output(['sh', '-c', script, 'udms-storage', *arguments], text=True)
        with patch.object(storage, 'exec_container', side_effect=proc_exec):
            storage.application_identity('unused', 'bazarr', str(os.geteuid()), str(os.getegid()))
            with self.assertRaises(storage.StorageError):
                storage.application_identity('unused', 'bazarr', '4294967294', '4294967294')

    def test_remote_docker_is_rejected(self):
        with patch.dict(os.environ, {'DOCKER_HOST': 'ssh://other-server'}):
            with self.assertRaises(storage.StorageError):
                storage.require_local_docker()

    def test_process_umask_mismatch_is_rejected(self):
        with patch.object(storage, 'exec_container', return_value='1001:1001:0022\n'):
            with self.assertRaisesRegex(storage.StorageError, 'umask is 0022'):
                storage.application_identity('unused', 'qbittorrent', '1001', '1001')

    def test_unwritable_storage_is_rejected(self):
        if os.geteuid() == 0:
            self.skipTest('Permission denial requires a non-root test process')
        path = self.root / 'read-only-directory'
        path.mkdir(mode=0o500)
        with self.assertRaises(storage.StorageError):
            storage.check_host_access(path, str(os.geteuid()), str(os.getegid()))


if __name__ == '__main__':
    unittest.main()
