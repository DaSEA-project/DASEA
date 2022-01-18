# DASEA

[![Go Build](https://github.com/heyjoakim/DASEA/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/heyjoakim/DASEA/actions/workflows/build.yml) [![Go Report Card](https://goreportcard.com/badge/github.com/heyjoakim/dasea)](https://goreportcard.com/report/github.com/heyjoakim/dasea)

**Da**ta for **S**oftware **E**cosystem **A**nalysis (DASEA)

A continuously updated dataset of software dependencies covering various package manager ecosystems.

Current:

- Conan
- Fpm
- Vcpkg

Access datasets at [DASEA](https://heyjoakim.github.io/DASEA/)

## Executables

### Generate csv files locally

```bash
go run main.go packageManagerName
```

### Create .env file

```bash
cp .env.example .env
```

Populate the .env file with your Zenodo API ACCESS_TOKEN key, where you want the dataset to be published. You can create one [here](https://zenodo.org/account/settings/applications/tokens/new/)

### Publish a new dataset

After you generate the csv files for the package managers, to publish the final dataset, run:

```bash
go run main.go publish-dataset

```

# Contribute

See [CONTRIBUTE.md](https://github.com/heyjoakim/DASEA/blob/main/CONTRIBUTE.md) file

# License

Licensed by the [GNU Affero General Public License v3.0](https://github.com/heyjoakim/DASEA/blob/main/LICENSE)

# Jekyll Homepage

- Follow the [Jekyll installation guide](https://jekyllrb.com/docs/installation/)
- cd into the docs folder
- Run the docs locally:

```bash
  bundle exec jekyll serve
```

Note: if you get a webrick-related [error](https://github.com/jekyll/jekyll/issues/8523), run `bundle add webrick`


------------------------------------

# Mining in General

Every ecosystem that can be mined remotely, i.e., by sending requests to web-APIs, text mining in cloned remote repositories, etc., can be mined directly on a Linux/Unix host.

Requirements are:

  * Python >= 3.9
  * Poetry setup

The following three steps have to be executed only once initially.

```bash
$ git clone https://...
$ cd <DASEA>
$ poetry install
```

The latter command installs 
Eventually, we will distribute DASEA as a Python package via PyPI.



## Alire

Alire is the [Ada Library Repository](https://alire.ada.dev/)

```bash
$ poetry shell
[poetry]$ dasea mine alire
```

## Conan

Conan is the [Ada Library Repository](https://alire.ada.dev/)
Mining Conan packages takes approximately an hour.

```bash
$ poetry shell
[poetry]$ dasea mine conan
```

## Nimble

Nimble is [Nim's package manager](https://github.com/nim-lang/nimble)

```bash
$ dasea mine nimble
```

## BSD Packages

Mining of the respective packages takes place in Virtualbox virtual machines that are managed with Vagrant.
That is, on the host machine VirtualBox, Vagrant, and the Vagrant plugins SCP and reload have to be installed.


### Mining FreeBSD Ports

Mining the Makefiles of the FreeBSD ports tree takes approximately an hour.

```bash
$ vagrant up freebsd11
$ bash bin/get_freebsd_ports.sh
```


### Mining OpenBSD Ports

```bash
$ vagrant up openbsd69
$ bash bin/get_openbsd_ports.sh
```

### Mining NetBSD PkgSrc

Mining the Makefiles of the PkgSrc Makefiles takes in between 3.5 to 5 hours, depending on the host machine.

```bash
$ vagrant up netbsd9
$ bash bin/get_netbsd_pkgsrc.sh
```



