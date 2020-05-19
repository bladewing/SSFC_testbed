# Copyright (C) 2012 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import time
import MySQLdb
import json
import ast
from webob import Response

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_0
from ryu.lib import ofctl_v1_2
from ryu.lib import ofctl_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.app.wsgi import ControllerBase, WSGIApplication


LOG = logging.getLogger('ryu.app.ofctl_rest')

# supported ofctl versions in this restful app
supported_ofctl = {
    ofproto_v1_0.OFP_VERSION: ofctl_v1_0,
    ofproto_v1_2.OFP_VERSION: ofctl_v1_2,
    ofproto_v1_3.OFP_VERSION: ofctl_v1_3,
}

# REST API
#

# Retrieve the switch stats
#
# get the list of all switches
# GET /stats/switches
#
# get the desc stats of the switch
# GET /stats/desc/<dpid>
#
# get flows stats of the switch
# GET /stats/flow/<dpid>
#
# get flows stats of the switch filtered by the fields
# POST /stats/flow/<dpid>
#
# get aggregate flows stats of the switch
# GET /stats/aggregateflow/<dpid>
#
# get aggregate flows stats of the switch filtered by the fields
# POST /stats/aggregateflow/<dpid>
#
# get table stats of the switch
# GET /stats/table/<dpid>
#
# get table features stats of the switch
# GET /stats/tablefeatures/<dpid>
#
# get ports stats of the switch
# GET /stats/port/<dpid>
#
# get queues stats of the switch
# GET /stats/queue/<dpid>
#
# get queues config stats of the switch
# GET /stats/queueconfig/<dpid>/<port>
#
# get meter features stats of the switch
# GET /stats/meterfeatures/<dpid>
#
# get meter config stats of the switch
# GET /stats/meterconfig/<dpid>
#
# get meters stats of the switch
# GET /stats/meter/<dpid>
#
# get group features stats of the switch
# GET /stats/groupfeatures/<dpid>
#
# get groups desc stats of the switch
# GET /stats/groupdesc/<dpid>
#
# get groups stats of the switch
# GET /stats/group/<dpid>
#
# get ports description of the switch
# GET /stats/portdesc/<dpid>

# Update the switch stats
#
# add a flow entry
# POST /stats/flowentry/add
#
# modify all matching flow entries
# POST /stats/flowentry/modify
#
# modify flow entry strictly matching wildcards and priority
# POST /stats/flowentry/modify_strict
#
# delete all matching flow entries
# POST /stats/flowentry/delete
#
# delete flow entry strictly matching wildcards and priority
# POST /stats/flowentry/delete_strict
#
# delete all flow entries of the switch
# DELETE /stats/flowentry/clear/<dpid>
#
# add a meter entry
# POST /stats/meterentry/add
#
# modify a meter entry
# POST /stats/meterentry/modify
#
# delete a meter entry
# POST /stats/meterentry/delete
#
# add a group entry
# POST /stats/groupentry/add
#
# modify a group entry
# POST /stats/groupentry/modify
#
# delete a group entry
# POST /stats/groupentry/delete
#
# modify behavior of the physical port
# POST /stats/portdesc/modify
#
#
# send a experimeter message
# POST /stats/experimenter/<dpid>


class StatsController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(StatsController, self).__init__(req, link, data, **config)
        self.dpset = data['dpset']
        self.waiters = data['waiters']

    def get_dpids(self, req, **_kwargs):
        dps = list(self.dpset.dps.keys())
        body = json.dumps(dps)
        return Response(content_type='application/json', body=body)

    def get_desc_stats(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)
        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            desc = _ofctl.get_desc_stats(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(desc)
        return Response(content_type='application/json', body=body)

    def get_flow_stats(self, req, dpid, **_kwargs):

        if req.body == '':
            flow = {}

        else:

            try:
                flow = ast.literal_eval(req.body)

            except SyntaxError:
                LOG.debug('invalid syntax %s', req.body)
                return Response(status=400)

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            flows = _ofctl.get_flow_stats(dp, self.waiters, flow)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)

    def get_aggregate_flow_stats(self, req, dpid, **_kwargs):

        if req.body == '':
            flow = {}

        else:
            try:
                flow = ast.literal_eval(req.body)

            except SyntaxError:
                LOG.debug('invalid syntax %s', req.body)
                return Response(status=400)

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            flows = _ofctl.get_aggregate_flow_stats(dp, self.waiters, flow)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(flows)
        return Response(content_type='application/json', body=body)

    def get_table_stats(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            ports = _ofctl.get_table_stats(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    def get_table_features(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            ports = _ofctl.get_table_features(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    def get_port_stats(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            ports = _ofctl.get_port_stats(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(ports)
        return Response(content_type='application/json', body=body)

    def get_queue_stats(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            queues = _ofctl.get_queue_stats(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(queues)
        return Response(content_type='application/json', body=body)

    def get_queue_config(self, req, dpid, port, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        if type(port) == str and not port.isdigit():
            LOG.debug('invalid port %s', port)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))
        port = int(port)

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            queues = _ofctl.get_queue_config(dp, port, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(queues)
        return Response(content_type='application/json', body=body)

    def get_meter_features(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'get_meter_features'):
            meters = _ofctl.get_meter_features(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_meter_config(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'get_meter_config'):
            meters = _ofctl.get_meter_config(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_meter_stats(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'get_meter_stats'):
            meters = _ofctl.get_meter_stats(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        body = json.dumps(meters)
        return Response(content_type='application/json', body=body)

    def get_group_features(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'get_group_features'):
            groups = _ofctl.get_group_features(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_group_desc(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'get_group_desc'):
            groups = _ofctl.get_group_desc(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_group_stats(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'get_group_stats'):
            groups = _ofctl.get_group_stats(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def get_port_desc(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            groups = _ofctl.get_port_desc(dp, self.waiters)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        body = json.dumps(groups)
        return Response(content_type='application/json', body=body)

    def mod_flow_entry(self, req, cmd, **_kwargs):

        try:
            flow = ast.literal_eval(req.body)

        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = flow.get('dpid')

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPFC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPFC_MODIFY
        elif cmd == 'modify_strict':
            cmd = dp.ofproto.OFPFC_MODIFY_STRICT
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPFC_DELETE
        elif cmd == 'delete_strict':
            cmd = dp.ofproto.OFPFC_DELETE_STRICT
        else:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            _ofctl.mod_flow_entry(dp, flow, cmd)
        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def delete_flow_entry(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        if ofproto_v1_0.OFP_VERSION == _ofp_version:
            flow = {}
        else:
            flow = {'table_id': dp.ofproto.OFPTT_ALL}

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            _ofctl.mod_flow_entry(dp, flow, dp.ofproto.OFPFC_DELETE)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def mod_meter_entry(self, req, cmd, **_kwargs):

        try:
            flow = ast.literal_eval(req.body)

        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = flow.get('dpid')

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPMC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPMC_MODIFY
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPMC_DELETE
        else:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'mod_meter_entry'):
            _ofctl.mod_meter_entry(dp, flow, cmd)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        return Response(status=200)

    def mod_group_entry(self, req, cmd, **_kwargs):

        try:
            group = ast.literal_eval(req.body)

        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = group.get('dpid')

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        if cmd == 'add':
            cmd = dp.ofproto.OFPGC_ADD
        elif cmd == 'modify':
            cmd = dp.ofproto.OFPGC_MODIFY
        elif cmd == 'delete':
            cmd = dp.ofproto.OFPGC_DELETE
        else:
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'mod_group_entry'):
            _ofctl.mod_group_entry(dp, group, cmd)

        else:
            LOG.debug('Unsupported OF protocol or \
                request not supported in this OF protocol version')
            return Response(status=501)

        return Response(status=200)

    def mod_port_behavior(self, req, cmd, **_kwargs):

        try:
            port_config = ast.literal_eval(req.body)

        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        dpid = port_config.get('dpid')

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        port_no = port_config.get('port_no', 0)
        if type(port_no) == str and not port_no.isdigit():
            LOG.debug('invalid port_no %s', port_no)
            return Response(status=400)

        port_info = self.dpset.port_state[int(dpid)].get(port_no)

        if port_info:
            port_config.setdefault('hw_addr', port_info.hw_addr)
            port_config.setdefault('advertise', port_info.advertised)
        else:
            return Response(status=404)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        if cmd != 'modify':
            return Response(status=404)

        _ofp_version = dp.ofproto.OFP_VERSION

        _ofctl = supported_ofctl.get(_ofp_version, None)
        if _ofctl is not None:
            _ofctl.mod_port_behavior(dp, port_config)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)

    def send_experimenter(self, req, dpid, **_kwargs):

        if type(dpid) == str and not dpid.isdigit():
            LOG.debug('invalid dpid %s', dpid)
            return Response(status=400)

        dp = self.dpset.get(int(dpid))

        if dp is None:
            return Response(status=404)

        try:
            exp = ast.literal_eval(req.body)

        except SyntaxError:
            LOG.debug('invalid syntax %s', req.body)
            return Response(status=400)

        _ofp_version = dp.ofproto.OFP_VERSION
        _ofctl = supported_ofctl.get(_ofp_version, None)

        if _ofctl is not None and hasattr(_ofctl, 'send_experimenter'):
            _ofctl.send_experimenter(dp, exp)

        else:
            LOG.debug('Unsupported OF protocol')
            return Response(status=501)

        return Response(status=200)


class RestStatsApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION,
                    ofproto_v1_2.OFP_VERSION,
                    ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
        self.db_con = None
        
        # Switch ports
        self.port_external = 1
        self.port_internal = 3
        self.port_ids_in = 10
        
        # flow timings and priority
        self.ids_flow_hard_timeout = 2
        self.normal_flow_hard_timeout = 10
        self.ids_flow_priority = 120
        self.normal_flow_priority = 115
        
        # rest api variables
        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        mapper = wsgi.mapper

        wsgi.registory['StatsController'] = self.data
        path = '/stats'
        uri = path + '/switches'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_dpids',
                       conditions=dict(method=['GET']))

        uri = path + '/desc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_desc_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/flow/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_flow_stats',
                       conditions=dict(method=['GET', 'POST']))

        uri = path + '/aggregateflow/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController,
                       action='get_aggregate_flow_stats',
                       conditions=dict(method=['GET', 'POST']))

        uri = path + '/table/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_table_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/tablefeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_table_features',
                       conditions=dict(method=['GET']))

        uri = path + '/port/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_port_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/queue/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_queue_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/queueconfig/{dpid}/{port}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_queue_config',
                       conditions=dict(method=['GET']))

        uri = path + '/meterfeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_features',
                       conditions=dict(method=['GET']))

        uri = path + '/meterconfig/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_config',
                       conditions=dict(method=['GET']))

        uri = path + '/meter/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_meter_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/groupfeatures/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_features',
                       conditions=dict(method=['GET']))

        uri = path + '/groupdesc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_desc',
                       conditions=dict(method=['GET']))

        uri = path + '/group/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_group_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/portdesc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_port_desc',
                       conditions=dict(method=['GET']))

        uri = path + '/flowentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_flow_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/flowentry/clear/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='delete_flow_entry',
                       conditions=dict(method=['DELETE']))

        uri = path + '/meterentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_meter_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/groupentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_group_entry',
                       conditions=dict(method=['POST']))

        uri = path + '/portdesc/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_port_behavior',
                       conditions=dict(method=['POST']))

        uri = path + '/experimenter/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='send_experimenter',
                       conditions=dict(method=['POST']))

    def db_connect(self):
        if self.db_con == None:
            self.db_con = MySQLdb.connect(host="10.1.3.36",    # your host, usually localhost
                                 user="l7sdntest",         # your username
                                 passwd="l7sdntest",       # your password
                                 db="snort")      # name of the data base
            self.logger.info("DB connected")
        else:
            self.logger.info("DB already connected")

    def db_disconnect(self):
        if self.db_con == None:
            self.logger.info("DB not connected")
        else:
            self.db_con.close()
            self.db_con = None
            self.logger.info("DB disconnected")

    def db_query(self, sql):
        if self.db_con == None:
            self.logger.info("DB not connected")
        else:
            cur = self.db_con.cursor()
            cur.execute(sql)
            self.db_con.commit()
            return cur
    
    def leadingZero(self, number):
        if number < 10:
            return "0"+str(number)
        else:
            return str(number)

    def timeAsString(self, offset):
        offset_second = 0
        offset_minute = 0
        offset_hour = 0
        
        offset_sign = 0
        if offset < 0:
            offset_sign = -1
        else:
            offset_sign = 1
        offset_second = offset % (60 * offset_sign)
        offset_minute = ((offset - offset_second) % (3600 * offset_sign)) / 60
        offset_hour = (offset - offset_second - (offset_minute*60)) / 3600
            
        rawtime = time.localtime()
        year = rawtime.tm_year
        month = rawtime.tm_mon
        day = rawtime.tm_mday
        hour = rawtime.tm_hour + offset_hour
        minute = rawtime.tm_min + offset_minute
        second = rawtime.tm_sec + offset_second
        if second < 0:
            second = second + 60
            minute = minute - 1
        if second > 59:
            second = second - 60
            minute = minute + 1
        while minute < 0:
            minute = minute + 60
            hour = hour - 1
        while minute > 59:
            minute = minute - 60
            hour = hour + 1
        while hour < 0:
            hour = hour + 24
            day = day - 1
        while hour > 23:
            hour = hour - 24
            day = day + 1
        while day < 1:
            day = 1
            hour = 0
            minute = 0
            second = 0
        while day > 31:
            day = day - 31
        
        return str(year)+"-"+self.leadingZero(month)+"-"+self.leadingZero(day)+" "+self.leadingZero(hour)+":"+self.leadingZero(minute)+":"+self.leadingZero(second)

    def IP2num(self, ip):
        ip = ip.split(".")
        num = int(ip[3]) * 1
        num = num + int(ip[2]) * 256
        num = num + int(ip[1]) * 256 * 256
        num = num + int(ip[0]) * 256 * 256 * 256
        return num

    @set_ev_cls([ofp_event.EventOFPStatsReply,
                 ofp_event.EventOFPDescStatsReply,
                 ofp_event.EventOFPFlowStatsReply,
                 ofp_event.EventOFPAggregateStatsReply,
                 ofp_event.EventOFPTableStatsReply,
                 ofp_event.EventOFPTableFeaturesStatsReply,
                 ofp_event.EventOFPPortStatsReply,
                 ofp_event.EventOFPQueueStatsReply,
                 ofp_event.EventOFPMeterStatsReply,
                 ofp_event.EventOFPMeterFeaturesStatsReply,
                 ofp_event.EventOFPMeterConfigStatsReply,
                 ofp_event.EventOFPGroupStatsReply,
                 ofp_event.EventOFPGroupFeaturesStatsReply,
                 ofp_event.EventOFPGroupDescStatsReply,
                 ofp_event.EventOFPPortDescStatsReply
                 ], MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
            flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()

    @set_ev_cls([ofp_event.EventOFPSwitchFeatures,
                 ofp_event.EventOFPQueueGetConfigReply], MAIN_DISPATCHER)
    def features_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        del self.waiters[dp.id][msg.xid]
        lock.set()
        
    def add_flow(self, datapath, match, actions, hard_timeout, priority, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]

        if hard_timeout < 10:
            if buffer_id:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, hard_timeout=hard_timeout, priority=priority, flags=ofproto.OFPFF_SEND_FLOW_REM, match=match, instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, hard_timeout=hard_timeout, priority=priority, flags=ofproto.OFPFF_SEND_FLOW_REM, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, hard_timeout=hard_timeout, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        
        ipv4_msg = pkt.get_protocol(ipv4.ipv4)
        while ipv4_msg != None:
            src_ip = ipv4_msg.src
            dst_ip = ipv4_msg.dst
            
            if src_ip == '0.0.0.0':
                self.logger.info("Broadcast cutted")
                return
            
            tcp_msg = pkt.get_protocol(tcp.tcp)
            if tcp_msg == None:
                self.logger.info("no tcp msg from %s to %s", src_ip, dst_ip)
                return
            
            src_tcp = tcp_msg.src_port
            dst_tcp = tcp_msg.dst_port
            
            current_time = time.localtime()
            self.logger.info("[%d.%d.%d %d:%d:%d] packet in src:%s:%s dst:%s:%s port:%s", current_time.tm_year, current_time.tm_mon, current_time.tm_mday, current_time.tm_hour, current_time.tm_min, current_time.tm_sec, src_ip, src_tcp, dst_ip, dst_tcp, in_port)
            
            # Flow 1
            match = ofp_parser.OFPMatch(in_port=self.port_external, eth_type=0x800, ip_proto=6, ipv4_src=src_ip, ipv4_dst=dst_ip, tcp_src=src_tcp, tcp_dst=dst_tcp)
            actions = [ofp_parser.OFPActionOutput(self.port_ids_in)]
            hard_timeout = self.ids_flow_hard_timeout
            priority = self.ids_flow_priority
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, match, actions, hard_timeout, priority, msg.buffer_id)
            else:
                self.add_flow(datapath, match, actions, hard_timeout, priority)
                # Classic output
                out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=msg.data)
                datapath.send_msg(out)
            
            # Flow 2
            actions = [ofp_parser.OFPActionOutput(self.port_internal)]
            hard_timeout = self.normal_flow_hard_timeout
            priority = self.normal_flow_priority
            self.add_flow(datapath, match, actions, hard_timeout, priority)
            
            break

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def _flow_removed_handler(self, ev):
        #self.logger.info('%s', ev)
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        
        if msg.reason == ofp.OFPRR_IDLE_TIMEOUT:
            reason = 'IDLE TIMEOUT'
        elif msg.reason == ofp.OFPRR_HARD_TIMEOUT:
            reason = 'HARD TIMEOUT'
        elif msg.reason == ofp.OFPRR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofp.OFPRR_GROUP_DELETE:
            reason = 'GROUP DELETE'
        else:
            reason = 'unknown'

        self.logger.info('OFPFlowRemoved received: '
                          'match=%s cookie=%d priority=%d reason=%s '
                          'duration_sec=%d duration_nsec=%d '
                          'idle_timeout=%d packet_count=%d byte_count=%d',
                          msg.match, msg.cookie, msg.priority, reason,
                          msg.duration_sec, msg.duration_nsec,
                          msg.idle_timeout, msg.packet_count,
                          msg.byte_count)
        
        # (0) Prepare variables
        timestamp = self.timeAsString(-(self.ids_flow_hard_timeout+1)) # alternative: -(msg.duration_sec+1)
        ip_src = self.IP2num(msg.match["ipv4_src"])
        ip_dst = self.IP2num(msg.match["ipv4_dst"])
        tcp_sport = msg.match["tcp_src"]
        tcp_dport = 8080
        # (1) Connect to database
        self.db_connect()
        # (2) look for unhandled clients
        query = self.db_query('SELECT e.signature FROM event e INNER JOIN iphdr ip ON ip.cid = e.cid INNER JOIN tcphdr tcp ON tcp.cid = e.cid WHERE e.timestamp > "'+timestamp+'" AND ip.ip_src = '+str(ip_src)+' AND ip.ip_dst = '+str(ip_dst)+' AND tcp.tcp_sport = '+str(tcp_sport)+' AND tcp.tcp_dport = '+str(tcp_dport))
        # in error case, when 
        if query == None:
            self.logger.info("DB-query was None")
        else:
            alerts = query.fetchall()
            # (3) handle each client
            for alert in alerts:
                 # TODO: Find available servers in the database
                 #new_tcp_port = 29000 + random.randint(0,1)
                 # debug message
                 self.logger.info("Found alert for signature %s", str(alert[0]))
                 #self.logger.info("Read id=%s ip=%s port=%s dst_ip=%s dst_port=%s new tcp port=%s", client[0], client[1], client[2], client[4], client[5], str(new_tcp_port))
        self.db_disconnect()
