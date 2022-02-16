# Setup DaSEA tool

## ❗ Prerequisites

- 🐍 Python >= 3.9, for example installed via [pyenv](https://github.com/pyenv/pyenv)
- [Poetry](https://python-poetry.org/docs/)
- Vagrant, see [Vagrant installation file](https://github.com/dependulum/DASEA/blob/main/docs/setup_vagrant.md). For miners running in virtual machines, which are currently the ports and pkgsrc miners on BSDs, vagrant and VirtualBox have to be installed
- To release the dataset, `tar` and `bzip2` have to be installed and users need a Zenodo API token.

## 📚 Installation

After cloning the repository, run the following command:

```bash
poetry install
```

## 📝 Usage locally

For miners that do not require a VM, you can mine by running the following command:

```bash
poetry run dasea mine nameOfPackageManager
```

## 📝 Usage in Vagrant

Some ecosystem miners, e.g., those mining BSD ports and NetBSD pkgsrc have to be run on the respective BSD OS.
Therefore, in these cases mining takes place in Virtualbox virtual machines that are managed with Vagrant. See our [Vagrant installation file](https://github.com/dependulum/DASEA/blob/main/docs/setup_vagrant.md) if you have not setup Vagrant yet.

Once setup, the available miners can be run by running the commands in the [creade_dataset.sh](https://github.com/dependulum/DASEA/blob/main/bin/create_dataset.sh)

## 🤖 Available commands

All available miner commands can be found [here](https://github.com/dependulum/DASEA/blob/main/docs/available_commands.adoc)

## 📄 Run formatter

```bash
poetry run black -l 120 --check ./dasea
```

## 🧪 Run tests

```bash
poetry run pytest tests
```
