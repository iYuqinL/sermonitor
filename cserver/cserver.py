# -*- coding:utf-8 -*-
###
# File: cserver.py
# Created Date: Wednesday, November 25th 2020, 4:54:17 pm
# Author: yusnows
# -----
# Last Modified:
# Modified By:
# -----
# Copyright (c) 2020 yusnows
#
# All shall be well and all shall be well and all manner of things shall be well.
# Nope...we're doomed!
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###
import time
import json
import requests
import cpustat
import gpustat


from threading import Thread, Lock
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError(type(obj))


class Monitor(object):
    def __init__(self, cfg: dict) -> None:
        self.cserver_addr = cfg["cserver_addr"]
        self.cserver_port = cfg["cserver_port"]
        self.mserver_addr = cfg["mserver_addr"]
        self.mserver_port = cfg["mserver_port"]
        self.mserver_url = "http://%s:%d" % (self.mserver_addr, self.mserver_port)
        self.check_interval = cfg["check_interval"]
        self.registed = False
        self.registed_time = 0
        self.regis_lock = Lock()
        self.info_request = True
        self.info_request_lock = Lock()

    def collate_info(self):
        cpu_info = cpustat.query_jdict()
        gpu_info = gpustat.query_jdict()
        server_info = {"cpu": cpu_info, "gpu": gpu_info}
        return server_info

    def jdict_info2str(self, info_dict):
        info_str = json.dumps(info_dict, default=date_handler)
        return info_str

    # def request_service(self):
    #     server = HTTPServer(self.cserver_addr, self.cserver_port, InfoRequestHandler(self))
    #     print("监听服务开启， 按<Ctrl-C>退出")
    #     server.serve_forever()

    def check_regi_in_mserver(self):
        info = {"check_regi": self.cserver_addr}
        info_str = json.dumps(info)
        if self.mserver_url is None or self.mserver_url == "":
            print(info_str)
        else:
            try:
                response = requests.get(self.mserver_url, data=info_str)
                if response.status_code == 200:
                    self.regis_lock.acquire()
                    self.registed == True
                    self.registed_time = time.time()
                    self.regis_lock.release()
                elif response.status_code == 201:
                    print("warning: sending address differ from slaver address")
                elif response.status_code == 202:
                    print(
                        "the service on mserver port [%d] only support check_regi and cserver_info" %
                        (self.mserver_port))
                else:
                    print("mserver get a not check_regi request")
            except Exception as e:
                self.regis_lock.acquire()
                self.registed_time = 0
                self.registed = False
                self.regis_lock.release()
                print("exception", e)

    def monitor(self):
        info_str = self.jdict_info2str({"cserver_info": self.collate_info()})
        if self.mserver_url is None:
            print(info_str)
        else:
            try:
                response = requests.get(self.mserver_url, data=info_str)
                if response.status_code == 200:
                    self.regis_lock.acquire()
                    self.registed_time = time.time()
                    self.registed = True
                    self.regis_lock.release()
                elif response.status_code == 301:
                    self.regis_lock.acquire()
                    self.registed_time = 0
                    self.registed = False
                    self.regis_lock.release()
                    print("warning: cserver address not registed")
                else:
                    print("erro: in monitor; the service on this port only support check_regi and cserver_info")
            except Exception as e:
                self.regis_lock.acquire()
                if time.time() - self.registed_time > 5 * self.check_interval:
                    self.registed_time = 0
                    self.registed = False
                self.regis_lock.release()
                print("exception", e)
        self.info_request_lock.acquire()
        self.info_request = False
        self.info_request_lock.release()

    def run(self):
        # self.request_service_thread = Thread(target=self.request_service, args=(self))
        while True:
            if self.registed is False:
                self.check_regi_in_mserver()
            if self.info_request:
                self.monitor()
            time.sleep(self.check_interval)
            self.regis_lock.acquire()
            if time.time() - self.registed_time > 5*self.check_interval:
                self.registed = False
                self.registed_time = 0
            self.regis_lock.release()


class InfoRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        length = int(self.headers['content-length'])
        info = json.loads(self.rfile.read(length).decode())
        if "request_info" in info:
            slaver_addr, _ = self.client_address
            if slaver_addr != monitor.mserver_addr:
                print("warning: request_info from [%s] differ from mserver address [%s]" %
                      (slaver_addr, monitor.mserver_addr))
                self.send_response(
                    501, "warning: request_info from [%s] differ from mserver address [%s]" %
                    (slaver_addr, monitor.mserver_addr))
            else:
                cserver_addr = info["request_info"]
                if cserver_addr != monitor.cserver_addr:
                    print("warning: request_info for [%s] differ from self cserver address [%s]" %
                          (cserver_addr, monitor.cserver_addr))
                    self.send_response(
                        502, "warning: request_info for [%s] differ from self cserver address [%s]" %
                        (cserver_addr, monitor.cserver_addr))
                else:
                    monitor.info_request_lock.acquire()
                    monitor.info_request = True
                    monitor.info_request_lock.release()
                    self.send_response(200)
        else:
            print("erro: in GET; the service on this port noly support request_info")
            self.send_response(503, "erro: the service on this port noly support request_info")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        return


def request_service(monitor: Monitor):
    print(monitor.cserver_addr, monitor.cserver_port)
    # args_v = (monitor.cserver_addr, monitor.cserver_port)
    # kwargs_v = {"monitor": monitor}
    server = HTTPServer((monitor.cserver_addr, monitor.cserver_port), InfoRequestHandler)
    print("监听服务开启， 按<Ctrl-C>退出")
    server.serve_forever()


def load_cfg(cfg_file="config.json"):
    with open(cfg_file) as f:
        cfg = json.load(f)
    return cfg


if __name__ == "__main__":
    cfg = load_cfg()
    monitor = Monitor(cfg)
    rservice_thread = Thread(target=request_service, args=(monitor,))
    rservice_thread.start()
    monitor.run()
