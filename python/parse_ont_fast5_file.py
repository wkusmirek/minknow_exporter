import json
import sys
from ont_fast5_api.fast5_interface import get_fast5_file

def parse_ont_fast5_file(path_to_file):
    vars = dict()
    with get_fast5_file(path_to_file, mode="r") as f5:
        for read in f5.get_reads():
            # TODO
            vars['read.read_id'] = read.read_id
            vars['read.channel_info.channel_number'] = read.get_channel_info()['channel_number']
            vars['read.channel_info.digitisation'] = read.get_channel_info()['digitisation']
            vars['read.channel_info.offset'] = read.get_channel_info()['offset']
            vars['read.channel_info.range'] = read.get_channel_info()['range']
            vars['read.channel_info.sampling_rate'] = read.get_channel_info()['sampling_rate']
            vars['read.status.read_info.duration'] = read.status.read_info[0].duration
            vars['read.status.read_info.start_time'] = read.status.read_info[0].start_time
            vars['read.status.read_info.read_id'] = read.status.read_info[0].read_id
            vars['read.status.read_info.start_mux'] = read.status.read_info[0].start_mux
            vars['read.status.read_info.read_number'] = read.status.read_info[0].read_number

    print(json.dumps(vars))

if __name__ == '__main__':
    parse_ont_fast5_file(sys.argv[1])
