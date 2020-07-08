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




## Master
#### Run l7sdntest
From /home/vagrant/l7sdntest:
```sh
sudo java -jar l7sdntest.jar expcontr **ConfigurationFile (same dir)**
```

#### ryu
Starting ryu:
```sh
ryu-manager ryu.app.ofctl_rest
```

Get the List of all Switches connected to the Ryu-Controller: 
```sh
curl -X GET http://localhost:8080/stats/switches (from master)
curl -X GET http://192.168.206.1:8080/stats/switches (from anywhere else)
```




## ClientHost
Send attack to IDS (For Testing Purposes):
```sh
nmap **ip to ids** (here: 192.168.203.1)
```




## ids/sa1
#### Snort:
Snort Configuration:
```sh
/etc/snort/snort.conf
```

Test Snort Rules:
```sh
sudo snort -T -c /etc/snort/snort.conf -i enp0s9
```

Modify the HOME_NET Variable to reduce false-positive alerts:
```sh
/etc/snort/snort.conf ipvar HOME_NET
```                                    

Start snort: 
```sh
sudo snort -c /etc/snort/snort.conf -Q -i enp0s9:enp0s10 --daq afpacket --daq-mode inline -A unsock
alternative: sudo snort -A console -q -u snort -g snort -c /etc/snort/snort.conf -i enp0s9
```

Example snort rule: 
```sh
alert icmp $EXTERNAL_NET any -> $EXTERNAL_NET any (msg:”Ping”;sid:232;gid:666;rev:5;)
```

Send alert to Wrapper:
```sh
curl -d '{"rate":"1", "misc":""}' -H "Content-Type: application/json" -X POST localhost:5001/attack
```




## fw/sa2
#### firewall
Example firewall rule:
```sh
sudo iptables -A FORWARD -p icmp -j DROP
```




## ddos/sa3




## server




## switch
#### Flows
From ryu_l7sdntest prject:<br>
Run Layer2 Switch: 
````shell script
ryu-manager simple_switch_13.py
````

Connect openvswitch to the Ryu Controller:<br> 
(if the ryu controller runs on the same Host):
````shell script
ovs-vsctl set-controller br0 tcp:127.0.0.1:**portNr from Controller**
````

Test the Connection between OpenvSwitch and the Ryu-Controller:
````shell script
ovs-vsctl show
````
If the Connection is successfull, it will print "is_connected: true" for every Bridge


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
