import grpc

import sys
import path_config

sys.path.append(str(path_config.repo_root / "experimentNao" / "generated"))

from experimentNao.generated.nao_pb2_grpc import NaoControllerStub


def initialize_client():
    channel = grpc.insecure_channel("localhost:18861")
    client = NaoControllerStub(channel)
    return client
