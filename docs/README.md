## Nebula Cert Maker

The Nebula Cert Maker is a commandline script will parse a host list yaml file, create a new Nebula CA certificate, and then generate and sign certificates for all hosts in the host list. 

## Nebula Cert Manager

Nebula Cert Manager is a GUI tool to create and edit a yaml host list. It can also generate a new Nebula CA certificate and host certificates.

## NebulaCertMaker.py vs NebulaCertManager.py
NebulaCertManager.py is a useful tool to create your inital host list yaml file and setup your first Nebula mesh VPN. When you are satisfied with your host list, you can use it with NebulaCertMaker.py with your automation and configuration management software (like Ansible) to deploy certificates to your network.

### Equivalent bash commands with NebulaCertManager/NebulaCertMaker

Creating the site certificate.

```bash
$ ./nebula-cert ca -name "domain" -duration "2160h" 
```

Creating the lighthouse certificate

```bash
$ ./nebula-cert sign -name "domain" -ip "192.168.100.1/24"
```

Creating a host certificate

```bash
$ ./nebula-cert sign -ca-crt ./ca.crt -ca-key ./ca.key -name "Hostname" -ip "192.168.100.100/24" -groups "client_devices,admin_group_3,devs"
```

  
Creating a host certificate using a device certificate

```bash
$ ./nebula-cert sign -ca-crt ./ca.crt -ca-key ./ca.key -in-pub host.pub -name "Hostname" -ip "192.168.100.100/24" -groups "client_devices,admin_group_3,devs"
```

Converting a crt file to a QR code

```bash
$ ./nebula-cert print -path ./host.crt -out-qr host_crt.png
```