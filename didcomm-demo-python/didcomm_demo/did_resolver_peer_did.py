import json
from typing import Optional

from didcomm.common.types import DID, VerificationMethodType, VerificationMaterial, VerificationMaterialFormat
from didcomm.did_doc.did_doc import DIDDoc, VerificationMethod, DIDCommService
from didcomm.did_doc.did_resolver import DIDResolver
from peerdid import peer_did
from peerdid.core.did_doc_types import DIDCommServicePeerDID
from peerdid.did_doc import DIDDocPeerDID
from peerdid.types import VerificationMaterialFormatPeerDID


class DIDResolverPeerDID(DIDResolver):

    async def resolve(self, did: DID) -> Optional[DIDDoc]:
        # request DID Doc in JWK format
        did_doc_json = peer_did.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK)
        did_doc = DIDDocPeerDID.from_json(did_doc_json)

        return DIDDoc(
            did=did_doc.did,
            key_agreement_kids=did_doc.agreement_kids,
            authentication_kids=did_doc.auth_kids,
            verification_methods=[
                VerificationMethod(
                    id=m.id,
                    type=VerificationMethodType.JSON_WEB_KEY_2020,
                    controller=m.controller,
                    verification_material=VerificationMaterial(
                        format=VerificationMaterialFormat.JWK,
                        value=json.dumps(m.ver_material.value)
                    )
                )
                for m in did_doc.authentication + did_doc.key_agreement
            ],
            didcomm_services=[
                DIDCommService(
                    id=s.id,
                    service_endpoint=s.service_endpoint,
                    routing_keys=s.routing_keys,
                    accept=s.accept
                )
                for s in did_doc.service
                if isinstance(s, DIDCommServicePeerDID)
            ] if did_doc.service else []
        )
