# cserver

**Compute Server Monitor on Compute Server Service**

## install on compute server

1. copy cserver folder to the compute server's /opt directory.

2. `cd /opt && sudo chown $(id -u):$(id -g) cserver/ -R && cd /opt/cserver`

3. `sudo -H pip3 install -r requirements.txt`

4. change the config.json file. in general, just change the ip address is OK.
   `mserver_addr` means the monitor server ip address, `cserver_addr` means the compute server itself ip address.

5. change the value of User at line 6 in file cserver.service. it is the user name of the compute server.

6. `sudo mv cserver.service /etc/systemd/system/`

7. `sudo systemctl daemon-reload`

8. `sudo systemctl enable cserver.service`

9. `sudo service cserver start`

10. `sudo service cserver status`. and you will see the service is runing.
