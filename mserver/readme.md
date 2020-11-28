# mserver

**Compute Servers Monitor on Monitor Server Service**

## install on monitor server

1. copy mserve folder to the monitor server. you can add a user for this monitor service, for example `sermonitor` is the user on the monitor server for this monitor service. put the mserver folder in /home/sermonitor/
2. `cd /home/sermonitor/mserver/`
3. `sudo -H pip3 install -r requirements.txt`
4. change the config.json file. in general, just change the ip address is OK. "mserver_addr" means the monitor server ip address.
5. change the value of User at line 6 in file `mserver.service`. for example sermonitor.
6. `sudo mv cserver.service /etc/systemd/system/`
7. `sudo systemctl daemon-reload`
8. `sudo systemctl enable cserver.service`
9. `sudo service cserver start`
10. `sudo service cserver status`. and you will see the service is runing.

