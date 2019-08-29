#!/usr/bin/env python3
import sys
from dupcomposer.dupcomposer import read_config, BackupRunner
from dupcomposer.backup_config import BackupConfig

def main():
    config_raw =  read_config('tests/fixtures/dupcomposer-config.yml')
    config = BackupConfig(config_raw)
    runner = BackupRunner(config,sys.argv[1])
    commands = runner.get_cmds_raw()
    for group in sorted(commands):
        print('Generating commands for group {}:\n'.format(group))
        for cmd in commands[group]: print(cmd)
        print('\n')

if __name__ == '__main__':
         main()
