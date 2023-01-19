from uuid import uuid4
import logging
from pathlib import Path
from threading import Thread
import time
import grpc
import numpy as np
import sys
from minknow_api import manager_pb2
from minknow_server import ManagerServer

LOGGER = logging.getLogger(__name__)

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
            name="X1",
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=8000),
        ),
        manager_pb2.FlowCellPosition(
            name="X2",
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=8001),
        ),
        manager_pb2.FlowCellPosition(
            name="X3",
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=8002),
        ),
        manager_pb2.FlowCellPosition(
            name="X4",
            state=manager_pb2.FlowCellPosition.State.STATE_RUNNING,
            rpc_ports=manager_pb2.FlowCellPosition.RpcPorts(secure=8003),
        ),
        manager_pb2.FlowCellPosition(
            name="X5",
            state=manager_pb2.FlowCellPosition.State.STATE_INITIALISING
        ),
    ]

    with ManagerServer(positions=positions, port=9502) as server:
        time.sleep(20000)

if __name__ == "__main__":
    mock()
