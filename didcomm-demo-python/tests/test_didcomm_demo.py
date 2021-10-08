import json

import pytest
from didcomm.pack_encrypted import PackEncryptedConfig
from didcomm.secrets.secrets_resolver_demo import SecretsResolverDemo
from peerdid.peer_did import is_peer_did
from peerdid.types import VerificationMaterialFormatPeerDID

from didcomm_demo.didcomm_demo import DIDCommDemo
from tests.common import get_secret_resolver_kids, check_expected_did_doc


@pytest.fixture()
def secrets_resolver(tmp_path):
    tmp_file = tmp_path / "secrets.json"
    return SecretsResolverDemo(tmp_file)


@pytest.fixture()
def demo(secrets_resolver):
    return DIDCommDemo(secrets_resolver)


def test_create_peer_did_numalg_0_one_auth_key(demo):
    did = demo.create_peer_did(auth_keys_count=1, agreement_keys_count=0)
    assert is_peer_did(did)
    assert did.startswith("did:peer:0")
    assert len(get_secret_resolver_kids(demo.secrets_resolver)) == 1
    assert get_secret_resolver_kids(demo.secrets_resolver)[0].startswith(did)
    check_expected_did_doc(did, auth_keys_count=1, agreement_keys_count=0, service_endpoint=None)


@pytest.mark.parametrize(
    "auth_keys_count,agreement_keys_count",
    [
        pytest.param(1, 1, id="1auth-1agreem"),
        pytest.param(2, 3, id="2auth-3agreem"),
        pytest.param(0, 1, id="0auth-1agreem"),
        pytest.param(0, 2, id="0auth-2agreem")
    ]
)
def test_create_peer_did_numalg_2_no_service(demo, auth_keys_count, agreement_keys_count):
    did = demo.create_peer_did(auth_keys_count=auth_keys_count, agreement_keys_count=agreement_keys_count)
    assert is_peer_did(did)
    assert did.startswith("did:peer:2")
    assert len(get_secret_resolver_kids(demo.secrets_resolver)) == auth_keys_count + agreement_keys_count
    for kid in get_secret_resolver_kids(demo.secrets_resolver):
        assert kid.startswith(did)
    check_expected_did_doc(did,
                           auth_keys_count=auth_keys_count, agreement_keys_count=agreement_keys_count,
                           service_endpoint=None)


@pytest.mark.asyncio
def test_create_peer_did_numalg_2_with_service_endpoint_no_routing(demo):
    endpoint = "https://my-endpoint"
    did = demo.create_peer_did(auth_keys_count=1, agreement_keys_count=1, service_endpoint=endpoint)
    assert is_peer_did(did)
    assert did.startswith("did:peer:2")
    assert len(get_secret_resolver_kids(demo.secrets_resolver)) == 2
    for kid in get_secret_resolver_kids(demo.secrets_resolver):
        assert kid.startswith(did)
    check_expected_did_doc(did,
                           auth_keys_count=1, agreement_keys_count=1,
                           service_endpoint=endpoint, service_routing_keys=None)


def test_create_peer_did_numalg_2_with_service_endpoint_and_routing(demo):
    endpoint = "https://my-endpoint"
    routing_keys = ["key1", "key2"]
    did = demo.create_peer_did(auth_keys_count=1, agreement_keys_count=1,
                               service_endpoint=endpoint,
                               service_routing_keys=routing_keys)
    assert is_peer_did(did)
    assert did.startswith("did:peer:2")
    assert len(get_secret_resolver_kids(demo.secrets_resolver)) == 2
    for kid in get_secret_resolver_kids(demo.secrets_resolver):
        assert kid.startswith(did)
    check_expected_did_doc(did,
                           auth_keys_count=1, agreement_keys_count=1,
                           service_endpoint=endpoint, service_routing_keys=routing_keys)


def test_resolve_peer_did():
    did = "did:peer:0z6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V"
    did_doc_json = DIDCommDemo.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK)
    did_doc = json.loads(did_doc_json)
    assert "authentication" in did_doc
    assert did_doc["id"] == did


@pytest.fixture()
def did_frm(demo):
    return demo.create_peer_did(auth_keys_count=2, agreement_keys_count=2,
                                service_endpoint="http://endpoint-from",
                                service_routing_keys=["key1", "key2"])


@pytest.fixture()
def did_to(demo):
    return demo.create_peer_did(auth_keys_count=2, agreement_keys_count=2,
                                service_endpoint="http://endpoint-to",
                                service_routing_keys=["key3", "key4"])


MESSAGES = ["hello", "111", '{"aaa": "bbb"}']


@pytest.mark.parametrize("input_msg", MESSAGES)
def test_pack_unpack_authcrypt(input_msg, demo, did_frm, did_to):
    packed_res = demo.pack(
        msg=input_msg,
        frm=did_frm,
        to=did_to
    )

    unpacked_msg, frm, to, unpack_res = demo.unpack(packed_res.packed_msg)
    assert input_msg == unpacked_msg
    assert frm == did_frm
    assert to == did_to
    assert unpack_res.metadata.authenticated is True
    assert unpack_res.metadata.encrypted is True
    assert unpack_res.metadata.anonymous_sender is True
    assert unpack_res.metadata.non_repudiation is False


@pytest.mark.parametrize("input_msg", MESSAGES)
def test_pack_anoncrypt(input_msg, demo, did_to):
    packed_res = demo.pack(
        msg=input_msg,
        to=did_to
    )

    unpacked_msg, frm, to, unpack_res = demo.unpack(packed_res.packed_msg)
    assert input_msg == unpacked_msg
    assert frm is None
    assert to == did_to
    assert unpack_res.metadata.authenticated is False
    assert unpack_res.metadata.encrypted is True
    assert unpack_res.metadata.anonymous_sender is True
    assert unpack_res.metadata.non_repudiation is False


@pytest.mark.parametrize("input_msg", MESSAGES)
def test_pack_authcrypt_signed(input_msg, demo, did_frm, did_to):
    packed_res = demo.pack(
        msg=input_msg,
        frm=did_frm,
        to=did_to,
        sign_frm=did_frm
    )

    unpacked_msg, frm, to, unpack_res = demo.unpack(packed_res.packed_msg)
    assert input_msg == unpacked_msg
    assert frm == did_frm
    assert to == did_to
    assert unpack_res.metadata.authenticated is True
    assert unpack_res.metadata.encrypted is True
    assert unpack_res.metadata.anonymous_sender is True
    assert unpack_res.metadata.non_repudiation is True


@pytest.mark.parametrize("input_msg", MESSAGES)
def test_pack_authcrypt_not_hidden_sender(input_msg, demo, did_frm, did_to):
    config = PackEncryptedConfig(protect_sender_id=False)
    packed_res = demo.pack(
        msg=input_msg,
        frm=did_frm,
        to=did_to,
        config=config
    )

    unpacked_msg, frm, to, unpack_res = demo.unpack(packed_res.packed_msg)
    assert input_msg == unpacked_msg
    assert frm == did_frm
    assert to == did_to
    assert unpack_res.metadata.authenticated is True
    assert unpack_res.metadata.encrypted is True
    assert unpack_res.metadata.anonymous_sender is False
    assert unpack_res.metadata.non_repudiation is False
