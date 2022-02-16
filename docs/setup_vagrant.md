# Locally setup Vagrant

## 🍏 MacOS

### Install VirtualBox

Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) for OS X hosts.

!! Make sure to allow VM and Vigrant on MacOS in System Preferences > Security & Privacy

### Install Vagrant

Download and install [Vagrant](https://www.vagrantup.com/downloads).

!! Make sure to allow VM and Vigrant on MacOS in System Preferences > Security & Privacy

### Install Vagrant plugins

```bash
vagrant plugin uninstall vagrant-vbguest
vagrant plugin install vagrant-reload
vagrant plugin install vagrant-scp
```

### Try to connect to any of the Vagrant VMs

See all the VMs in bin/create_dataset.sh or the Vagrant Config file.

!!NB: If you get an error like "The IP address configured for the host-only network is not within the allowed ranges. Please update the address used to be within the allowed ranges and run the command again. Address: 192.168.20.2 Ranges: 192.168.56.0/21", you need to update the Vagrant Config file to allow the IP address. Create touch /etc/vbox/networks.conf with \* 0.0.0.0/0 ::/0 inside of it.

## 🪟 Windows

- To be announced

## 🐧 Linux

- To be announced
