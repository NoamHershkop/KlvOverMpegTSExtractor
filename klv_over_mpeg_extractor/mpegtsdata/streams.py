from logging import getLogger

from .packet import extract_packet
from .utils import get_or_create_key
import socket

logger = getLogger("__name__")

packet_size = 188


def _prepare_socket(address: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except AttributeError as e:
        logger.error(e)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    sock.bind((address, port))
    host = socket.gethostbyname(socket.gethostname())
    sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
    sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                    socket.inet_aton(address) + socket.inet_aton(host))

    return sock


def extract_streams_for_file(stream):
    """
    Extract MPEG-TS packets per stream
    :param stream: MPEG-TS data stream, usually from a file
    :return: Dictionary of stream id (key) and list of packets (value)
    """
    streams_packets = {}
    packet_data = stream.read(packet_size)
    while packet_data:
        packet = extract_packet(packet_data)
        stream_packets = get_or_create_key(streams_packets, packet['packet_id'], [])
        stream_packets.append(packet)
        packet_data = stream.read(packet_size)
    return streams_packets


def extract_mpeg_ts_from_stream(address: str, port: int):
    sock = _prepare_socket(address, port)

    while True:
        try:
            data, addr = sock.recvfrom(packet_size)
            packet = extract_packet(data)
            # TODO: figure out what to do here
        except socket.error as e:
            logger.error(e)

