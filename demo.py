import subprocess
from enum import Enum

PYTHON_CLI = "didcomm-cli"

# TODO: call a script instead
JAVA_CLI = "java"
JAVA_ARGS = ["-jar", "didcomm-demo-jvm/didcomm-demo-cli/build/libs/didcomm-demo-cli-0.1-SNAPSHOT.jar"]


class Command(Enum):
    CREATE_PEER_DID = "create-peer-did"
    RESOLVE_PEER_DID = "resolve-peer-did"
    PACK = "pack"
    UNPACK = "unpack"


def call_didcomm_python(cmd: Command, *args):
    return subprocess.check_output([PYTHON_CLI, cmd.value] + list(args)).strip().decode()


def call_didcomm_java(cmd: Command, *args):
    return subprocess.check_output([JAVA_CLI] + JAVA_ARGS + [cmd.value] + list(args)).strip().decode()


def demo(alice_fun, bob_fun):
    # 1. Bob creates a pairwise peer DID for the connection
    bob_peer_did = bob_fun(Command.CREATE_PEER_DID)
    print(f"Bob generates a new pairwise peer DID for communication with Alice: `{bob_peer_did}`.")
    print()

    # 2. Alice creates a pairwise peer DID for the connection
    alice_peer_did = alice_fun(Command.CREATE_PEER_DID)
    print(f"Alice generates a new pairwise peer DID for communication with Bob: `{alice_peer_did}`.")
    print()

    # # 3. Alice sends message to Bob
    msg_bob = "Hello Bob!"
    packed_to_bob = alice_fun(Command.PACK, "Hello Bob!", '--from', alice_peer_did, '--to', bob_peer_did)
    print(f"Alice sends '{msg_bob}' to Bob as '${packed_to_bob}'.")
    print(
        f"The message is authenticated by Alice's peer DID `{alice_peer_did}` and encrypted to Bob's peer DID `{bob_peer_did}`")
    print()

    # 4. Bob unpacks the message
    unpacked_msg = bob_fun(Command.UNPACK, packed_to_bob)
    print(f"Bob received {unpacked_msg} from Alice.")


def from_python_to_java():
    print("--------------------------------")
    print("Alice uses Python; Bob uses Java")
    print()
    demo(call_didcomm_python, call_didcomm_java)
    print()


def from_java_to_python():
    print("--------------------------------")
    print("Alice uses Java; Bob uses Python")
    print()
    demo(call_didcomm_java, call_didcomm_python)
    print()


if __name__ == '__main__':
    from_python_to_java()
    from_java_to_python()
