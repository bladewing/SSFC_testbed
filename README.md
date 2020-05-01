# IDS-Bypass-Instantiation

#### Install ansible: 
From ids-bypass-instantiation:
```sh
/.bootstrap_ansible.sh
```

#### Install Vagrant: 

Todo 

#### Run vagrant:
From ids-bypass-instantiation:(dont do a vagrant reload!!!)
```sh
vagrant up
``` 

#### Run ansible:
From ids-bypass-instantiation/ansible:<br>
Main playbook, do this first: 
```sh
ansible-playbook --inventory-file hosts-vagrant playbook.yml
```   

all Hosts:
```sh
ls *.yml | grep -v playbook.yml | xargs -I % ansible-playbook --inventory-file hosts-vagrant %
```

one Host:
```sh
ansible-playbook --inventory-file hosts-vagrant **host**.yml
```




##Master
####Run l7sdntest
From /home/vagrant/l7sdntest:
```sh
sudo java -jar l7sdntest.jar expcontr **ConfigurationFile (same dir)**
```

####ryu
Starting ryu:
```sh
ryu-manager ryu.app.ofctl_rest
```

Get the List of all Switches connected to the Controller: 
```sh
curl -X GET http://localhost:8080/stats/switches (from master)
curl -X GET http://192.168.206.1:8080/stats/switches (from anywhere else)
```




##ClientHost




##ids/sa1
####Snort:
Start snort: 
```sh
sudo snort -c /etc/snort/snort.conf -Q -i enp0s9:enp0s10 --daq afpacket --daq-mode inline -A unsock
alternative: sudo snort A console
```

Example snort rule: 
```sh
alert icmp $EXTERNAL_NET any -> $EXTERNAL_NET any (msg:”Ping”;sid:232;gid:666;rev:5;)
```

Send alert to Wrapper:
```sh
curl -d '{"rate":"1", "misc":""}' -H "Content-Type: application/json" -X POST localhost:5001/attack
```




##fw/sa2
####firewall
Example firewall rule:
```sh
sudo iptables -A FORWARD -p icmp -j DROP
```




##ddos/sa3




##server




##switch
####Flows
Add a flow from X to Y:
```sh
sudo ovs-ofctl add-flow br0 in_port=X,actions=Y
```

flows:<br>

    client -> FW -> server
    1 -> 6
    5 -> 9
    9 -> 1

    client -> IDS -> server
    1 -> 4
    3 -> 9
    9 -> 1
