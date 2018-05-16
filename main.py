import numpy as np
from devicehive import Handler
from devicehive import DeviceHive
from influxdb import InfluxDBClient
from datetime import datetime as dt

DEVICE_IDS = ['esp-michal', 'esp-mon1']

def parse_mpp_device(device_id, notification, now):
    keys = notification.parameters.keys()
    if ('4' not in keys) or ('5' not in keys):
        return None

    value_0 = notification.parameters['4']
    value_1 = notification.parameters['5']

    if not isinstance(value_0, int):
        return None
    if not isinstance(value_1, int):
        return None

    points = [{
        "measurement": '{}'.format(device_id),
        "time": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "fields": {
            "in_1": value_0,
            "in_2": value_1
        }
    }]

    return points

def notification2points(notification):
    # Use this to pipe the data through different routines
    device_id = notification.device_id

    points = None

    now = dt.now()
    # Synology sucks at time
    # now -= datetime.timedelta(hours = 2)

    # Make sure that the RHS of those ifs is compatible
    # With the list of devices provided above
    if device_id == 'python-test-0':
        if 'state' not in notification.parameters.keys():
            return None
        keys = notification.parameters['state'].keys()
        if ('0' not in keys) or ('1' not in keys):
            return None
        value_0 = notification.parameters['state']['0']
        value_1 = notification.parameters['state']['1']

        points = [{
            "measurement": '{}'.format(device_id),
            "time": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": {
                "value_0": value_0,
                "value_1": value_1
            }
        }]

    if device_id == 'esp-michal':
        points = parse_mpp_device(device_id, notification, now)

    # Debug
    print(now, device_id)

    return points

class SimpleHandler(Handler):
    def __init__(self, *args, **kwargs):
        super(SimpleHandler, self).__init__(*args, **kwargs)

        # Influx access
        host = 'localhost'
        port = 8086
        USER = 'root'
        PASSWORD = 'root'
        DBNAME = 'tutorial'
        self.db = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)

    def handle_connect(self):
        device_ids = DEVICE_IDS
        for device_id in device_ids:
            device = self.api.put_device(device_id)
            device.subscribe_insert_commands()
            device.subscribe_update_commands()
            device.subscribe_notifications()

    def handle_command_insert(self, command):
        print(command.command)

    def handle_command_update(self, command):
        print(command.command)

    def handle_notification(self, notification):
        points = notification2points(notification)
        if points:
            self.db.write_points(points)
        else:
            print('Dissmissed notification!')
            print(notification.parameters)

if __name__ == '__main__':
    url = 'http://35.227.31.21/api/rest'
    with open('refresh_token') as fin:
        refresh_token = fin.read().strip()

    while True:
        try:
            print('Connecting to DeviceHive')
            dh = DeviceHive(SimpleHandler)
            dh.connect(url, refresh_token=refresh_token)
        except Exception as e:
            print('ERROR:', e)
