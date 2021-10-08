import json

import pytest
from click.testing import CliRunner
from didcomm.secrets.secrets_resolver_demo import SecretsResolverDemo
from peerdid.peer_did import is_peer_did

from didcomm_demo.didcomm_cli import set_secrets_resolver, cli
from didcomm_demo.didcomm_demo import DIDCommDemo
from tests.common import get_secret_resolver_kids, check_expected_did_doc


@pytest.fixture()
def secrets_resolver(tmp_path):
    tmp_file = tmp_path / "secrets.json"
    secrets_resolver = SecretsResolverDemo(tmp_file)
    set_secrets_resolver(secrets_resolver)
    return secrets_resolver


def test_create_peer_did_numalg_0(secrets_resolver):
    runner = CliRunner()
    result = runner.invoke(cli, ['create-peer-did', '--auth-keys-count=1', '--agreement-keys-count=0'])
    assert result.exit_code == 0
    peer_did = result.output.strip()
    assert is_peer_did(peer_did)
    assert peer_did.startswith("did:peer:0")
    assert len(get_secret_resolver_kids(secrets_resolver)) == 1
    assert get_secret_resolver_kids(secrets_resolver)[0].startswith(peer_did)
    check_expected_did_doc(peer_did, auth_keys_count=1, agreement_keys_count=0, service_endpoint=None)


@pytest.mark.parametrize(
    "auth_keys_count,agreement_keys_count",
    [
        pytest.param(1, 1, id="1auth-1agreem"),
        pytest.param(2, 3, id="2auth-3agreem"),
        pytest.param(0, 1, id="0auth-1agreem"),
        pytest.param(0, 2, id="0auth-2agreem")
    ]
)
def test_create_peer_did_numalg_2_no_service(secrets_resolver, auth_keys_count, agreement_keys_count):
    runner = CliRunner()
    result = runner.invoke(cli, ['create-peer-did', f'--auth-keys-count={auth_keys_count}',
                                 f'--agreement-keys-count={agreement_keys_count}'])
    assert result.exit_code == 0
    peer_did = result.output.strip()
    assert is_peer_did(peer_did)
    assert peer_did.startswith("did:peer:2")
    assert len(get_secret_resolver_kids(secrets_resolver)) == auth_keys_count + agreement_keys_count
    for kid in get_secret_resolver_kids(secrets_resolver):
        assert kid.startswith(peer_did)
    check_expected_did_doc(peer_did, auth_keys_count=auth_keys_count, agreement_keys_count=agreement_keys_count,
                           service_endpoint=None)


def test_create_peer_did_numalg_2_with_service_endpoint_no_routing(secrets_resolver):
    runner = CliRunner()
    result = runner.invoke(cli, ['create-peer-did',
                                 '--auth-keys-count=1',
                                 '--agreement-keys-count=1',
                                 '--service-endpoint=https://my-endpoint'])
    assert result.exit_code == 0
    peer_did = result.output.strip()
    assert is_peer_did(peer_did)
    assert peer_did.startswith("did:peer:2")
    assert len(get_secret_resolver_kids(secrets_resolver)) == 2
    for kid in get_secret_resolver_kids(secrets_resolver):
        assert kid.startswith(peer_did)
    check_expected_did_doc(peer_did, auth_keys_count=1, agreement_keys_count=1, service_endpoint="https://my-endpoint")


def test_create_peer_did_numalg_2_with_service_endpoint_and_routing(secrets_resolver):
    runner = CliRunner()
    result = runner.invoke(cli, ['create-peer-did',
                                 '--auth-keys-count=1',
                                 '--agreement-keys-count=1',
                                 '--service-endpoint=https://my-endpoint',
                                 '--service-routing-key=key1',
                                 '--service-routing-key=key2'
                                 ], )
    assert result.exit_code == 0
    peer_did = result.output.strip()
    assert is_peer_did(peer_did)
    assert peer_did.startswith("did:peer:2")
    assert len(get_secret_resolver_kids(secrets_resolver)) == 2
    for kid in get_secret_resolver_kids(secrets_resolver):
        assert kid.startswith(peer_did)
    check_expected_did_doc(peer_did, auth_keys_count=1, agreement_keys_count=1, service_endpoint="https://my-endpoint",
                           service_routing_keys=["key1", "key2"])


def test_resolve_peer_did(secrets_resolver):
    did = "did:peer:0z6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V"
    runner = CliRunner()
    result = runner.invoke(cli, ['resolve-peer-did', did])
    assert result.exit_code == 0
    did_doc_json = result.output.strip()
    did_doc = json.loads(did_doc_json)
    assert "authentication" in did_doc
    assert did_doc["id"] == did


MESSAGES = ["hello", "111", '{"aaa": "bbb"}']


@pytest.fixture()
def did_frm(secrets_resolver):
    return DIDCommDemo(secrets_resolver).create_peer_did()


@pytest.fixture()
def did_to(secrets_resolver):
    return DIDCommDemo(secrets_resolver).create_peer_did()


@pytest.mark.parametrize("input_msg", MESSAGES)
def test_pack_unpack_authcrypt(input_msg, secrets_resolver, did_frm, did_to):
    runner = CliRunner()
    result = runner.invoke(cli, ['pack', input_msg,
                                 f'--from={did_frm}',
                                 f'--to={did_to}'])
    assert result.exit_code == 0
    packed_msg = result.output.strip()

    result = runner.invoke(cli, ['unpack', packed_msg])
    assert result.exit_code == 0
    res = result.output.strip()
    assert input_msg in res
    assert did_frm in res
    assert did_to in res


@pytest.mark.parametrize("input_msg", MESSAGES)
def test_pack_unpack_anoncrypt(input_msg, secrets_resolver, did_to):
    runner = CliRunner()
    result = runner.invoke(cli, ['pack', input_msg,
                                 f'--to={did_to}'])
    assert result.exit_code == 0
    packed_msg = result.output.strip()

    result = runner.invoke(cli, ['unpack', packed_msg])
    assert result.exit_code == 0
    res = result.output.strip()
    assert input_msg in res
    assert did_to in res
