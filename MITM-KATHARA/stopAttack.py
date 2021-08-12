import paramiko
from getpass import getpass
import time

host = "202.43.176.5"
port = 22
username = "root"
password = "kathara"

# command = "cd / && ls"

remote_conn_pre = paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(host, port=22, username=username,
                        password=password,
                        look_for_keys=False, allow_agent=False)

remote_conn = remote_conn_pre.invoke_shell()
output = remote_conn.recv(65535)
print(output.decode("utf-8"))

stop_attack_commands = ['vtysh\n', 'conf t\n', 'router bgp 8\n', 'no network 200.7.0.0/24\n', ' no ip route 200.7.0.0 255.255.255.0 216.239.32.1\n', 'no access-list 10 permit 200.7.0.0 255.255.255.0\n',
                        'no route-map toMY-ISP permit 10\n', 'no match ip address 10\n', 'no set as-path prepend 5 1 2\n', 'exit\n', 'router bgp 8\n', 'no neighbor 216.239.32.1 route-map toMY-ISP out \n', 'exit\n', 'exit\n', 'do clear ip bgp *\n']

for stop_attack_command in stop_attack_commands:
    remote_conn.send(stop_attack_command)
    time.sleep(.5)
    output = remote_conn.recv(65535)
    print(output.decode("utf-8"))

# remote_conn.send("vtysh\n")
# time.sleep(.5)
# output = remote_conn.recv(65535)
# print(output.decode("utf-8"))

#remote_conn.send("conf t\n")
# time.sleep(.5)
#output = remote_conn.recv(65535)
#print (output)

# remote_conn.send("exit\n")
# time.sleep(.5)
#output = remote_conn.recv(65535)
#print (output)
