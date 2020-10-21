#!/usr/bin/python3
# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import os
from pathlib import Path

from aion.mysql import BaseMysqlAccess
from aion.logger import lprint, lprint_exception


class RobotBackupDB(BaseMysqlAccess):
    def __init__(self):
        super().__init__("Maintenance")

    def set_backup_to_db(self, mac_address, backup_save_path, backup_date, backup_state):
        query = f"""
                insert into backupfiles(macAddress, path, date, state)
                values ('{mac_address}', '{backup_save_path}', '{backup_date}', {backup_state});
                """
        ret = self.set_query(query)
        if not ret:
            lprint_exception('failed to insert new backup data')
        else:
            self.commit_query()


class DeviceDB(BaseMysqlAccess):
    def __init__(self):
        super().__init__('Device')

    def get_devices(self, maker_id):
        query = f"""
                SELECT macAddress, deviceName, deviceIp
                FROM device
                WHERE makerId = '{maker_id}';
                """
        return self.get_query_list(100, query)

