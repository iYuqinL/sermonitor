# Compute Servers Status Monitor

sers-monitor means Compute Servers Status Monitor.

It is a tool to monitor the compute servers status. The tool consists of two parts: cserver and mserver. 

"cserver" means compute server, it runs on the compute servers. "mserver" means monitor server, it runs on the monitor server.

## Development Details

### cserver details

```bash
cserver
├── config.json  # configuration file, configure the cserver IP, PORT
│                 #and reflesh interval. etc.
├── cpustat      # CPU status module
│   ├── cpustat.py
│   └── __init__.py
├── gpustat      # GPU status module
│   ├── gpustat.py
│   ├── __init__.py
│   └── util.py
├── cserver.py   # top level python script
├── readme.md
└── requirements.txt
```

The cserver is quite simple. For gpustat, it is mainly from the open source project [gpustat](https://github.com/wookayin/gpustat). For cpustat, it is just simply use the pypi module psutil to get cpu information.

And the server and request(register request) are **http server** and **http request**.

### mserver details

```bash
mserver
├── assets           # the web view style source directory
├── dataserver       # the compute server status data server module
│   ├── __init__.py
│   └── server.py
├── ip2name.json     # map the computer server ip to the server name, 
│                     # if the ip is not in the json dict, the web will show
│                     # only the ip of the compute server, but no server name.
├── config.json      # configuration file, configure the cserver IP, PORT
│                     #and reflesh interval. etc.
├── data2dash.py     # the web server and top level of the mserver.
├── readme.md
├── requirements.txt
└── webview_conf.py  # some web view configurations.
```

There are two module in the mserver: dataserver and web server.

The dataserver is to receive the compute servers' status information. It is a http server.

The web server is developed base on the framework named [dash](https://github.com/plotly/dash). I am also new to this framework, so the web server may have a big improvement.