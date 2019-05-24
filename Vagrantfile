Vagrant.configure("2") do |config|

  config.vm.define "master" do |master|
    master.vm.box = "ubuntu/bionic64"
    master.vm.hostname = "master"
    master.vm.network "private_network", ip: "192.168.42.2", virtualbox__intnet: "management"
    master.vm.network "forwarded_port", guest: 8888, host: 8888
    playbook = 'master'
    master.vm.provision "#{playbook}", type: "ansible" do |ansible|
      ansible.playbook = "ansible/#{playbook}.yml"
    end
  end

  config.vm.define "client" do |client|
    client.vm.box = "ubuntu/bionic64"
    client.vm.hostname = "client"
    client.vm.network "private_network", ip: "192.168.42.10", virtualbox__intnet: "management"
    client.vm.network "private_network", ip: "192.168.43.10", virtualbox__intnet: "client2switch"
    playbook = 'client'
    client.vm.provision "#{playbook}", type: "ansible" do |ansible|
      ansible.playbook = "ansible/#{playbook}.yml"
    end
  end

  config.vm.define "eve" do |eve|
    eve.vm.box = "ubuntu/bionic64"
    eve.vm.hostname = "eve"
    eve.vm.network "private_network", ip: "192.168.42.30", virtualbox__intnet: "management"
    eve.vm.network "private_network", ip: "192.168.43.30", virtualbox__intnet: "eve2switch"
    playbook = 'eve'
    eve.vm.provision "#{playbook}", type: "ansible" do |ansible|
      ansible.playbook = "ansible/#{playbook}.yml"
    end
  end

  config.vm.define "ids" do |ids|
    ids.vm.box = "ubuntu/bionic64"
    ids.vm.hostname = "ids"
    ids.vm.network "private_network", ip: "192.168.42.50", virtualbox__intnet: "management"
    ids.vm.network "private_network", ip: "192.168.43.50", virtualbox__intnet: "ids2switch"
    playbook = 'ids'
    ids.vm.provision "#{playbook}", type: "ansible" do |ansible|
      ansible.playbook = "ansible/#{playbook}.yml"
    end
  end

  config.vm.define "server" do |server|
    server.vm.box = "ubuntu/bionic64"
    server.vm.hostname = "server"
    server.vm.network "private_network", ip: "192.168.42.60", virtualbox__intnet: "management"
    server.vm.network "private_network", ip: "192.168.43.60", virtualbox__intnet: "server2switch"
    playbook = 'server'
    server.vm.provision "#{playbook}", type: "ansible" do |ansible|
      ansible.playbook = "ansible/#{playbook}.yml"
    end
  end

  config.vm.define "switch" do |switch|
    switch.vm.box = "ubuntu/bionic64"
    switch.vm.network "private_network", ip: "192.168.42.3", virtualbox__intnet: "management"
    switch.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "client2switch"
    switch.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "eve2switch"
    switch.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "ids2switch"
    switch.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "server2switch"
    playbook = 'switch'
    switch.vm.provision "#{playbook}", type: "ansible" do |ansible|
      ansible.playbook = "ansible/#{playbook}.yml"
    end
  end
end
