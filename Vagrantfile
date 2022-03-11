Vagrant.configure("2") do |config|

  # TODO: How to handle new OS version?
  # Start FreeBSD VM
  config.vm.define "freebsd11", primary: false do |freebsd|
    freebsd.vm.box = "bento/freebsd-11"

    # Needed on MacOS: https://github.com/dotless-de/vagrant-vbguest/issues/362
    if Vagrant.has_plugin?("vagrant-vbguest")
      config.vbguest.auto_update = false
    end

    # Increase timeout to 10 minutes (600 seconds) to ensure boot on DO droplet
    config.vm.boot_timeout = 600

    # Private network is needed for synced folder to work, see https://www.vagrantup.com/docs/synced-folders/nfs#prerequisites
    freebsd.vm.network "private_network", ip: "192.168.20.2"
    # The two-way synced directories seem to be flaky with the FreeBSD guest.
    # On the first write lower level directories do not exist anymore/are unmounted.
    # Consequently, we fall back to rsync
    # freebsd.vm.synced_folder "./", "/vagrant", type: "virtualbox"
    freebsd.vm.synced_folder "./", "/vagrant", type: "rsync"

    freebsd.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = "2"
    end

    freebsd.vm.hostname = "freebsd11"
    freebsd.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from FreeBSD"

      echo "Setting up BASH as default shell..."
      pkg install -y bash
      chsh -s /usr/local/bin/bash vagrant

      # echo "Setting up Python for dataset creation..."
      pkg install -y python39
      ln -s /usr/local/bin/python3.9 /usr/local/bin/python3

      # Both of the following are needed for lxml, a Python dependency of DaSEA
      pkg install -y libxml2
      pkg install -y libxslt

      echo "Collecting ports tree..."
      # TODO: Use an alternative method to get quartely branch, see
      # https://docs.freebsd.org/en/books/handbook/ports/#ports-using
      portsnap --interactive fetch
      portsnap --interactive extract
    SHELL

    # For some reason extracting the ports tree unmounts the synced dir
    # Consequently, restart the machine here before the next provisioner
    freebsd.vm.provision :reload

    freebsd.vm.provision "shell", privileged: false, inline: <<-SHELL
      echo ". $HOME/.bashrc" >> $HOME/.bash_profile

      curl -sSL https://install.python-poetry.org | python3 -
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc

      mkdir -p /vagrant/data/tmp/ports/freebsd11
      mkdir -p /vagrant/data/out/ports/freebsd11

      cd /vagrant/
      $HOME/.local/bin/poetry install

    SHELL
  end
  # End FreeBSD VM

  # Start OpenBSD VM
  config.vm.define "openbsd69", primary: false do |openbsd|
    openbsd.vm.box = "generic/openbsd6"
    openbsd.vm.network "private_network", ip: "192.168.20.3"
    openbsd.vm.synced_folder "./", "/vagrant", type: "rsync", rsync__exclude: "data/tmp/"
    openbsd.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = "2"
    end

    openbsd.vm.hostname = "openbsd69"
    openbsd.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from OpenBSD"

      echo "Setting up Python for dataset creation..."
      pkg_add python-3.9.7
      ln -s /usr/local/bin/python3.9 /usr/local/bin/python
      pkg_add libxslt

      echo "Collecting ports tree..."
      # https://www.openbsd.org/faq/ports/ports.html#PortsFetch
      cd /tmp
      ftp https://cdn.openbsd.org/pub/OpenBSD/$(uname -r)/{ports.tar.gz,SHA256.sig}
      signify -Cp /etc/signify/openbsd-$(uname -r | cut -c 1,3)-base.pub -x SHA256.sig ports.tar.gz
      cd /usr
      tar xzf /tmp/ports.tar.gz

    SHELL

    openbsd.vm.provision "shell", privileged: false, inline: <<-SHELL
      curl -sSL https://install.python-poetry.org | python -

      mkdir -p /vagrant/data/tmp/ports/openbsd69
      mkdir -p /vagrant/data/out/ports/openbsd69

      cd /vagrant/
      $HOME/.local/bin/poetry install

      # Start the actual mining process
      # $HOME/.local/bin/poetry run dasea mine ports

    SHELL
  end
  # End OpenBSD VM

  # Start NetBSD VM
  config.vm.define "netbsd9", primary: false do |netbsd|
    netbsd.vm.box = "generic/netbsd9"
    netbsd.vm.network "private_network", ip: "192.168.20.4"
    netbsd.vm.synced_folder "./", "/vagrant", type: "rsync", rsync__exclude: "data/tmp/"
    netbsd.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = "2"
    end

    netbsd.vm.hostname = "netbsd9"
    netbsd.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from NetBSD"

      echo "Setting up Python for dataset creation..."
      pkgin -y install python39
      pkgin -y install py39-expat  # A dependency for poetry, which is not installed by default
      ln -s /usr/pkg/bin/python3.9 /usr/pkg/bin/python

      pkgin -y install mozilla-rootcerts
      mozilla-rootcerts install

      echo "Collecting pkgsrc tree..."
      ftp ftp://ftp.NetBSD.org/pub/pkgsrc/current/pkgsrc.tar.gz
      tar -xzf pkgsrc.tar.gz -C /usr
      rm pkgsrc.tar.gz
    SHELL
  end
  # End NetBSD VM

  # Start Conan VM
  config.vm.define "ubuntu2104", primary: false do |ubuntu|
    ubuntu.vm.box = "bento/ubuntu-21.04"
    # To make the two-way sync work, the vbguest plugin has to be installed:
    # vagrant plugin install vagrant-vbguest
    ubuntu.vm.synced_folder "./", "/vagrant", type: "virtualbox"

    ubuntu.vm.provider "virtualbox" do |vb|
      # TODO: Are less resources doable?
      vb.memory = "4096"
      vb.cpus = "2"
    end

    ubuntu.vm.hostname = "ubuntu2104"
    ubuntu.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from Ubuntu 21.04"
      apt update

      # echo "Setting up Python for dataset creation..."
      apt install -y python3 python3.9-venv
      apt install -y gcc make  # Conan needs a C/C++ compiler
    SHELL
    ubuntu.vm.provision "shell", privileged: false, inline: <<-SHELL
      curl -sSL https://install.python-poetry.org | python3 -
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
      source $HOME/.bashrc

      cd /vagrant
      $HOME/.local/bin/poetry install
    SHELL
  end
  # End Conan VM

  # Start Nible VM
  config.vm.define "ubuntu2104oneway", primary: false do |ubuntu|
    ubuntu.vm.box = "bento/ubuntu-21.04"
    # To make the two-way sync work, the vbguest plugin has to be installed:
    # vagrant plugin install vagrant-vbguest
    ubuntu.vm.synced_folder "./", "/vagrant", type: "rsync"

    ubuntu.vm.provider "virtualbox" do |vb|
      # TODO: Are less resources doable?
      vb.memory = "4096"
      vb.cpus = "2"
    end

    ubuntu.vm.hostname = "ubuntu2104oneway"
    # Install needed dependencies
    ubuntu.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from Ubuntu 21.04"
      apt update
      apt install -y python3 python3.9-venv
    SHELL

    # Install Poetry
    ubuntu.vm.provision "shell", privileged: false, inline: <<-SHELL
      curl -sSL https://install.python-poetry.org | python3 -
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
      source $HOME/.bashrc

      cd /vagrant
      $HOME/.local/bin/poetry install
    SHELL

    # Install Nimble
    ubuntu.vm.provision "shell", privileged: true, inline: <<-SHELL
      apt install -y nim
      echo 'export PATH="$HOME/.nimble/bin:$PATH"' >> ~/.bashrc
    SHELL
  end
  # End Nible VM

  # TODO: Create a VM for mining Homebrew on MacOS
end
