import re
import yaml_proxy as yp

# Not necessary for the tool, but added for configuration management tools 
# (like ansible) to share the yaml file, identifying the architecture to select
# the right nebula architecture if the package is not available in the package 
# repo
# 
# offical release architectures as of 2026.06.10 
# from https://github.com/slackhq/nebula/releases/tag/v1.10.3
NEBULA_ARCH = (
    "",
    "nebula-darwin",
    "nebula-freebsd-amd64",
    "nebula-freebsd-arm64",
    "nebula-linux-386",
    "nebula-linux-amd64",
    "nebula-linux-arm-5",
    "nebula-linux-arm-6",
    "nebula-linux-arm-7",
    "nebula-linux-arm64",
    "nebula-linux-loong64",
    "nebula-linux-mips-softfloat",
    "nebula-linux-mips",
    "nebula-linux-mips64",
    "nebula-linux-mips64le",
    "nebula-linux-mipsle",
    "nebula-linux-ppc64le",
    "nebula-linux-riscv64",
    "nebula-netbsd-amd64",
    "nebula-netbsd-arm64",
    "nebula-openbsd-amd64",
    "nebula-openbsd-arm64",
    "nebula-windows-amd64",
    "nebula-windows-arm64 ",
    "nebula-android",
    "nebula-iOS"
    )

def parse_duration(str):
        if(re.fullmatch(r"[+=]?\d+h", str)):
            return str
        if(str.isdigit()):
            return f"{str}h"
        return f"invalid duration: {str}" # we know this will cause certificate generation exeptions, we will hint now and will prompt user later

class Core:
    def __init__(self):
        self.yaml_proxy = yp.Yaml_Proxy()
        self.cert_domain = []
        self.cert_duration = []
        self.lighthouses = []
        self.hosts = []

    def open_config(self,file_path):
        if file_path:
            self.yaml_proxy.yaml_file = file_path
            self.yaml_proxy.load()
        
        self.cert_domain = self.yaml_proxy.get_ca_name()
        self.cert_duration = self.yaml_proxy.get_ca_duration()
        
        self.lighthouses.clear()
        self.hosts.clear()

        self.lighthouses.extend(self.yaml_proxy.get_lighthouses())
        self.hosts.extend(self.yaml_proxy.get_hosts())

    def write_config_to_yaml(self):
        if self.yaml_proxy.yaml_file:
            self.yaml_proxy.update_yaml_config(
                self.cert_domain,
                self.cert_duration,
                self.lighthouses,
                self.hosts)
            self.yaml_proxy.save()




    

