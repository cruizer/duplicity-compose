import unittest
from  dupcomposer.dupcomposer import read_config
from dupcomposer.backup_config import (BackupConfig, BackupGroup,
                                       BackupEncryption, BackupProvider,
                                       BackupProviderLocal, BackupProviderS3,
                                       BackupProviderSCP, BackupSource,
                                       BackupFilePrefixes)

class TestBackupConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        
    def setUp(self):
        self.backup_config = BackupConfig(self.config_data)
        
    def test_object_instance(self):
        self.assertIsInstance(self.backup_config, BackupConfig)

    def test_attributes(self):
        self.assertEqual(self.backup_config.config_data,
                         self.config_data)

    def test_backup_groups_number(self):
        self.assertEqual(len(self.backup_config.groups), 3)

    def test_backup_groups_instances(self):
        for group in self.backup_config.groups:
            self.assertIsInstance(group, BackupGroup)

class TestBackupGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.backup_groups = {}

    def setUp(self):
        self.backup_groups['my_local_backups'] = \
            BackupGroup(self.config_data['backup_groups']['my_local_backups'], 'my_local_backups')
        self.backup_groups['my_s3_backups'] = \
            BackupGroup(self.config_data['backup_groups']['my_s3_backups'], 'my_s3_backups')
        self.backup_groups['my_scp_backups'] = \
            BackupGroup(self.config_data['backup_groups']['my_scp_backups'], 'my_scp_backups')

    def test_name(self):
        self.assertEqual(self.backup_groups['my_local_backups'].name, 'my_local_backups')
        self.assertEqual(self.backup_groups['my_s3_backups'].name, 'my_s3_backups')
        self.assertEqual(self.backup_groups['my_scp_backups'].name, 'my_scp_backups')

    def test_group_data(self):
        self.assertEqual(self.backup_groups['my_local_backups']
                         .group_data['backup_provider']['url'],
                         'file://')
        self.assertEqual(self.backup_groups['my_s3_backups']
                         .group_data['backup_provider']['url'],
                         's3://s3.sa-east-1.amazonaws.com/my-backup-bucket')
        self.assertEqual(self.backup_groups['my_scp_backups']
                         .group_data['backup_provider']['url'],
                         'scp://myscpuser@host.example.com/')

    def test_invalid_group_data(self):
        self.assertRaises(KeyError,
                          BackupGroup,
                          {'foo': 'bar'}, 'foo')

    def test_volume_cmd(self):
        self.assertEqual(self.backup_groups['my_local_backups']._get_volume_cmd(),
                         ['--volsize', '200'])
        self.assertEqual(self.backup_groups['my_s3_backups']._get_volume_cmd(),
                         ['--volsize', '50'])
        self.assertEqual(self.backup_groups['my_scp_backups']._get_volume_cmd(),
                         ['--volsize', '200'])

    def test_encryption_instance(self):
        self.assertIsInstance(self.backup_groups['my_s3_backups'].encryption, BackupEncryption)
        self.assertIsInstance(self.backup_groups['my_local_backups'].encryption, BackupEncryption)
        self.assertIsInstance(self.backup_groups['my_scp_backups'].encryption, BackupEncryption)

    def test_provider_instance(self):
        self.assertIsInstance(self.backup_groups['my_s3_backups'].provider, BackupProvider)
        self.assertIsInstance(self.backup_groups['my_local_backups'].provider, BackupProvider)
        self.assertIsInstance(self.backup_groups['my_scp_backups'].provider, BackupProvider)

    def test_source_instances(self):
        for s in self.backup_groups['my_s3_backups'].sources:
            self.assertIsInstance(s, BackupSource)
    
    def test_prefix_instance(self):
        self.assertIsInstance(self.backup_groups['my_s3_backups'].prefix, BackupFilePrefixes)

    def test_get_opts_raw_backup(self):
        self.assertEqual(self.backup_groups['my_s3_backups'].get_opts_raw('backup'),
                         [['--encrypt-key xxxxxx', '--sign-key xxxxxx',
                           '--volsize', '50',
                           '--file-prefix-archive', 'archive_',
                           '--file-prefix-manifest', 'manifest_',
                           '--file-prefix-signature', 'signature_',
                           '/home/shared',
                           's3://s3.sa-east-1.amazonaws.com/my-backup-bucket/home/shared'],
                          ['--encrypt-key xxxxxx', '--sign-key xxxxxx',
                           '--volsize', '50',
                           '--file-prefix-archive', 'archive_',
                           '--file-prefix-manifest', 'manifest_',
                           '--file-prefix-signature', 'signature_',
                           'etc',
                           's3://s3.sa-east-1.amazonaws.com/my-backup-bucket/etc']])
        self.assertEqual(self.backup_groups['my_local_backups'].get_opts_raw('backup'),
                         [['--no-encryption',
                           '--volsize', '200',
                           '/var/www/html',
                           'file:///root/backups/var/www/html'],
                          ['--no-encryption',
                           '--volsize', '200',
                           'home/tommy',
                           'file://backups/home/tommy']])
        self.assertEqual(self.backup_groups['my_scp_backups'].get_opts_raw('backup'),
                         [['--no-encryption',
                           '--volsize', '200',
                           '/home/katy',
                           'scp://myscpuser@host.example.com//home/katy'],
                          ['--no-encryption',
                           '--volsize', '200',
                           'home/fun',
                           'scp://myscpuser@host.example.com/home/fun']])

    def test_get_opts_raw_restore(self):
        self.assertEqual(self.backup_groups['my_s3_backups'].get_opts_raw('restore'),
                         [['--encrypt-key xxxxxx', '--sign-key xxxxxx',
                           '--volsize', '50',
                           '--file-prefix-archive', 'archive_',
                           '--file-prefix-manifest', 'manifest_',
                           '--file-prefix-signature', 'signature_',
                           's3://s3.sa-east-1.amazonaws.com/my-backup-bucket/home/shared',
                           '/root/restored/home/shared'],
                          ['--encrypt-key xxxxxx', '--sign-key xxxxxx',
                           '--volsize', '50',
                           '--file-prefix-archive', 'archive_',
                           '--file-prefix-manifest', 'manifest_',
                           '--file-prefix-signature', 'signature_',
                           's3://s3.sa-east-1.amazonaws.com/my-backup-bucket/etc',
                           'restored/etc']])
        self.assertEqual(self.backup_groups['my_local_backups'].get_opts_raw('restore'),
                         [['--no-encryption',
                           '--volsize', '200',
                           'file:///root/backups/var/www/html',
                           '/root/restored/var/www/html'],
                          ['--no-encryption',
                           '--volsize', '200',
                           'file://backups/home/tommy',
                           'restored/home/tommy']])
        self.assertEqual(self.backup_groups['my_scp_backups'].get_opts_raw('restore'),
                         [['--no-encryption',
                           '--volsize', '200',
                           'scp://myscpuser@host.example.com//home/katy',
                           '/root/restored/home/katy'],
                          ['--no-encryption',
                           '--volsize', '200',
                           'scp://myscpuser@host.example.com/home/fun',
                           'restored/home/fun']])

    def test_get_env(self):
        self.assertEqual(self.backup_groups['my_local_backups'].get_env(), {})
        self.assertEqual(self.backup_groups['my_s3_backups'].get_env(),
                         {'AWS_ACCESS_KEY': 'xxxxxx', 'AWS_SECRET_KEY': 'xxxxxx',
                          'PASSPHRASE': 'xxxxxx'})
        self.assertEqual(self.backup_groups['my_scp_backups'].get_env(),
                         {'FTP_PASSWORD': 'xxxxxx'}) 

class TestBackupEncryption(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.config_encryption_off = (cls.config_data['backup_groups']
                                                   ['my_local_backups']
                                                   ['encryption'])
        cls.config_encryption_on = (cls.config_data['backup_groups']
                                                   ['my_s3_backups']
                                                   ['encryption'])
    def setUp(self):
        self.backup_encryption_off = BackupEncryption(self.config_encryption_off)
        self.backup_encryption_on = BackupEncryption(self.config_encryption_on)

    def test_enabled_flag(self):
        self.assertIs(self.backup_encryption_off.enabled, False)
        self.assertIs(self.backup_encryption_on.enabled, True)

    def test_gpg_config(self):
        self.assertEqual(self.backup_encryption_on.gpg_key, 'xxxxxx')
        self.assertEqual(self.backup_encryption_on.gpg_passphrase, 'xxxxxx')
        self.assertEqual(self.backup_encryption_off.gpg_key, None)
        self.assertEqual(self.backup_encryption_off.gpg_key, None)

    def test_incorrect_enabled_flag(self):
        self.assertRaises(ValueError,
                          BackupEncryption,
                          {'enabled': 'chocolate'})

    def test_missing_key_or_passphrase(self):
        self.assertRaises(ValueError,
                          BackupEncryption,
                          {'enabled': True,
                           'gpg_key': 'xxxxxx'})
        self.assertRaises(ValueError,
                          BackupEncryption,
                          {'enabled': True,
                           'gpg_passphrase': 'xxxxxx'})

    def test_cmd_output_enc_on(self):
        self.assertEqual(self.backup_encryption_on.get_cmd(),
                         ['--encrypt-key xxxxxx', '--sign-key xxxxxx'])

    def test_environment_enc_on(self):
        self.assertEqual(self.backup_encryption_on.get_env(),
                         {'PASSPHRASE': 'xxxxxx'})

    def test_cmd_output_enc_off(self):
        self.assertEqual(self.backup_encryption_off.get_cmd(),
                         ['--no-encryption'])

    def test_environment_enc_off(self):
        self.assertEqual(self.backup_encryption_off.get_env(),
                      {})

class TestBackupProvider(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.config_provider_local = (cls.config_data['backup_groups']
                                                   ['my_local_backups']
                                                   ['backup_provider'])
        cls.config_provider_s3 = (cls.config_data['backup_groups']
                                                   ['my_s3_backups']
                                                   ['backup_provider'])
        cls.config_provider_scp = (cls.config_data['backup_groups']
                                                   ['my_scp_backups']
                                                   ['backup_provider'])

    def setUp(self):
        self.backup_local = BackupProvider.factory(self.config_provider_local)
        self.backup_s3 = BackupProvider.factory(self.config_provider_s3)
        self.backup_scp = BackupProvider.factory(self.config_provider_scp)

    def test_provider_instances(self):
        self.assertIsInstance(self.backup_local, BackupProviderLocal)
        self.assertIsInstance(self.backup_s3, BackupProviderS3)
        self.assertIsInstance(self.backup_scp, BackupProviderSCP)

    def test_missing_url(self):
        self.assertRaises(KeyError,
                          BackupProvider.factory,
                          {'foo': 'bar'})

    def test_local_invalid_url(self):
        self.assertRaises(ValueError,
                          BackupProvider.factory,
                          {'url': 'foo://'})

class TestBackupProviderLocal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.config_provider_local = (cls.config_data['backup_groups']
                                                   ['my_local_backups']
                                                   ['backup_provider'])

    def setUp(self):
        self.backup_local = BackupProvider.factory(self.config_provider_local)

    def test_get_cmd(self):
        self.assertEqual(self.backup_local.get_cmd('/home/test'), 'file:///home/test')
        self.assertEqual(self.backup_local.get_cmd('home/test'), 'file://home/test')

    def test_get_env(self):
        self.assertEqual(self.backup_local.get_env(), {})

class TestBackupProviderS3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.config_provider_s3 = (cls.config_data['backup_groups']
                                                   ['my_s3_backups']
                                                   ['backup_provider'])

    def setUp(self):
        self.backup_s3 = BackupProvider.factory(self.config_provider_s3)

    def test_get_cmd(self):
        self.assertEqual(self.backup_s3.get_cmd('home/test'),
                         's3://s3.sa-east-1.amazonaws.com/my-backup-bucket/home/test')
        self.assertEqual(self.backup_s3.get_cmd('/home/test'),
                         's3://s3.sa-east-1.amazonaws.com/my-backup-bucket/home/test')

    def test_get_env(self):
        self.assertEqual(self.backup_s3.get_env(), {'AWS_ACCESS_KEY': 'xxxxxx',
                                                    'AWS_SECRET_KEY': 'xxxxxx'})

    def test_missing_keys(self):
        self.assertRaises(KeyError,
                          BackupProvider.factory,
                          {'url': 's3://s3.sa-east-1.amazonaws.com/my-backup-bucket',
                           'aws_access_key': 'xxxxxx'})
        self.assertRaises(KeyError,
                          BackupProvider.factory,
                          {'url': 's3://s3.sa-east-1.amazonaws.com/my-backup-bucket',
                           'aws_secret_key': 'xxxxxx'})
        
class TestBackupProviderSCP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.config_provider_scp = (cls.config_data['backup_groups']
                                                   ['my_scp_backups']
                                                   ['backup_provider'])
        cls.config_provider_scp_nopass = cls.config_provider_scp.copy()
        del cls.config_provider_scp_nopass['password']

    def setUp(self):
        self.backup_scp = BackupProvider.factory(self.config_provider_scp)
        self.backup_scp_nopass = BackupProvider.factory(self.config_provider_scp_nopass)

    def test_get_cmd(self):
        self.assertEqual(self.backup_scp.get_cmd('/home/test/'),
                         'scp://myscpuser@host.example.com//home/test/')
        self.assertEqual(self.backup_scp.get_cmd('home/test'),
                         'scp://myscpuser@host.example.com/home/test')

    def test_get_env(self):
        self.assertEqual(self.backup_scp.get_env(), {'FTP_PASSWORD': 'xxxxxx'})
        self.assertEqual(self.backup_scp_nopass.get_env(), {})

class TestBackupSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.config_sources_for_local = (cls.config_data['backup_groups']
                                                   ['my_local_backups']
                                                   ['sources'])
        cls.config_provider_local = (cls.config_data['backup_groups']
                                                   ['my_local_backups']
                                                   ['backup_provider'])

    def setUp(self):
        self.local_provider = BackupProvider.factory(self.config_provider_local)
        self.backup_sources = []
        for source in self.config_sources_for_local:
            self.backup_sources.append(BackupSource(source,
                                                    self.config_sources_for_local[source],
                                                    self.local_provider))

    def test_instances(self):
        for source in self.backup_sources:
            self.assertIsInstance(source, BackupSource)

    def test_get_cmd_backup(self):
        for source in self.backup_sources:
            if source.source_path == '/var/www/html':
                cmd = ['/var/www/html', 'file:///root/backups/var/www/html']
            else:
                cmd = ['home/tommy', 'file://backups/home/tommy']
            self.assertEqual(source.get_cmd('backup'),
                             cmd)

    def test_get_cmd_restore(self):
        for source in self.backup_sources:
            if source.source_path == '/var/www/html':
                cmd = ['file:///root/backups/var/www/html', '/root/restored/var/www/html']
            else:
                cmd = ['file://backups/home/tommy', 'restored/home/tommy']
            self.assertEqual(source.get_cmd('restore'),
                             cmd)

    def test_get_cmd_invalid_mode(self):
        self.assertRaises(ValueError,
                          self.backup_sources[0].get_cmd,
                          'foo')

    def test_config_key_error(self):
        self.assertRaises(KeyError,
                          BackupSource,
                          'foo',
                          {'foo': 'bar'},
                          self.local_provider)

    def test_empty_path_error(self):
        self.assertRaises(ValueError,
                          BackupSource,
                          '',
                          {'backup_path': '/root',
                           'restore_path': '/root/restored'},
                          self.local_provider)
        self.assertRaises(ValueError,
                          BackupSource,
                          '/root',
                          {'backup_path': '',
                           'restore_path': '/root/restored'},
                          self.local_provider)
        self.assertRaises(ValueError,
                          BackupSource,
                          '/root',
                          {'backup_path': '/root',
                           'restore_path': ''},
                          self.local_provider)

class TestBackupFilePrefixes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_data = read_config('tests/fixtures/dupcomposer-config.yml')
        cls.prefixes_for_s3 = (cls.config_data['backup_groups']
                                                   ['my_s3_backups']
                                                   ['backup_file_prefixes'])

    def setUp(self):
        self.backup_prefixes = BackupFilePrefixes(self.prefixes_for_s3)
        self.backup_prefixes_none = BackupFilePrefixes(None)

    def test_instance(self):
        self.assertIsInstance(self.backup_prefixes, BackupFilePrefixes)
        self.assertIsInstance(self.backup_prefixes_none, BackupFilePrefixes)

    def test_get_cmd(self):
        self.assertEqual(self.backup_prefixes.get_cmd(),
                         ['--file-prefix-archive', 'archive_',
                          '--file-prefix-manifest', 'manifest_',
                          '--file-prefix-signature', 'signature_'])
        self.assertEqual(self.backup_prefixes_none.get_cmd(), [])

    def test_invalid_prefix(self):
        self.assertRaises(ValueError,
                          BackupFilePrefixes,
                          {'archive': 'archive_', 'foo': 'bar'})
