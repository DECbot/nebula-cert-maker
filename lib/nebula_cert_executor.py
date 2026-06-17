import subprocess
from pathlib import Path
from typing import Iterable

from yaml_proxy import Host

class NebulaCertExecutor:
    def __init__(self, nebula_cert_cmd):
        self.nebula_cert_cmd = nebula_cert_cmd
        self.home_dir = Path.home()
        self.deploy_dir = self.home_dir / "NebulaCertManager" / "deploy"

    def set_destination_dir(self,destitation_dir):
        self.deploy_dir = Path(destitation_dir).resolve()

    def get_destination_dir(self):
        return self.deploy_dir

    def make_ca_cert(self, name, duration):
        try:
            subprocess.run([self.nebula_cert_cmd, "ca", 
                            "-name", name, 
                            "-duration", duration,
                            "-out-crt", f"ca_{name}.crt",
                            "-out-key", f"ca_{name}.key",
                            "-out-qr",  f"ca_{name}.png"], 
                           cwd=self.deploy_dir,
                           capture_output=True,
                           text=True,
                           check=True
                           )
        except FileNotFoundError as e:
            raise e
        except subprocess.CalledProcessError as e:
            raise Exception(f"{e.stderr.strip()}")
        except Exception as e:
            raise e

    def sign_host(self, host: Host, cert_domain):
        groups_str = None
        if isinstance(host.groups, Iterable): groups_str = ",".join(host.groups)

        try:
            # print(self.nebula_cert_cmd, "sign", # TODO: remove this
            #     "-ca-crt",f"ca_{cert_domain}.crt",
            #     "-ca-key", f"ca_{cert_domain}.key", 
            #     "-name", host.host_name, 
            #     "-ip", host.ip, 
            #     *(["-groups", groups_str]
            #         if (groups_str != None)
            #         else []),
            #     *(["-in-pub", host.device_cert] 
            #         if (host.device_cert != None) 
            #         else []), 
            #     *(["-out-qr", (host.host_name+".png")]
            #         if (host.make_qr_code == "True")
            #         else []))
            subprocess.run([self.nebula_cert_cmd, "sign", 
                            "-ca-crt",f"ca_{cert_domain}.crt",
                            "-ca-key", f"ca_{cert_domain}.key", 
                            "-name", host.host_name, 
                            "-ip", host.ip, 
                            *(["-groups", groups_str]
                                if (groups_str != None)
                                else []),
                            *(["-in-pub", host.device_cert] 
                                if (host.device_cert != None) 
                                else []), 
                            *(["-out-qr", (host.host_name+".png")]
                                if (host.make_qr_code == "True")
                                else [])],
                            cwd=self.deploy_dir,
                            capture_output=True,
                            text=True,
                            check=True
                        )
            return True
        except FileNotFoundError as e:
            raise e
        except subprocess.CalledProcessError as e:
            raise Exception(f"{e.stderr.strip()}")
        except Exception as e:
            raise e

    def generate_certs(self, cert_domain, cert_duration, lighthouses, hosts):
        try:
            self.deploy_dir.mkdir(parents=True, exist_ok=True)
            self.make_ca_cert(cert_domain, cert_duration)
            
            for lighthouse in lighthouses:
                self.sign_host(
                    lighthouse,
                    cert_domain
                )
            
            for host in hosts:
                self.sign_host(
                    host,
                    cert_domain
                )
            return True
        except FileExistsError as e:
            raise e
        except subprocess.CalledProcessError as e:
            raise e
        except Exception as e:
            raise e
