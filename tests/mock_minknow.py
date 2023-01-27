from uuid import uuid4
import uuid
import logging
from pathlib import Path
from threading import Thread
import time
import grpc
import numpy as np
import sys
from minknow_server import ManagerServer, SequencingPositionServer, FlowCellInfo, PositionInfo
from minknow_api import acquisition_pb2, manager_pb2, protocol_pb2, statistics_pb2

LOGGER = logging.getLogger(__name__)

minknowDefaultPort=9502
port0=8000
port1=8001
port2=8002
port3=8003
port4=8004
name0='X1'
name1='X2'
name2='X3'
name3='X4'
name4='X5'

TEST_ACQUISITION = acquisition_pb2.AcquisitionRunInfo(run_id=str(uuid.uuid4()))

TEST_PROTOCOL = protocol_pb2.ProtocolRunInfo(
    run_id=str(uuid.uuid4()),
)
TEST_PROTOCOL_WITH_ACQUISTIIONS = protocol_pb2.ProtocolRunInfo(
    run_id=str(uuid.uuid4()), acquisition_run_ids=[TEST_ACQUISITION.run_id]
)

TEST_ACQUISITION_OUTPUT_STATS = [
    statistics_pb2.StreamAcquisitionOutputResponse(
        snapshots=[
            statistics_pb2.StreamAcquisitionOutputResponse.FilteredSnapshots(
                filtering=[
                    statistics_pb2.AcquisitionOutputKey(
                        barcode_name="barcode1234",
                        lamp_barcode_id="unclassified",
                        lamp_target_id="unclassified",
                        alignment_reference="unaligned",
                    )
                ],
                snapshots=[
                    statistics_pb2.AcquisitionOutputSnapshot(
                        seconds=60,
                        yield_summary=acquisition_pb2.AcquisitionYieldSummary(
                            basecalled_pass_read_count=600
                        ),
                    )
                ],
            )
        ]
    )
]

def mock():
    positions = [
        #STATE_INITIALISING = 0;
        #STATE_RUNNING = 1;
        #STATE_RESETTING = 2;
        #STATE_HARDWARE_REMOVED = 3;
        #STATE_HARDWARE_ERROR = 4;
        #STATE_SOFTWARE_ERROR = 5;
        #STATE_NEEDS_ASSOCIATION = 6;
#      name:
#          The name of the position.  For MinIONs, this is the name of
#          the MinION (eg: MN12345). For integrated positions, this is
#          the label for the position on the sequencer (eg: X1 for
#          GridION, 1-A1-D1 for PromethION).
#      location:
#          For integrated flow cell positions, indicates where it is on
#          the sequencing unit.  This information is not provided for
#          MinIONs (except for the MinION Mk1C, in which case the
#          position is always 0, 0).
#      state:
#          The state of the flow cell position.  If the state is not
#          `STATE_RUNNING` or `STATE_INITIALISING`, the flow cell
#          position can be assumed to be unusable, and the `error_info`
#          field should be populated.
#      rpc_ports:
#          The ports the APIs for this flow cell position are provided
#          on.  Always provided if `state` is `STATE_RUNNING`. May also
#          be provided when `state` is one of the hardware errors if the
#          software is still running.
#      error_info:
#          Provides a textual description of error states.  When `state`
#          is not `STATE_INITIALISING`, `STATE_RUNNING` or
#          `STATE_RESETTING`, this provides some information (in English)
#          about the error. This will be a textual description of the
#          value in `state`, possibly with extra information about the
#          error (if available).  This can be useful for dealing with
#          (new) unknown states.
#      shared_hardware_group:
#          Some positions may share hardware. Positions that share
#          hardware will have the same group-id. If positions do share
#          hardware, to reset the hardware you will need to reset all
#          positions in the group at the same time.
#      is_integrated:
#          Indicates that this is an integrated flow cell position.  This
#          is true for the integrated positions on a PromethION, GridION
#          or MinION Mk1C, and false for a MinION Mk1B.  Integrated
#          positions are always listed, even if (due to some hardware
#          error) they can't be found. They are never in
#          STATE_HARDWARE_REMOVED, and they always report a location.
#          Additionally, integrated positions cannot be associated
#          independently - if they are in STATE_NEEDS_ASSOCIATION, then
#          the host as a whole needs associating. Likewise, either all
#          integrated positions can run offline, or none of them can.
#          Since 4.4
#      can_sequence_offline:
#          Indicates that this position can sequence offline.  For
#          integrated positions, this is the same as the corresponding
#          field returned from the describe_host RPC.
#      protocol_state:
#          Indicates the state of the last or current protocol on the
#          flow cell position.  Since 5.0.
#      is_simulated:
#          Whether the device is simulated.  If this is true, there is no
#          physical device - MinKNOW is simulating it. If it is false,
#          MinKNOW will be acquiring data from a real device.  Since 5.2
#      device_type:
#          The type of the device.  Since 5.2
#      parent_name:
#          The name of the device this flow cell position is part of.
#          For an integrated position, this will be the host serial, as
#          returned by describe_host().  For a MinION Mk1B, this will be
#          the same as the `name` field.  For a P2 Solo, this will be the
#          name of the P2 Solo unit.  Since 5.3
        manager_pb2.FlowCellPosition(
            name=name0,
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=port0),
        ),
        manager_pb2.FlowCellPosition(
            name=name1,
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=port1),
        ),
        manager_pb2.FlowCellPosition(
            name=name2,
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=port2),
        ),
        manager_pb2.FlowCellPosition(
            name=name3,
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=port3),
        ),
        manager_pb2.FlowCellPosition(
            name=name4,
            state=manager_pb2.FlowCellPosition.State.STATE_INITIALISING
        ),
    ]

    with SequencingPositionServer(PositionInfo(position_name=name0),port=port0) as sequencing_position_0, SequencingPositionServer(PositionInfo(position_name=name1),port=port1) as sequencing_position_1, SequencingPositionServer(PositionInfo(position_name=name2),port=port2) as sequencing_position_2, SequencingPositionServer(PositionInfo(position_name=name3),port=port3) as sequencing_position_3, SequencingPositionServer(PositionInfo(position_name=name4),port=port4) as sequencing_position_4:

        sequencing_position_0.set_protocol_runs([TEST_PROTOCOL_WITH_ACQUISTIIONS])
        sequencing_position_0.set_acquisition_runs([TEST_ACQUISITION])
        sequencing_position_0.set_acquisition_output_statistics(TEST_ACQUISITION.run_id, TEST_ACQUISITION_OUTPUT_STATS)
        sequencing_position_1.set_protocol_runs([TEST_PROTOCOL_WITH_ACQUISTIIONS])
        sequencing_position_1.set_acquisition_runs([TEST_ACQUISITION])
        sequencing_position_1.set_acquisition_output_statistics(TEST_ACQUISITION.run_id, TEST_ACQUISITION_OUTPUT_STATS)
        sequencing_position_2.set_protocol_runs([TEST_PROTOCOL_WITH_ACQUISTIIONS])
        sequencing_position_2.set_acquisition_runs([TEST_ACQUISITION])
        sequencing_position_2.set_acquisition_output_statistics(TEST_ACQUISITION.run_id, TEST_ACQUISITION_OUTPUT_STATS)
        sequencing_position_3.set_protocol_runs([TEST_PROTOCOL_WITH_ACQUISTIIONS])
        sequencing_position_3.set_acquisition_runs([TEST_ACQUISITION])
        sequencing_position_3.set_acquisition_output_statistics(TEST_ACQUISITION.run_id, TEST_ACQUISITION_OUTPUT_STATS)
        sequencing_position_4.set_protocol_runs([TEST_PROTOCOL_WITH_ACQUISTIIONS])
        sequencing_position_4.set_acquisition_runs([TEST_ACQUISITION])
        sequencing_position_4.set_acquisition_output_statistics(TEST_ACQUISITION.run_id, TEST_ACQUISITION_OUTPUT_STATS)

        with ManagerServer(positions=positions, port=minknowDefaultPort) as server:
            time.sleep(20000)

if __name__ == "__main__":
    mock()
