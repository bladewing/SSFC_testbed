"""Provide ctypes' struct Alertpkt definition from spo_alert_unixsock.h"""
from ctypes import *

ALERTMSG_LENGTH = 256 # decode.h
SNAPLEN = 1514 # decode.h

"""
	    struct timeval {
		   time_t      tv_sec;     /* seconds */
		   suseconds_t tv_usec;    /* microseconds */
	    };
"""
# LONGWORD -- type of __WORDSIZE bits, traditionally long
time_t = suseconds_t = c_long

class timeval(Structure):
    _fields_ = [('tv_sec', time_t),
                ('tv_usec', suseconds_t)]

"""
00037 typedef struct _Event
00038 {
00039     u_int32_t sig_generator;   /* which part of snort generated the alert? */
00040     u_int32_t sig_id;          /* sig id for this generator */
00041     u_int32_t sig_rev;         /* sig revision for this id */
00042     u_int32_t classification;  /* event classification */
00043     u_int32_t priority;        /* event priority */
00044     u_int32_t event_id;        /* event ID */
00045     u_int32_t event_reference; /* reference to other events that have gone off,
00046                                 * such as in the case of tagged packets...
00047                                 */
00048     struct timeval ref_time;   /* reference time for the event reference */
00049
00050     /* Don't add to this structure because this is the serialized data
00051      * struct for unified logging.
00052      */
00053 } Event;
"""
class Event(Structure):
    _fields_ = [('sig_generator', c_uint32),
                ('sig_id', c_uint32),
                ('sig_rev', c_uint32),
                ('classification', c_uint32),
                ('priority', c_uint32),
                ('event_id', c_uint32),
                ('event_reference', c_uint32),
                ('ref_time', timeval),
    ]


"""
      /*
00143  * Each packet in the dump file is prepended with this generic header.
00144  * This gets around the problem of different headers for different
00145  * packet interfaces.
00146  */
00147 struct pcap_pkthdr {
00148         struct timeval ts;      /* time stamp */
00149         bpf_u_int32 caplen;     /* length of portion present */
00150         bpf_u_int32 len;        /* length this packet (off wire) */
00151 };
"""
class pcap_pkthdr(Structure):
    _fields_ = [('ts', timeval),
                ('caplen', c_uint32),
                ('len', c_uint32)]
"""
 /* this struct is for the alert socket code.... */
00035 typedef struct _Alertpkt
00036 {
00037     u_int8_t alertmsg[ALERTMSG_LENGTH]; /* variable.. */
00038     struct pcap_pkthdr pkth;
00039     u_int32_t dlthdr;       /* datalink header offset. (ethernet, etc.. ) */
00040     u_int32_t nethdr;       /* network header offset. (ip etc...) */
00041     u_int32_t transhdr;     /* transport header offset (tcp/udp/icmp ..) */
00042     u_int32_t data;
00043     u_int32_t val;  /* which fields are valid. (NULL could be
00044         * valids also)
00045 *                                  */
00046     /* Packet struct --> was null */
00047 #define NOPACKET_STRUCT 0x1
00048     /* no transport headers in packet */
00049 #define NO_TRANSHDR    0x2kR3IDTai3KWAh6gf
00050     u_int8_t pkt[SNAPLEN];
00051     Event event;
00052 } Alertpkt;
"""
class Alertpkt(Structure):
	_fields_ = [('alertmsg', (c_uint8 * ALERTMSG_LENGTH)),
                ('pkth', pcap_pkthdr),
                ('dlthdr', c_uint32),
                ('nethdr', c_uint32),
                ('transhdr', c_uint32),
                ('data', c_uint32),
                ('val', c_uint32),
                ('pkt', (c_uint8 * SNAPLEN)),
                ('event', Event)
    ]
    #str_format = "[%s]" % ', '.join(['{0.%s}' % f[0] for f in _fields_])

	def getMessage(self):
		return ''.join([chr(i) for i in self.alertmsg]).rstrip('\x00')
