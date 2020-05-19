# library-imports
import random
import time
import sqlite3 as lite

# standard ryu-imports
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

# packets for l2> packet analysis
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp

class L7sdntestSwitch(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(L7sdntestSwitch, self).__init__(*args, **kwargs)
        self.logger.info("l7sdntest Switch-mode initialized")
        
        # Database
        self.db_con = None
        # DEBUG!!!!
        self.db_connect()
        query = self.db_query('SELECT SQLITE_VERSION()')
        data = query.fetchone()
        self.logger.info("SQLite version: %s", data)
        self.db_disconnect()
        
        # Global datapath
        self.cached_dp = None
        
        # physical ports
        self.internal_ports = [22] # list
        self.mac_to_port = {} # dictionary
        self.completed_db_entries = []

# ----------------------------------------------------------------------
# helper methods
    # self, switch (datapath), match rules, actions after match, idle timeout, hard timeout
    def add_flow(self, datapath, match, actions, idle_timeout, hard_timeout, priority_modificator = 0):
        ofproto = datapath.ofproto
        
        priority = ofproto.OFP_DEFAULT_PRIORITY + priority_modificator

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=idle_timeout, hard_timeout=hard_timeout,
            priority=priority,
            flags=ofproto.OFPFF_SEND_FLOW_REM, match=match, actions=actions)
            
        datapath.send_msg(mod)
        
        print(str(time.time())+": Send FlowMod to Switch; idle="+str(idle_timeout)+" hard="+str(hard_timeout)+" prio="+str(priority_modificator))

    def db_connect(self):
        try:
            if self.db_con == None:
                self.db_con = lite.connect('/home/vagrant/l7sdntest/src/comappdb.sqlite')
                self.logger.info("DB connected")
            else:
                self.logger.info("DB already connected")
        except lite.Error as e:
            self.logger.info("Error %s:", e.args[0])

    def db_disconnect(self):
        try:
            if self.db_con == None:
                self.logger.info("DB not connected")
            else:
                self.db_con.close()
                self.db_con = None
                self.logger.info("DB disconnected")
        except lite.Error as e:
            self.logger.info("Error %s:", e.args[0])

    def db_query(self, sql):
        try:
            if self.db_con == None:
                self.logger.info("DB not connected")
            else:
                cur = self.db_con.cursor()    
                return cur.execute(sql)
        except lite.Error as e:
            self.logger.info("Error %s:", e.args[0])

    def handle_client(self):
        self.logger.info("Client-handling is not ready yet")

# ----------------------------------------------------------------------
# EVENTS
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        # extract standard vars
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        # update current cached global datapath
        self.cached_dp = datapath
        
        # extract helpful vars
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst_mac = eth.dst
        src_mac = eth.src
        
        ipv4_msg = pkt.get_protocol(ipv4.ipv4)
        while ipv4_msg != None:
            dst_ip = ipv4_msg.dst
            src_ip = ipv4_msg.src
            
            if src_ip == '0.0.0.0':
                break
            
            tcp_msg = pkt.get_protocol(tcp.tcp)
            if tcp_msg == None:
                break
            
            dst_tcp = tcp_msg.dst_port
            src_tcp = tcp_msg.src_port
            
            self.logger.info("packet in src:%s dst:%s port:%s", src_ip, dst_ip, msg.in_port)
            
            if src_tcp >= 30000 and dst_tcp >= 29000 and dst_tcp < 30000:
                self.logger.info('Default: from out to in')
                match = ofp_parser.OFPMatch(dl_type=0x800, nw_proto=6, nw_src=src_ip, nw_dst=dst_ip, tp_src=src_tcp, tp_dst=dst_tcp)
                actions = [ofp_parser.OFPActionOutput(self.internal_ports[0])]
                idle_timeout = 2
                hard_timeout = 0
                priority = 10
                self.add_flow(datapath, match, actions, idle_timeout, hard_timeout, priority)
                out = ofp_parser.OFPPacketOut(
                    datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
                    actions=actions, data=data)
                datapath.send_msg(out)
                return
            
            if src_tcp >= 29000 and src_tcp < 30000 and dst_tcp >= 30000:
                self.logger.info('Default: from in to out')
                match = ofp_parser.OFPMatch(dl_type=0x800, nw_proto=6, nw_src=src_ip, nw_dst=dst_ip, tp_src=src_tcp, tp_dst=dst_tcp)
                actions = [ofp_parser.OFPActionOutput(23)]
                idle_timeout = 2
                hard_timeout = 0
                priority = 0
                self.add_flow(datapath, match, actions, idle_timeout, hard_timeout, priority)
                out = ofp_parser.OFPPacketOut(
                    datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
                    actions=actions, data=data)
                datapath.send_msg(out)
                return
            
            break
            
        
        self.logger.info("packet in dpid:%s src:%s dst:%s port:%s", dpid, src_mac, dst_mac, msg.in_port)
        
        # Lern port for next time
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src_mac] = msg.in_port
        
        # Lookup for used addresses
        if dst_mac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst_mac]
        else:
            out_port = ofproto.OFPP_FLOOD
        
        actions = [ofp_parser.OFPActionOutput(out_port)]
        
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            idle_timeout = 0
            hard_timeout = 2
            if msg.in_port in list(self.internal_ports):
                idle_timeout = 6
                hard_timeout = 0
            match = datapath.ofproto_parser.OFPMatch(in_port=msg.in_port, dl_dst=dst_mac)
            self.add_flow(datapath, match, actions, idle_timeout, hard_timeout, -5)
        
        out = ofp_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPVendor, MAIN_DISPATCHER)
    def vendor1_msg_handler(self, ev):
        msg = ev.msg
        self.logger.info("Vendor message detected")
        
        # (0) Check if datapath is available
        if self.cached_dp == None:
            self.logger.info("No datapath for installing rules available")
            return
        
        # (1) Connect to database
        self.db_connect()
        # (2) look for unhandled clients
        timelimit = int(time.time()) - 30
        query = self.db_query('SELECT * FROM clients WHERE switch_to_port IS NULL AND last_signal > ' + str(timelimit))
            # in error case, when 
        if query == None:
            self.logger.info("DB-query was None")
            self.db_disconnect()
            return
        clients = query.fetchall()
        # (3) handle each client
        
        for client in clients:
            # TODO: Find available servers in the database
            new_tcp_port = 29000 + random.randint(0,1)
            # debug message
            dbid = int(client[0])
            if dbid in list(self.completed_db_entries):
                self.logger.info("id %s ignored", dbid)
                continue
            self.logger.info("Read id=%s ip=%s port=%s dst_ip=%s dst_port=%s new tcp port=%s", dbid, client[1], client[2], client[4], client[5], str(new_tcp_port))
            self.completed_db_entries.append(dbid)
            # update database
        #    update = self.db_query('UPDATE clients SET switch_to_port="'+str(new_tcp_port)+'" WHERE id='+str(client[0]))
        
            datapath = self.cached_dp
            
            client_ip = '10.10.1.3'
            server_ip = client[4][1:]
            client_tcp_port = int(client[2])
            server_tcp_port = int(client[5])
            
            # rule1: from out to in
            match = datapath.ofproto_parser.OFPMatch(dl_type=0x800, nw_proto=6, nw_src=client_ip, nw_dst=server_ip, tp_src=client_tcp_port, tp_dst=server_tcp_port)
            actions = []
            if server_tcp_port != new_tcp_port:
                actions.append(datapath.ofproto_parser.OFPActionSetTpDst(new_tcp_port))
            actions.append(datapath.ofproto_parser.OFPActionOutput(self.internal_ports[0]))
            idle_timeout = 3
            hard_timeout = 0
            self.add_flow(datapath, match, actions, idle_timeout, hard_timeout)
            
            # rule2: from in to out
            match = datapath.ofproto_parser.OFPMatch(dl_type=0x800, nw_proto=6, nw_src=server_ip, nw_dst=client_ip, tp_src=new_tcp_port, tp_dst=client_tcp_port)
            actions = []
            if server_tcp_port != new_tcp_port:
                actions.append(datapath.ofproto_parser.OFPActionSetTpSrc(server_tcp_port))
            actions.append(datapath.ofproto_parser.OFPActionOutput(23))
            idle_timeout = 2
            hard_timeout = 0
            self.add_flow(datapath, match, actions, idle_timeout, hard_timeout, 5)
        
        # (4) Close database-connection
        self.db_disconnect()

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no
        
        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)

