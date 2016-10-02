import fake
import manager
import gnokii
import ds18b20
import jabber

registry = {}
registry['FAKE'] = fake.FakeDevice
registry['DS18B20'] = ds18b20.Ds18b20
registry['GNOKII'] = gnokii.Gnokii
registry['MANAGER'] = manager.Manager
registry['JABBER'] = jabber.Jabber