import asyncio
import json

from peerdid.types import VerificationMaterialFormatPeerDID

from didcomm_demo.didcomm_demo import DIDCommDemo

TARGET_PEER_DID = (
        "did:peer:2"
        + ".Ez6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc"
        + ".Vz6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od935YF4s8M7V"
        + ".Vz6MkgoLTnTypo3tDRwCkZXSccTPHRLhF4ZnjhueYAFpEX6vg"
        + ".SeyJ0IjoiZG0iLCJzIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9lbmRwb2ludCIsInIiOlsiZGlkOmV4YW1wbGU6c29tZW1lZGlhdG9yI3NvbWVrZXkiXSwiYSI6WyJkaWRjb21tL3YyIiwiZGlkY29tbS9haXAyO2Vudj1yZmM1ODciXX0="
)


def get_secret_resolver_kids(secrets_resolver):
    return asyncio.get_event_loop().run_until_complete(
        secrets_resolver.get_kids()
    )


def check_expected_did_doc(did, auth_keys_count, agreement_keys_count, service_endpoint=None,
                           service_routing_keys=None):
    did_doc = json.loads(DIDCommDemo.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK))
    assert len(did_doc.get("authentication", [])) == auth_keys_count
    assert len(did_doc.get("keyAgreement", [])) == agreement_keys_count
    if service_endpoint is None:
        assert "service" not in did_doc
    else:
        assert did_doc.get("service")[0]["serviceEndpoint"] == service_endpoint
        assert did_doc.get("service")[0]["accept"] == ["didcomm/v2"]
        if service_routing_keys is not None:
            assert did_doc.get("service")[0]["routingKeys"] == service_routing_keys
