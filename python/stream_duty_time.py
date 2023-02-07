import argparse
import logging
from pathlib import Path
import sys
import grpc
import json
from minknow_api.manager import Manager
import minknow_api.statistics_pb2


def dump_statistics(connection, acquisition_run_id, args):
    """Extract any acquisition output information about `acquisition_run_id`."""
    run_info = connection.acquisition.get_acquisition_info(run_id=acquisition_run_id)

    def do_title(title_str, title_char):
        """Format a markdown title for `title_str`"""
        return title_str + "\n" + title_char * len(title_str) + "\n\n"

    def format_filter_group(filter_group):
        """Find a descriptive string for `filter_group`."""
        return (
            "barcode: %s, lamp_barcode_id: %s, lamp_target_id: %s, alignment_reference: %s"
            % (
                filter_group.barcode_name,
                filter_group.lamp_barcode_id,
                filter_group.lamp_target_id,
                filter_group.alignment_reference,
            )
        )

    # Invoke the API to get a stream of acquisition output results:
    #
    # Request snapshots each hour, and ensure data is split on
    # alignment reference, barcode name, and lamp target/barcode.
    stream = connection.statistics.stream_duty_time(
        acquisition_run_id=acquisition_run_id,
        data_selection=minknow_api.statistics_pb2.DataSelection(step=60 * 60),
        #split=minknow_api.statistics_pb2.AcquisitionOutputSplit(
        #    alignment_reference=True,
        #    barcode_name=True,
        #    lamp_barcode_id=True,
        #    lamp_target_id=True,
        #),
    )

    result = list()
    print(stream)
    for a in stream:    # channel_states
        print(a)
    #    for b in a:
    #        print(b)
#    for filter_groups in stream:
#        for filter_group in filter_groups.bucket_ranges:
#            for snapshot in filter_group.snapshots:
#                # TODO brac tylko ostatni snapshot!!!!!!!!!!!!!!!!!!!!!!!!!
#                vars = dict()
#                vars['address'] = str(args.host) + ':' + str(args.port)
#                vars['name'] = args.position
#                vars['seconds'] = str(snapshot.seconds)
#                vars['read_count'] = str(snapshot.yield_summary.read_count)
#                result.append(vars)
#    print('[' + ','.join(json.dumps(d) for d in result) + ']')


def main():
    """Entrypoint to extract run statistics example"""
    # Parse arguments to be passed to started protocols:
    parser = argparse.ArgumentParser(
        description="""
        Collect statistics from an existing protocol.
        """
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="IP address of the machine running MinKNOW (defaults to localhost)",
    )
    parser.add_argument(
        "--port",
        default=9502,
        help="Port to connect to on host (defaults to standard MinKNOW port)",
    )
    parser.add_argument(
        "--api-token",
        default=None,
        help="Specify an API token to use, should be returned from the sequencer as a developer API token.",
    )
    parser.add_argument(
        "--position",
        default=None,
        help="position on the machine (or MinION serial number) to run the protocol at",
    )
    parser.add_argument(
        "--protocol",
        help="Extract information for a specific protocol run-id (eg. 04462a44-eed3-4550-af0d-bc9683352583 returned form protocol.list_protocol_runs). Defaults to last run protocol.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Specify --verbose on the command line to get extra details about
    if args.verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Construct a manager using the host + port provided:
    manager = Manager(
        host=args.host, port=args.port, developer_api_token=args.api_token
    )

    # Find which positions we are going to start protocol on:
    positions = list(manager.flow_cell_positions())
    filtered_positions = list(filter(lambda pos: pos.name == args.position, positions))

    # Find the position we were asked to interrogate:
    if not filtered_positions and args.position is not None:
        print(
            "Failed to find position %s in available positions '%s'"
            % (args.position, ", ".join([p.name for p in positions]))
        )
        sys.exit(1)

    filtered_positions=positions
    # Connect to the grpc port for the position:
    connection = filtered_positions[0].connect()

    # Find the protoocol id we are going to query (or the most recent if not specified):
    protocol_id = args.protocol
    if not protocol_id:
        protocols = connection.protocol.list_protocol_runs()
        if not protocols.run_ids:
            print(
                "%s has no protocols available to extract statistics" % args.position,
                file=sys.stderr,
            )
            sys.exit(1)
        protocol_id = protocols.run_ids[-1]

    # Find the correct acquisition run to query:
    try:
        run_info = connection.protocol.get_run_info(run_id=protocol_id)
    except grpc.RpcError as e:
        print("Failed to get protocol info for id '%s'" % protocol_id, file=sys.stderr)
        sys.exit(1)

    if not run_info.acquisition_run_ids:
        print("No acquisition info for protocol id '%s'" % protocol_id, file=sys.stderr)
        sys.exit(1)

    interesting_acquisition_id = run_info.acquisition_run_ids[-1]

    # Last acquisition period will contain any sequencing.
    #
    # The first acquisition may be a calibration (if required), then the sequencing run is next.
    dump_statistics(
        connection, interesting_acquisition_id, args
    )


if __name__ == "__main__":
    main()
