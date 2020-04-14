import requests
import config
import pprint
import datetime
import logging
import itertools
logging.basicConfig(level=logging.INFO)

def query(endpoint, **kwargs):
    url = config.URL + endpoint + '?apikey=' + config.API_KEY
    for k, v in kwargs.items():
        url += '&%s=%s'%(k, v)

    r = requests.get(url)
    r = r.json()
    #pprint.pprint(r)
    return r

class Device:
    def __init__(self, json):
        self.json = json
        self.id = self.json['id']
        self._data = self.json['data']
        self.is_plugged = self._data['isListening']['value']
        self.is_battery = not self.is_plugged
        self.is_enabled = self._data['is_enable']['value']
        self._description = self._data['description']
        self.name = self._description['name']
        self.location = self._description['location']
        self.product_name = self._description['product_name']
        #print "isReady=%s"%datetime.datetime.fromtimestamp(e['data']['isReady']['updateTime'])
        #print "isAwake=%s"%datetime.datetime.fromtimestamp(e['data']['isAwake']['updateTime'])
        self.last_received =datetime.datetime.fromtimestamp(self._data['lastReceived']['updateTime'])
        self.wakeup_interval = self._data['wakeup_interval']['value']
        wakeup_interval = self.wakeup_interval
        if not wakeup_interval:
            wakeup_interval = 86400
            logging.info("%s does not have a wakeup_interval in config, taking %s to compute next wakeup"%(self, config.DEFAULT_WAKEUP_INTERVAL))
        if self.id in config.NODE_LAST_RECEIVED_MAX_OVERRIDE:
            wakeup_interval = config.NODE_LAST_RECEIVED_MAX_OVERRIDE[self.id]
        self.next_expected_message = self.last_received + datetime.timedelta(seconds=wakeup_interval)

    @property
    def missed_message(self):
        if (datetime.datetime.now() - datetime.timedelta(seconds=600)) > self.next_expected_message:
            return True
        return False

    def __str__(self):
        return '%s - %s - %s - %s'%(self.id, self.location, self.name, self.product_name)


class DeviceCollection:
    def __init__(self, json):
        self.devices = []
        for device_id, e in r['result']['devices'].iteritems():
            e['id'] = int(device_id)
            self.devices.append(Device(e))

    def build_table(self, missed_only = False, sort_by = None, alternate_device_list=None):
        table_ = u""
        header = ['id', 'is_enabled', 'is_plugged', 'location', 'product_name', 'name', 'missed_message', 'last_received', 'next_expected_message']
        if alternate_device_list:
            devices = alternate_device_list
        else:
            devices = self.devices
        if sort_by:
            devices = sorted(devices, key=lambda e: getattr(e, sort_by))
        for d in itertools.chain([header], devices):
            line = []
            if isinstance(d, list):
                line = d
            else:
                for k in header:
                    line.append(unicode(getattr(d, k)))
                if missed_only and not d.missed_message:
                    continue
            s = "{0:<4} | {1:<15} | {2:<15} | {3:<20} | {4:<50} | {5:<50} | {6:<15} | {7:<20} | {8:<20}\r\n".format(*line)
            table_ += s
        return table_

    def check_status(self):
        dead_nodes = []
        for d in self.devices:
            if not d.is_enabled:
                continue
            if d.missed_message:
                if d.id in config.SKIP_MONITORING_NODE_ID:
                    continue
                dead_nodes.append(d)
        if dead_nodes:
            return self.build_table(alternate_device_list=dead_nodes, sort_by='last_received')
        return None

query('network', type="info", info="getStatus")
r = query('network', type="info", info="getHealth")
d = DeviceCollection(r)
result = d.check_status()
if result is None:
    exit(0)
else:
    print result
    exit(2)
#d.print_table(sort_by='last_received')
#query('network', type="info", info="getNodesList")
#query('network', type="info", info="getNeighbours")