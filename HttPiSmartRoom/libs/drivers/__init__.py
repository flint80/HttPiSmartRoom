import fake
import traceback
import common.util as util
import manager
import ds18b20
import jabber
import openhab

registry = {}
registry['FAKE'] = fake.FakeDevice
registry['MANAGER'] = manager.Manager
registry['JABBER'] = jabber.Jabber
registry['OPENHAB'] = openhab.Openhab
registry['DS18B20'] = ds18b20.Ds18b20

try:
    import gnokii
    registry['GNOKII'] = gnokii.Gnokii
except ImportError:
    util.logger.warning("unable to load module gnokii, reason %s"  % traceback.format_exc()  )
try:
    import dht22
    registry['DHT22'] = dht22.DHT22
except ImportError:
    util.logger.warning("unable to load module dht22, reason %s"  % traceback.format_exc()  )
try:
    import gpio
    registry['GPIO'] = gpio.GPIO
except ImportError:
    util.logger.warning("unable to load module gpio, reason %s"  % traceback.format_exc()  )


