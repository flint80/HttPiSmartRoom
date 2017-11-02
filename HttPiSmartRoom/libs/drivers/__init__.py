import common.util as util
import fake
import traceback
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
    util.logger.debug("loading module  gpio")
    import gpio
    registry['GPIO'] = gpio.GPIO
    util.logger.debug("loaded module  gpio")
except ImportError:
    util.logger.warning("unable to load module gpio, reason %s"  % traceback.format_exc()  )
try:
    print "loading irsensor"
    from drivers import irsensor
    registry['IRSENSOR'] = irsensor.IRSensor
    print "loading irsensor"
except ImportError:
    util.logger.warning("unable to load module irsensor, reason %s"  % traceback.format_exc()  )
try:
    from drivers import player
    registry['MPD'] = player.MPD
except ImportError:
    util.logger.warning("unable to load module MPD, reason %s"  % traceback.format_exc()  )

