## Nebula Cert Maker

The Nebula Cert Maker will create a new Nebula CA certificates and then generate and sign certificates for all hosts in the host list. 

## Equivalent bash commands

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