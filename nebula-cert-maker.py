#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# nebula-cert-maker, version 1

# Released under the terms of the GNU General Public Licence, version 2
# <http://www.gnu.org/licenses/>

# Revision history:
#   1 - Initial release

__license__ = 'GPL v2'
__version__ = '1'

import sys
import subprocess
import yaml
from collections import OrderedDict

# total arguments
n =len(sys.argv)

if (n > 1 ):
    with open(sys.argv[1], 'r') as f:
        stream = f.read()
else:
    print('Usage: "nebula-cert-maker.py host_list.yaml"')
    exit()

nebula_cert_cmd = "/usr/local/bin/nebula-cert"


def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

# usage example:
data = ordered_load(stream, yaml.SafeLoader)

def ordered_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

def make_cert(name, duration):
    subprocess.call([nebula_cert_cmd, "ca", "-name", name, "-duration", duration, "-out-qr", "ca.png"])

def sign_lighthouse(name, ip):
    subprocess.call([nebula_cert_cmd, "sign", "-name", name, "-ip", ip])

def sign_host(name, ip, groups, deviceCert, makeQRCode):
    if makeQRCode:
        subprocess.call([nebula_cert_cmd, "sign", "-name", name, "-ip", ip, "-groups", groups, *(["-in-pub", deviceCert] if (deviceCert != False) else []), "-out-qr", (name+".png")])       
    else:
        subprocess.call([nebula_cert_cmd, "sign", "-name", name, "-ip", ip, "-groups", groups, *(["-in-pub", deviceCert] if (deviceCert != False) else [])])

ca = data.get('ca')
make_cert(ca.get('name'),ca.get('duration'))

lighthouse_hosts = data.get('lighthouse-hosts')
for lightouse in lighthouse_hosts:
    sign_lighthouse(lightouse.get('name'),lightouse.get('ip'))

hosts = data.get('hosts')
for host in hosts:
    mygroups = ""
    for group in host.get('groups'):
        mygroups = mygroups+","+group
    
    mygroups = mygroups.lstrip(mygroups[0])

    deviceCert = False

    if "deviceCert" in host:
            deviceCert = host.get("deviceCert")
   
    if "makeQRCode" in host and host.get("makeQRCode") == True:
            sign_host(host.get('name'),host.get('ip'),mygroups,deviceCert,True)
    else:
        sign_host(host.get('name'),host.get('ip'),mygroups,deviceCert,False)
