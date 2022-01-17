Vagrant.configure("2") do |config|

  # TODO: How to handle new OS version?
  config.vm.define "freebsd11", primary: false do |freebsd|
    freebsd.vm.box = "bento/freebsd-11"
    # Private network is needed for synced folder to work, see https://www.vagrantup.com/docs/synced-folders/nfs#prerequisites
    freebsd.vm.network "private_network", ip: "192.168.20.2"
    # The two-way synced directories seem to be flaky with the FreeBSD guest.
    # On the first write lower level directories do not exist anymore/are unmounted.
    # Consequently, we fall back to rsync
    freebsd.vm.synced_folder "./", "/vagrant", type: "virtualbox"
    # freebsd.vm.synced_folder "./", "/vagrant", type: "rsync"

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

      # Both of the following are needed for lxml, a Python dependency of DASEA
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
      # source $HOME/.bashrc

      mkdir -p /vagrant/data/tmp/ports/freebsd11
      mkdir -p /vagrant/data/out/ports/freebsd11

      cd /vagrant/
      $HOME/.local/bin/poetry install

      # Start the actual mining process
      # $HOME/.local/bin/poetry run dasea mine ports

    SHELL
  end


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

    # netbsd.vm.provision "shell", privileged: false, inline: <<-SHELL      
    #   echo ". $HOME/.bashrc" >> $HOME/.bash_profile
      
    #   curl -sSL https://install.python-poetry.org | python -
    #   echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
    #   source $HOME/.bashrc
      
    #   mkdir -p /vagrant/data/tmp/ports/netbsd9
    #   mkdir -p /vagrant/data/out/ports/netbsd9

    #   cd /vagrant/
    #   $HOME/.local/bin/poetry install

    #   # Start the actual mining process
    #   # $HOME/.local/bin/poetry run dasea mine pkgsrc

    # SHELL
  end


  config.vm.define "haikur1b2", primary: false do |haikuos|
    haikuos.vm.box = "haiku-os/r1beta2-x86_64"
    haikuos.vm.box_version = "20200702"

    # haikuos.vm.network "private_network", ip: "192.168.20.4"
    haikuos.vm.synced_folder "./", "/vagrant", type: "rsync"
    haikuos.vm.provider "virtualbox" do |vb|
      # TODO: Are less resources doable?
      vb.memory = "2048"
      vb.cpus = "2"
      vb.gui = true
      vb.customize ['modifyvm', :id, '--clipboard', 'bidirectional']
    end
   
    haikuos.vm.hostname = "haiku"
    haikuos.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from Haiku"
      #pkgman update
      # Use older Python or do proper update before
      #pkgman install -y python38


      #git clone https://github.com/haikuports/haikuporter.git
      # cp haikuporter/haikuports-sample.conf /boot/home/config/settings/haikuports.conf
      #git clone https://github.com/haikuports/haikuports.git --depth=10
    SHELL
  end

  config.vm.define "pypiminer", primary: false do |pypi|
    pypi.vm.box = 'digital_ocean'
    pypi.vm.box_url = "https://github.com/devopsgroup-io/vagrant-digitalocean/raw/master/box/digital_ocean.box"
    pypi.ssh.private_key_path = '~/.ssh/id_rsa'
    
    pypi.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ["./data/out/*.csv", "./data/out/*.bz2", ".git/", "./data/tmp/", "./data/code/", "./bsds.zip", "*.hpkg"]
    pypi.vm.hostname = "pypiminer"
    
    pypi.vm.provider :digital_ocean do |provider|
      provider.ssh_key_name = ENV["SSH_KEY_NAME"]
      provider.token = ENV["DIGITAL_OCEAN_TOKEN"]
      provider.image = 'ubuntu-18-04-x64'
      provider.region = 'fra1'
      provider.size = 's-1vcpu-1gb'
    end

    pypi.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Setting up Python for dataset creation..."
      apt install python3-pip

      # apt install -y python3.8

      pip3 install requests
      pip3 install ipython
      pip3 install bs4
      pip3 install lxml
      pip3 install html5lib
      pip3 install pandas

      cd /vagrant/
      nohup python3 pypi_main.py > /tmp/pypi.log 2>&1 &

      # nohup python3 clojars_main.py > /tmp/clojars.log 2>&1 &
      #   echo "$ vagrant ssh [machinename]"
    SHELL
  end

  config.vm.define "rubygemsminer", primary: false do |gems|
    gems.vm.box = 'digital_ocean'
    gems.vm.box_url = "https://github.com/devopsgroup-io/vagrant-digitalocean/raw/master/box/digital_ocean.box"
    gems.ssh.private_key_path = '~/.ssh/id_rsa'
    
    gems.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ["./data/out/*.csv", "./data/out/*.bz2", ".git/", "./data/tmp/", "./data/code/", "./bsds.zip", "*.hpkg"]
    gems.vm.hostname = "pypiminer"
    
    gems.vm.provider :digital_ocean do |provider|
      provider.ssh_key_name = ENV["SSH_KEY_NAME"]
      provider.token = ENV["DIGITAL_OCEAN_TOKEN"]
      provider.image = 'ubuntu-18-04-x64'
      provider.region = 'fra1'
      provider.size = 's-1vcpu-1gb'
    end

    gems.vm.provision "shell", privileged: true, inline: <<-SHELL
      apt install -y ruby

      echo "Setting up Python for dataset creation..."
      apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
                     libreadline-dev libsqlite3-dev wget curl llvm \
                     libncurses5-dev libncursesw5-dev xz-utils tk-dev \
                     libffi-dev liblzma-dev python-openssl git

      git clone https://github.com/pyenv/pyenv.git ~/.pyenv

      echo ". $HOME/.bashrc" >> $HOME/.bash_profile
      echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
      echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc

      source ~/.bashrc
      
      eval "$(pyenv init -)"
      pyenv install 3.9.4
      pyenv global 3.9.4

      $HOME/.pyenv/versions/3.9.4/bin/pip install requests
      $HOME/.pyenv/versions/3.9.4/bin/pip install ipython
      $HOME/.pyenv/versions/3.9.4/bin/pip install bs4
      $HOME/.pyenv/versions/3.9.4/bin/pip install lxml


      pip3 install requests
      pip3 install ipython
      pip3 install bs4
      pip3 install lxml

      cd /vagrant/
      nohup $HOME/.pyenv/versions/3.9.4/bin/python rubygems_main.py > /tmp/rubygems.log 2>&1 &
      #   echo "$ vagrant ssh [machinename]"
    SHELL
  end


  config.vm.define "packagistminer", primary: false do |pypi|
    pypi.vm.box = 'digital_ocean'
    pypi.vm.box_url = "https://github.com/devopsgroup-io/vagrant-digitalocean/raw/master/box/digital_ocean.box"
    pypi.ssh.private_key_path = '~/.ssh/id_rsa'
    
    pypi.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ["./data/out/*.csv", "./data/out/*.bz2", ".git/", "./data/tmp/", "./data/code/", "./bsds.zip", "*.hpkg"]
    pypi.vm.hostname = "packagistminer"
    
    pypi.vm.provider :digital_ocean do |provider|
      provider.ssh_key_name = ENV["SSH_KEY_NAME"]
      provider.token = ENV["DIGITAL_OCEAN_TOKEN"]
      provider.image = 'ubuntu-18-04-x64'
      provider.region = 'fra1'
      provider.size = 's-1vcpu-1gb'
    end

    pypi.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Setting up Python for dataset creation..."
      apt install python3-pip 
      # The above installs python3.8 as dependency
      # apt install -y python3.8

      pip3 install requests

      cd /vagrant/
      nohup python3 packagist_main.py > /tmp/packagist.log 2>&1 &

      cd /vagrant/data/out

      tar -cvjf packagist.tar.bz2 packagist_*.csv /tmp/packagist.log
    SHELL
  end


  config.vm.define "mavenminer", primary: false do |maven|
    maven.vm.box = 'digital_ocean'
    maven.vm.box_url = "https://github.com/devopsgroup-io/vagrant-digitalocean/raw/master/box/digital_ocean.box"
    maven.ssh.private_key_path = '~/.ssh/id_rsa'
    
    maven.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ["./data/", ".git/", "./artwork/"]
    maven.vm.hostname = "mavenminer"
    
    maven.vm.provider :digital_ocean do |provider|
      provider.ssh_key_name = ENV["SSH_KEY_NAME"]
      provider.token = ENV["DIGITAL_OCEAN_TOKEN"]
      provider.image = 'ubuntu-18-04-x64'
      provider.region = 'fra1'
      provider.size = 's-1vcpu-1gb'
    end

    maven.vm.provision "shell", privileged: true, inline: <<-SHELL
      apt update
      echo "Setting up Python for dataset creation..."
      
      # DASEA needs a Python 3.9, which we setup via pyenv. The following are 
      # the dependencies to build Python
      apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
                     libreadline-dev libsqlite3-dev wget curl llvm \
                     libncurses5-dev libncursesw5-dev xz-utils tk-dev \
                     libffi-dev liblzma-dev python-openssl git
      git clone https://github.com/pyenv/pyenv.git ~/.pyenv

      echo ". $HOME/.bashrc" >> $HOME/.bash_profile
      echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
      echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
      echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
      source ~/.bashrc

      # Since the above does not seem to work for some reason in the 
      # non-interactive shell, I use the absolute path to pyenv in the following
      /root/.pyenv/bin/pyenv install 3.9.4
      /root/.pyenv/bin/pyenv global 3.9.4

      # TODO: Consider dropping poetry installation on remote by building the
      # DASEA package locally and install the tgz via pip on remote
      curl -sSL https://install.python-poetry.org | python3 -
      echo 'export PATH="/root/.local/bin:$PATH"' >> ~/.bashrc
      source ~/.bashrc

      cd /vagrant/dasea
      mkdir -p data/tmp/maven
      mkdir -p data/out/maven

      /root/.local/bin/poetry install
      # poetry run nohup dasea mine maven >> data/tmp/maven.log 2>&1 &

      apt install -y sqlite3

  
    SHELL
  end




  config.vm.define "ubuntu1804", primary: false do |ubuntu|
    ubuntu.vm.box = "bento/ubuntu-18.04"
    # To make the two-way sync work, the vbguest plugin has to be installed:
    # vagrant plugin install vagrant-vbguest
    ubuntu.vm.synced_folder "./", "/vagrant", type: "virtualbox"

    ubuntu.vm.provider "virtualbox" do |vb|
      # TODO: Are less resources doable?
      vb.memory = "4096"
      vb.cpus = "2"
    end
   
    ubuntu.vm.hostname = "ubuntu1804"
    ubuntu.vm.provision "shell", privileged: true, inline: <<-SHELL
      echo "Hej from Ubuntu 18.04"

      # Include the source packages for each configured binary package
      # repository too, see https://askubuntu.com/a/1212734
      # That leaves out the `partner` repositories, which are not configured by
      # default 
      grep '^deb ' /etc/apt/sources.list | perl -pe 's/deb /deb-src /' >> /etc/apt/sources.list
      
      apt update

      echo "Setting up Python for dataset creation..."
      
      # DASEA needs a Python 3.9, which we setup via pyenv. The following are 
      # the dependencies to build Python
      apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
                     libreadline-dev libsqlite3-dev wget curl llvm \
                     libncurses5-dev libncursesw5-dev xz-utils tk-dev \
                     libffi-dev liblzma-dev python-openssl git

      # The following is needed to find all 
      apt install -y aptitude

    SHELL
    ubuntu.vm.provision "shell", privileged: true, inline: <<-SHELL
      git clone https://github.com/pyenv/pyenv.git ~/.pyenv

      echo ". $HOME/.bashrc" >> $HOME/.bash_profile
      echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
      echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
      echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
      source $HOME/.bashrc
      source $HOME/.bash_profile

      # Since the above does not seem to work for some reason in the 
      # non-interactive shell, I use the absolute path to pyenv in the following
      $HOME/.pyenv/bin/pyenv install 3.9.4
      $HOME/.pyenv/bin/pyenv global 3.9.4

      # TODO: Consider dropping poetry installation on remote by building the
      # DASEA package locally and install the tgz via pip on remote
      curl -sSL https://install.python-poetry.org | python3 -
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
      source $HOME/.bashrc

      mkdir -p /vagrant/data/tmp/ubuntu
      mkdir -p /vagrant/data/tmp/ubuntu/versions_db
      mkdir -p /vagrant/data/out/ubuntu

      cd /vagrant
      $HOME/.local/bin/poetry install
      SHELL

  end

  # TODO: Create a VM for mining Homebrew on MacOS
end
