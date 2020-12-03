# -*- coding:utf-8 -*-
###
# File: webview_conf.py
# Created Date: Friday, November 27th 2020, 2:01:50 pm
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
import json
import plotly.graph_objects as go

MiB = 1024*1024

bar_height = 50

gpu_mem_used_marker = dict(
    color='rgba(246, 78, 66, 0.6)',
    line=dict(color='rgba(246, 78, 66, 1.0)', width=3)
)


gpu_mem_free_marker = dict(
    color='rgba(0, 250, 154, 0.6)',
    line=dict(color='rgba(0, 250, 154, 1.0)', width=3)
)

gpu_power_draw_marker = dict(
    color='rgba(205, 91, 69, 0.6)',
    line=dict(color='rgba(205, 91, 69, 1.0)', width=3)
)


gpu_power_lave_marker = dict(
    color='rgba(118, 238, 0, 0.6)',
    line=dict(color='rgba(118, 238, 0, 1.0)', width=3)
)

cpu_mem_used_marker = dict(
    color='rgba(139, 69, 19, 0.6)',
    line=dict(color='rgba(139, 69, 19 1.0)', width=3)
)


cpu_mem_free_marker = dict(
    color='rgba(30, 144, 255, 0.6)',
    line=dict(color='rgba(30, 144, 255, 1.0)', width=3)
)


def load_cfg(cfg_file="config.json"):
    with open(cfg_file) as f:
        cfg = json.load(f)
    return cfg


def load_ip2name(file="ip2name.json"):
    with open(file) as f:
        ip2name = json.load(f)
    return ip2name


gpu_fig_layout = dict(
    barmode='stack', height=80,
    showlegend=False,
    margin={'t': 2, 'b': 1, 'l': 1, 'r': 2}
)

cpu_mem_fig_layout = dict(
    barmode='stack', height=40,
    showlegend=False,
    margin={'t': 2, 'b': 1, 'l': 1, 'r': 2}
)

content_fig_layout = go.Layout(
    barmode='stack', height=10,
    margin={'t': 2, 'b': 1, 'l': 1, 'r': 2},
    xaxis=go.layout.XAxis(
        showticklabels=False),
    yaxis=go.layout.YAxis(showticklabels=False),
    showlegend=False
)
