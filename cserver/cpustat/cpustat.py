# -*- coding:utf-8 -*-
###
# File: cpustat.py
# Created Date: Wednesday, November 25th 2020, 9:26:29 pm
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
import psutil
from datetime import datetime

MB = 1024*1024


def query_jdict():
    info_dict = {}
    info_dict["query_time"] = datetime.now()
    memory_info = psutil.virtual_memory()
    info_dict["memory"] = {
        "total": memory_info.total // MB, "used": memory_info.used // MB,
        "free": memory_info.free // MB, "buffers": memory_info.buffers // MB,
        "available": memory_info.available // MB}
    info_dict["cpu_percents"] = psutil.cpu_percent(interval=0.2, percpu=True)
    return info_dict


if __name__ == "__main__":
    cpu_info = query_jdict()
    print(cpu_info)
