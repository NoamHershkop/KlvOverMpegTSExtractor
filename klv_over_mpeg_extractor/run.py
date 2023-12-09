from logging import getLogger

import click
from klv_over_mpeg_extractor import mpegtsdata, klvdata
from klv_over_mpeg_extractor.klvreconstructor import reconstruct_klv_packets

logger = getLogger("__name__")


def extract_klv_file(path):
    with open(path, 'rb') as stream:
        for packet in klvdata.StreamParser(stream):
            packet.structure()
            packet.validate()


def extract_mpegts_from_file(file: str):
    with open(file, 'rb') as stream:
        extract_mpegts(stream)


def extract_mpegts(stream):
    streams_packets = mpegtsdata.extract_streams_for_file(stream)
    for key in streams_packets:
        packets = streams_packets[key]
        logger.debug(f'key=0x{key:X}, packets: {len(packets)}')
        klv_data, pts_per_packet = reconstruct_klv_packets(packets)
        total_klv_packets = len(pts_per_packet)
        if total_klv_packets:
            logger.info(f'Reconstructed packets: {total_klv_packets}')
            index = 0
            for packet in klvdata.StreamParser(klv_data):
                logger.debug(f'Packet pts: {pts_per_packet[index]}')
                index += 1
                packet.structure()
                packet.validate()


@click.command()
@click.option("--file", "-f", help="File stream to extract", type=str)
@click.option("--address", "-a", help="Address of MPEG TS", type=str)
@click.option("--port", "-p", help="port of MPEG TS", type=str)
@click.option("--klv", "-k", help='Is file KLV (true) or MPEG-TS (false)', is_flag=True)
def klv_extractor(file: str, address: str, klv: bool):
    if klv:
        extract_klv_file(file)
    elif file:
        extract_mpegts_from_file(file)
    elif address:
        ...
    else:
        logger.error("No method was given")
