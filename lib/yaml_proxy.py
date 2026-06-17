from typing import Iterable
import yaml
from yaml import load
from ipaddress import ip_interface
 
class Host:
    def __init__(self,
                host_name = None,
                ip = None,
                arch = None,
                groups = None,
                note = None,
                device_cert = None,
                make_qr_code = "False"
                ):
        self.host_name = host_name
        self.ip = ip
        self.arch = arch
        self.groups = []
        if isinstance(groups, Iterable): self.groups.extend(groups)
        self.note = note
        self.device_cert = device_cert
        self.make_qr_code = make_qr_code if(make_qr_code=="True") else False

    def to_yaml(self):
        return {
                "name": f"{self.host_name}",
                "ip": f"{self.ip}",
                "arch": (f"{self.arch}"
                           if (not self.arch is None)
                           else ''),
                "groups": self.groups,
                "note": (f"{self.note}"
                         if (not self.note is None)
                         else ''),
                "deviceCert": (f"{self.device_cert}"
                         if (not self.device_cert is None)
                         else ''),
                "makeQRCode": (f"{self.make_qr_code}"
                         if (not self.make_qr_code is None)
                         else '')
            }

class Yaml_Proxy:
    def __init__(self):
        self.yaml_config = Yaml_Proxy.init_yaml_config()
        self.yaml_file = None

    def init_yaml_config():
        yaml_skeleton = {
            'ca': {
                'name':'',
                'duration':''
            },
            'lighthouse-hosts': [],
            'hosts': []
        }
        return yaml_skeleton
    
    def update_yaml_config(self,cert_domain,cert_duration,lighthouses,hosts):
        lighthouses.sort(key=lambda host: (ip_interface(host.ip)))
        hosts.sort(key=lambda host: (ip_interface(host.ip)))

        self.yaml_config["ca"]["name"] = cert_domain
        self.yaml_config["ca"]["duration"] = cert_duration
        self.yaml_config["lighthouse-hosts"] = list(map(lambda host: host.to_yaml(), lighthouses))
        self.yaml_config["hosts"] = list(map(lambda host: host.to_yaml(), hosts))
    
    def load(self):
        with open(self.yaml_file, 'r') as infile:
            self.yaml_config = load(infile, Loader=yaml.SafeLoader)
            
    def save(self):
        with open(self.yaml_file, 'w') as outfile:
            yaml.dump(self.yaml_config, outfile, Dumper=yaml.SafeDumper, default_flow_style=False, sort_keys=False)
            
    def get_ca_name(self):
        return self.yaml_config["ca"]["name"]
    
    def get_ca_duration(self):
        return self.yaml_config["ca"]["duration"]
    
    def safe_get_attr(self, host, attr):
        try:
            return host[attr]
        except KeyError:
            return None

    
    def get_lighthouses(self):
        lighthouses = []
        for lighthouse in self.yaml_config["lighthouse-hosts"]:
            lighthouses.append(Host(
                lighthouse["name"],
                lighthouse["ip"],
                self.safe_get_attr(lighthouse, "arch"),
                self.safe_get_attr(lighthouse, "groups"),
                self.safe_get_attr(lighthouse, "note"),
                self.safe_get_attr(lighthouse, "deviceCert"),
                self.safe_get_attr(lighthouse, "makeQRCode")
            ))
        return lighthouses
    
    def get_hosts(self):
        hosts = []
        for host in self.yaml_config["hosts"]:
            hosts.append(Host(
                host["name"],
                host["ip"],
                self.safe_get_attr(host, "arch"),
                self.safe_get_attr(host, "groups"),
                self.safe_get_attr(host, "note"),
                self.safe_get_attr(host, "deviceCert"),
                self.safe_get_attr(host, "makeQRCode")
            ))
        return hosts
    
    def to_string(self):
        return yaml.dump(self.yaml_config, default_flow_style=False, sort_keys=False)