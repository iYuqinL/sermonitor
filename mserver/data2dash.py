# -*- coding:utf-8 -*-
###
# File: dash.py
# Created Date: Thursday, November 26th 2020, 10:03:58 pm
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
import copy
from dataserver import data_fetchor, start_dataservice
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import pandas as pd
from webview_conf import *

cfg = load_cfg()
ip2name = load_ip2name()

app = dash.Dash("visg compute servers monitor")
# app = dash.Dash("compute servers monitor")
app.title = "VISG Compute Servers Monitor"

app.layout = html.Div(
    className="container",
    children=[
        html.Div(id='top-margin', style={"height": 80}),
        html.H1(children="VISG Compute Servers Monitor",
                style={'textAlign': 'center'}),
        html.Div(id='tile-b-margin', style={"height": 30}),
        html.Div(
            className="row",
            children=[html.Div(id="contentsTab", className="two columns"),
                      html.Div(id="serverGraphs", className="ten columns"), ],
            id="columns-row"),
        html.Div(id='bottom-margin', style={"height": 120}),
        dcc.Interval(
            id="update-timer", interval=cfg["dash_interval"] * 1000,
            n_intervals=0),
    ])


def generate_process_table(processes: list):
    process_keys = ["username", "pid", "command", "gpu_memory_usage",
                    "cpu_memory_usage", "full_command"]
    for process in processes:
        fcmd = ""
        for cmd_phase in process["full_command"]:
            fcmd += cmd_phase + " "
        process["full_command"] = fcmd
    # processes = copy.deepcopy(processes)
    filter_out_user = ["gdm", "xorg", "Xorg"]
    filter_out_command = ["Xorg", "xorg", "TeamViewer"]
    processes = list(filter(
        lambda x: ((x["username"] not in filter_out_user) and
                   (x["command"] not in filter_out_command)), processes))
    processes.sort(key=lambda x: x["gpu_memory_usage"], reverse=True)
    # return html.Dash([
    #     html.Thead(html.Tr([html.Th(key) for key in process_keys])),
    #     html.Tbody([html.Tr([html.Td(processes[i][key]) for key in process_keys])
    #                 for i in range(len(processes))])])
    datatable = dash_table.DataTable(
        data=processes, columns=[{'id': c, 'name': c} for c in process_keys],
        fixed_rows={'headers': True},
        style_as_list_view=True,
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell={'minWidth': 90, 'height': 'auto', 'whiteSpace': 'normal',
                    'textAlign': 'center'},
        style_cell_conditional=[
            {'if': {'column_id': 'full_command'}, 'textAlign': 'left'},
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        page_size=2,)
    return datatable


def sort_addr_by_ip2name(cinfos, ip2name):
    sorted_addrs = []
    for addr in ip2name["self_order"]:
        if addr in cinfos:
            sorted_addrs.append(addr)
    for addr in cinfos:
        if addr not in sorted_addrs:
            sorted_addrs.append(addr)
    return sorted_addrs


@app.callback(
    Output("contentsTab", "children"),
    Output("serverGraphs", "children"),
    [Input("update-timer", "n_intervals")])
def update_all_graph(n_intervals):
    cinfos = data_fetchor.return_cserver_info()
    sorted_addrs = sort_addr_by_ip2name(cinfos, ip2name)
    all_html_divs = []
    all_contents = [html.H5("Severs List")]
    for server in sorted_addrs:
        cinfo = cinfos[server]
        html_divs = []
        gpu_contents = []
        server_name = "%s: %s" % (
            server, ip2name[server]) if server in ip2name else server
        html_divs.append(html.H3(server_name))
        gpus_info = cinfo["gpu"]["gpus"]
        gpus_div = []
        for gpu_info in gpus_info:
            gpu_div = []
            gpu_div.append(
                html.H5(("%s - %d (%s)" % (
                    gpu_info["name"], gpu_info["index"],
                    cinfo["gpu"]["query_time"]))))
            fig = make_subplots(rows=2, cols=1, row_heights=[0.5, 0.5])
            fig.add_trace(
                go.Bar(
                    y=["power"], x=[gpu_info["power.draw"]],
                    name="draw", orientation='h', width=0.6,
                    marker=gpu_power_draw_marker),
                row=2, col=1)
            fig.add_trace(
                go.Bar(
                    y=["power"],
                    x=[gpu_info["enforced.power.limit"] - gpu_info["power.draw"]],
                    name="lave", orientation='h', width=0.6,
                    marker=gpu_power_lave_marker),
                row=2, col=1,)
            fig.add_trace(
                go.Bar(y=["gmem"], x=[gpu_info["memory.used"]], name="used",
                       orientation='h', width=0.6, marker=gpu_mem_used_marker),
                row=1, col=1,)
            fig.add_trace(
                go.Bar(
                    y=["gmem"],
                    x=[(gpu_info["memory.total"] - gpu_info["memory.used"])],
                    name="free", orientation='h', width=0.6,
                    marker=gpu_mem_free_marker),
                row=1, col=1)
            fig.update_layout(**gpu_fig_layout)
            fig.update_xaxes(side="top", row=1, col=1)
            # fig.update_yaxes(showticklabels=False)
            gpu_div.append(html.Div(
                id="%sgpu%ddiv" %
                (server.replace(".", ""),
                 gpu_info["index"]),
                children=[dcc.Graph(
                    id="%sgpu%d" % (server.replace(".", ""), gpu_info["index"]),
                    figure=fig,
                    config={'displayModeBar': False})]))
            gpu_div.append(
                html.Div(
                    children=[html.H6(
                        "Processes on %s - %d" % (gpu_info["name"], gpu_info["index"])),
                        generate_process_table(gpu_info["processes"])],
                    style={"margin-left": 30}))
            gpus_div.append(html.Div(gpu_div))
            # content_fig = make_subplots(rows=1, cols=1)
            content_fig = go.Figure(layout=content_fig_layout)
            content_fig.add_trace(
                go.Bar(y=["gmem"], x=[gpu_info["memory.used"]], name="used",
                       orientation='h', width=0.8, marker=gpu_mem_used_marker))
            content_fig.add_trace(
                go.Bar(
                    y=["gmem"],
                    x=[(gpu_info["memory.total"] - gpu_info["memory.used"])],
                    name="free", orientation='h', width=0.8,
                    marker=gpu_mem_free_marker))
            name_len = len(gpu_info["name"])
            link_name = gpu_info["name"] if name_len <= 20 else gpu_info["name"][
                : 9] + "..." + gpu_info["name"]
            gpu_contents.append(html.A(
                [html.Div(
                    link_name, style={"font-size": "0.8em"}),
                 dcc.Graph(
                    id="content%sgpu%d" %
                    (server.replace(".", ""),
                     gpu_info["index"]),
                    figure=content_fig,
                    config={'displayModeBar': False})],
                href="#%sgpu%ddiv" %
                (server.replace(".", ""),
                 gpu_info["index"])))
        html_divs.append(html.Div(gpus_div, style={"margin-left": 20, }))
        cpu_info = cinfo["cpu"]
        cpu_div = []
        cpu_div.append(html.Div(
            html.H5("CPU: %d logic cores (%s)" % (
                len(cpu_info["cpu_percents"]), cpu_info["query_time"])),
            style={"margin-top": "30px"}))
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(
            go.Bar(
                y=["memory"],
                x=[cpu_info["memory"]["used"]],
                name="used", orientation='h', width=0.6,
                marker=cpu_mem_used_marker),
            row=1, col=1)
        fig.add_trace(
            go.Bar(
                y=["memory"],
                x=[cpu_info["memory"]["available"]],
                name="avail", orientation='h', width=0.6,
                marker=cpu_mem_free_marker),
            row=1, col=1)
        fig.update_layout(**cpu_mem_fig_layout)
        cpu_div.append(
            dcc.Graph(
                id="%scpu" % (server.replace(".", "")),
                figure=fig, config={'displayModeBar': False}))
        html_divs.append(html.Div(cpu_div, style={"margin-left": 30, }))
        html_divs.append(
            html.Div(
                html.A(html.H6("Back to Top"), href="#contentsTab"),
                style={"margin-left": 20}))
        all_html_divs.append(html.Div(id="server%s" %
                                      server.replace(".", ""), children=html_divs))
        # server_link_namke = server if
        all_contents.extend([html.A(html.H6(server, style={"font-size": "1.2em"}),
                                    href="#server%s" % server.replace(".", "")),
                             html.Div(gpu_contents, style={"margin-left": 5})])
    return all_contents, all_html_divs


if __name__ == '__main__':
    threads = start_dataservice()
    app.run_server(port=8086, host="0.0.0.0")
    for thread in threads:
        thread.join()
        thread.join()
