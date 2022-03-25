# -*- coding:utf-8 -*-
###
# File: server.py
# Created Date: Thursday, November 26th 2020, 1:46:40 pm
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
import copy
import requests
from threading import Thread, Lock
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

__all__ = ["data_fetchor", "start_dataservice"]


class DataFetchServer(object):
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.mserver_addr = cfg["mserver_addr"]
        self.mserver_port = cfg["mserver_port"]
        self.cserver_port = cfg["cserver_port"]
        self.request_interval = cfg["request_interval"]
        self.cserver_addrs = []
        self.cserver_addrs_time = {}
        self.caddr_lock = Lock()
        self.cserver_info = {}
        self.cserver_info_time = {}
        self.cinfo_lock = Lock()

    def request_info(self):
        self.caddr_lock.acquire()
        cserver_addrs = set(copy.deepcopy(self.cserver_addrs))
        self.caddr_lock.release()
        for cserver_addr in cserver_addrs:
            cserver_url = "http://%s:%d" % (cserver_addr, self.cserver_port)
            info = {"request_info": cserver_addr}
            info_str = json.dumps(info)
            try:
                response = requests.get(cserver_url, data=info_str)
                if response.status_code == 200:
                    self.caddr_lock.acquire()
                    self.cserver_addrs_time[cserver_addr] = time.time()
                    self.caddr_lock.release()
                elif response.status_code == 501:
                    print("warning: request_info from differ from mserver address")
                    self.cinfo_lock.acquire()
                    if (((time.time()-self.cserver_info_time[cserver_addr]) >
                         5*self.request_interval) and
                            (cserver_addr in self.cserver_info)):
                        self.cserver_info.pop(cserver_addr)
                        self.cserver_info_time.pop(cserver_addr)
                    self.cinfo_lock.release()
                elif response.status_code == 502:
                    print("warning: request_info for addres differ from cserver address")
                    self.caddr_lock.acquire()
                    cserver_addr_time = self.cserver_addrs_time[cserver_addr]
                    if ((time.time()-cserver_addr_time) > 5*self.request_interval):
                        self.cserver_addrs.remove(cserver_addr)
                        self.cserver_addrs_time.pop(cserver_addr)
                    self.caddr_lock.release()
                    self.cinfo_lock.acquire()
                    if (((time.time()-self.cserver_info_time[cserver_addr]) >
                         5*self.request_interval)
                            and (cserver_addr in self.cserver_info)):
                        self.cserver_info.pop(cserver_addr)
                        self.cserver_info_time.pop(cserver_addr)
                    self.cinfo_lock.release()
                else:
                    print(("erro: in request; the service on cserver port"
                           " [%d] noly support request_info" % self.cserver_port))
            except Exception as e:
                if cserver_addr in self.cserver_addrs_time:
                    self.caddr_lock.acquire()
                    cserver_addr_time = self.cserver_addrs_time[cserver_addr]
                    if (time.time() - cserver_addr_time) > 5*self.request_interval:
                        self.cserver_addrs.remove(cserver_addr)
                        self.cserver_addrs_time.pop(cserver_addr)
                        if cserver_addr in self.cserver_info:
                            self.cinfo_lock.acquire()
                            self.cserver_info.pop(cserver_addr)
                            self.cserver_info_time.pop(cserver_addr)
                            self.cinfo_lock.release()
                    self.caddr_lock.release()
                print("exception", e)

    def request_info_loop(self):
        while True:
            # print("request")
            self.request_info()
            time.sleep(self.request_interval)
            print(self.cserver_info)

    def return_cserver_info(self):
        self.cinfo_lock.acquire()
        cserver_info = copy.deepcopy(self.cserver_info)
        self.cinfo_lock.release()
        return cserver_info

    def return_cserver_info_simple(self):
        self.cinfo_lock.acquire()
        cserver_info = copy.deepcopy(self.cserver_info)
        self.cinfo_lock.release()
        for addr in cserver_info:
            cinfo = cserver_info[addr]
            if len(cinfo) > 0 and "gpu" in cinfo and "cpu" in cinfo:
                cinfo_gpus = cinfo["gpu"]["gpus"]
                for cinfo_gpu in cinfo_gpus:
                    del cinfo_gpu["uuid"]
                    del cinfo_gpu["utilization.gpu"]
                    del cinfo_gpu["utilization.enc"]
                    del cinfo_gpu["utilization.dec"]
                    for process in cinfo_gpu["processes"]:
                        process.pop("full_command")
        return cserver_info


class DataFetchHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        length = int(self.headers['content-length'])
        info = json.loads(self.rfile.read(length).decode())
        if "check_regi" in info:
            read_addr = info["check_regi"]
            slaver_addr, _ = self.client_address
            if read_addr == slaver_addr:
                data_fetchor.caddr_lock.acquire()
                if slaver_addr not in data_fetchor.cserver_addrs:
                    data_fetchor.cserver_addrs.append(slaver_addr)
                    data_fetchor.cserver_addrs_time[slaver_addr] = time.time()
                    print("register [%s] succesfully" % slaver_addr)
                    self.send_response(200, "regitster %s successfully" % slaver_addr)
                else:
                    self.send_response(
                        200, "address %s haved already registered" % slaver_addr)
                data_fetchor.caddr_lock.release()
            else:
                print(
                    "warning: sending address [%s] differ from slaver address [%s]" %
                    (read_addr, slaver_addr))
                self.send_response(201, "warning: sending address [%s] " % read_addr +
                                   "differ from slaver address [%s]" % slaver_addr)
        elif "cserver_info" in info:
            cserver_info = info["cserver_info"]
            slaver_addr, _ = self.client_address
            data_fetchor.caddr_lock.acquire()
            cserver_addrs = copy.deepcopy(data_fetchor.cserver_addrs)
            data_fetchor.caddr_lock.release()
            if slaver_addr not in cserver_addrs:
                print("warning: the slaver address is not in cserver_addrs")
                self.send_response(
                    301, "warning: the slaver address is not in cserver_addrs")
            else:
                data_fetchor.cinfo_lock.acquire()
                data_fetchor.cserver_info[slaver_addr] = cserver_info
                data_fetchor.cserver_info_time[slaver_addr] = time.time()
                data_fetchor.cinfo_lock.release()
                self.send_response(
                    200, "fetch info from [%s] successfully" % slaver_addr)
        else:
            print("erro: in GET; the service on this port only support"
                  " check_regi and cserver_info")
            self.send_response(202,
                               "erro: the service on this port only support"
                               " check_regi and cserver_info")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        return


def mservice(data_fecchor):
    print(data_fecchor.mserver_addr, data_fecchor.mserver_port)
    server = HTTPServer(
        (data_fecchor.mserver_addr, data_fecchor.mserver_port),
        DataFetchHandler)
    print("监听服务开启，按<Ctrl-C>退出")
    server.serve_forever()


def request_info_loop(fetchor: DataFetchServer):
    while True:
        # print("request")
        fetchor.request_info()
        time.sleep(fetchor.request_interval)
        # cserver_info = fetchor.return_cserver_info()
        # print(cserver_info)
        # cserver_info_simple = fetchor.return_cserver_info_simple()
        # print(cserver_info_simple)


def load_cfg(cfg_file="config.json"):
    with open(cfg_file) as f:
        cfg = json.load(f)
    return cfg


data_fetchor = DataFetchServer(load_cfg())


def start_dataservice():
    """
    Retruns
    -------
    the services threads
    """
    mservice_thread = Thread(target=mservice, args=(data_fetchor,))
    mservice_thread.start()
    request_thread = Thread(target=request_info_loop, args=(data_fetchor, ))
    request_thread.start()
    return mservice_thread, request_thread


if __name__ == "__main__":
    threads = start_dataservice()
    for thread in threads:
        thread.join()
