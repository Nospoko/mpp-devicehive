from devicehive import Handler
from devicehive import DeviceHive

class SimpleHandler(Handler):
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
        print(notification.notification)
        print(notification.parameters)
        print(notification.timestamp)
        print('--')

if __name__ == '__main__':
    url = 'http://35.227.31.21/api/rest'
    with open('refresh_token') as fin:
        refresh_token = fin.read().strip()

    dh = DeviceHive(SimpleHandler)
    dh.connect(url, refresh_token=refresh_token)
