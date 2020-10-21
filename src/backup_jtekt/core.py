# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import os
import shutil
from datetime import datetime, timedelta, timezone
from time import sleep

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from aion.microservice import main_decorator, Options
from aion.kanban import Kanban
from aion.logger import lprint, initialize_logger

from .robot_backup_db import RobotBackupDB, DeviceDB


MAKERID_JTEKT = 2
EXECUTE_INTERVAL = 1

SERVICE_NAME = os.environ.get("SERVICE", "get-plc-backup-jtekt-with-samba")
initialize_logger(SERVICE_NAME)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, conn, num, data_dir, copy_dir):
        self.conn = conn
        self.num = num
        self.data_dir = data_dir
        self.copy_dir = copy_dir
        self.JST = timezone(timedelta(hours=+9), 'JST')

    def __del__(self):
        del self.conn

    def on_created(self, event):
        lprint('on_created')
        depth = len(self.data_dir.split('/'))
        backup_taget = event.src_path.split('/')[depth]
        self.copy_backup(backup_taget)

    def copy_backup(self, backup_taget):
        backup_time = datetime.now(self.JST)
        timestamp = backup_time.strftime('%Y%m%d%H%M%S')

        with DeviceDB() as db:
            machine_list = db.get_devices(MAKERID_JTEKT)

        machine = machine_list[0]
        host = machine.get('deviceIp')
        mac_address = machine.get('macAddress')

        backup_save_dir = os.path.join(
            self.copy_dir,
            timestamp,
            host)
        os.makedirs(backup_save_dir, exist_ok=True)

        sleep(30)
        data_path = os.path.join(self.data_dir, backup_taget)
        backup_save_path = os.path.join(backup_save_dir, backup_taget)
        shutil.copytree(data_path, backup_save_path)
        shutil.rmtree(data_path)
        backup_state = 1

        try:
            # save log to mysql
            with RobotBackupDB() as db:
                db.set_backup_to_db(
                    mac_address,
                    backup_save_path,
                    backup_time.strftime('%Y-%m-%d %H:%M:%S'),
                    backup_state)
        finally:
            # output after kanban
            self.conn.output_kanban(
                result=True,
                connection_key="key",
                output_data_path=self.data_dir,
                process_number=self.num,
            )
        

@main_decorator(SERVICE_NAME)
def main(opt: Options):
    lprint("start main_without_kanban()")
    # get cache kanban
    conn = opt.get_conn()
    num = opt.get_number()
    kanban: Kanban = conn.set_kanban(SERVICE_NAME, num)

    data_dir = '/var/lib/aion/Data/samba'
    copy_dir = kanban.get_data_path() + '/data'

    ######### main function #############

    event_handler = ChangeHandler(conn, num, data_dir, copy_dir)
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=False)
    observer.start()
    try:
        while True:
            sleep(EXECUTE_INTERVAL)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    del event_handler

