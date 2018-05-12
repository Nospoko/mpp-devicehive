from devicehive import Handler
from devicehive import DeviceHive
from influxdb import InfluxDBClient
from datetime import datetime as dt

def notification2points(notification):
    device_id = notification.device_id
    value = notification.parameters['tick'] % 100
    print(value)

    points = [{
        "measurement": '{}'.format(device_id),
        # "time": int(now.strftime('%s')),
        "time": dt.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "fields": {
            "value": value
        }
    }]

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
        device_ids = ['esp-mon1']
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
        self.db.write_points(points)

if __name__ == '__main__':
    url = 'http://35.227.31.21/api/rest'
    with open('refresh_token') as fin:
        refresh_token = fin.read().strip()

    dh = DeviceHive(SimpleHandler)
    dh.connect(url, refresh_token=refresh_token)
