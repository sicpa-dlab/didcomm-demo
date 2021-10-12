import json
import subprocess
import sys
from enum import Enum
from pathlib import Path

PYTHON_CLI = "didcomm-cli"

JAVA_CLI_NAME = "didcomm-demo-cli.bat" if sys.platform.startswith("win") else "didcomm-demo-cli"
JAVA_CLI = Path("./didcomm-demo-jvm") / "didcomm-demo-cli" / "build" / "install" / "didcomm-demo-cli" / "bin" / JAVA_CLI_NAME


class Command(Enum):
    CREATE_PEER_DID = "create-peer-did"
    RESOLVE_PEER_DID = "resolve-peer-did"
    PACK = "pack"
    UNPACK = "unpack"


def call_didcomm_python(cmd: Command, *args):
    return subprocess.check_output([PYTHON_CLI, cmd.value] + list(args)).strip().decode()


def call_didcomm_java(cmd: Command, *args):
    return subprocess.check_output([JAVA_CLI, cmd.value] + list(args)).strip().decode()


def demo(alice_fun, bob_fun):
    # 1. Bob creates a pairwise peer DID for the connection
    bob_peer_did = bob_fun(Command.CREATE_PEER_DID,
                           '--service-endpoint', 'https://bob-endpoint.com',
                           '--service-routing-key', 'bob-key-1', '--service-routing-key', 'bob-key-2')
    assert bob_peer_did.startswith("did:peer")

    bob_did_doc_json = alice_fun(Command.RESOLVE_PEER_DID, bob_peer_did)
    bob_did_doc = json.loads(bob_did_doc_json)
    assert "id" in bob_did_doc
    assert "authentication" in bob_did_doc
    assert "keyAgreement" in bob_did_doc
    assert "service" in bob_did_doc

    # 2. Alice creates a pairwise peer DID for the connection
    alice_peer_did = alice_fun(Command.CREATE_PEER_DID,
                               '--service-endpoint', 'https://alice-endpoint.com',
                               '--service-routing-key', 'alice-key-1', '--service-routing-key', 'alice-key-2')
    assert bob_peer_did.startswith("did:peer")

    alice_peer_did_doc_json = bob_fun(Command.RESOLVE_PEER_DID, bob_peer_did)
    alice_peer_did_doc = json.loads(alice_peer_did_doc_json)
    assert "id" in alice_peer_did_doc
    assert "authentication" in alice_peer_did_doc
    assert "keyAgreement" in alice_peer_did_doc
    assert "service" in alice_peer_did_doc

    # 3. Alice sends message to Bob
    msg_bob = "Hello Bob!"
    packed_to_bob_json = alice_fun(Command.PACK, "Hello Bob!", '--from', alice_peer_did, '--to', bob_peer_did,
                                   '--sign-from', alice_peer_did)
    packed_to_bob = json.loads(packed_to_bob_json)
    assert "ciphertext" in packed_to_bob
    assert "protected" in packed_to_bob

    # 4. Bob unpacks the message
    unpacked_msg = bob_fun(Command.UNPACK, packed_to_bob_json)
    assert msg_bob in unpacked_msg
    assert bob_peer_did in unpacked_msg
    assert alice_peer_did in unpacked_msg


def test_python_to_java():
    demo(call_didcomm_python, call_didcomm_java)


def test_java_to_python():
    demo(call_didcomm_java, call_didcomm_python)
