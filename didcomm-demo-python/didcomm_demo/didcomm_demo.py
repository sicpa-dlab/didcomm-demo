import asyncio
import json
from typing import Optional, List

from didcomm.common.resolvers import ResolversConfig
from didcomm.common.types import DID, JSON
from didcomm.core.utils import id_generator_default, get_did
from didcomm.message import Message
from didcomm.pack_encrypted import pack_encrypted, PackEncryptedResult, PackEncryptedConfig
from didcomm.secrets.secrets_resolver_demo import SecretsResolverDemo
from didcomm.secrets.secrets_resolver_editable import SecretsResolverEditable
from didcomm.secrets.secrets_util import generate_x25519_keys_as_jwk_dict, generate_ed25519_keys_as_jwk_dict, \
    jwk_to_secret
from didcomm.unpack import unpack, UnpackResult
from peerdid import peer_did
from peerdid.core.did_doc_types import DIDCommServicePeerDID
from peerdid.did_doc import DIDDocPeerDID
from peerdid.types import VerificationMaterialFormatPeerDID, VerificationMaterialAgreement, \
    VerificationMethodTypeAgreement, VerificationMaterialAuthentication, VerificationMethodTypeAuthentication

from didcomm_demo.did_resolver_peer_did import DIDResolverPeerDID


class DIDCommDemo:

    def __init__(self, secrets_resolver: Optional[SecretsResolverEditable] = None) -> None:
        self.secrets_resolver = secrets_resolver or SecretsResolverDemo()
        self.resolvers_config = ResolversConfig(
            secrets_resolver=self.secrets_resolver,
            did_resolver=DIDResolverPeerDID()
        )

    def create_peer_did(self,
                        auth_keys_count: int = 1,
                        agreement_keys_count: int = 1,
                        service_endpoint: Optional[str] = None,
                        service_routing_keys: Optional[List[str]] = None
                        ) -> str:
        # 1. generate keys in JWK format
        agreem_keys = [generate_x25519_keys_as_jwk_dict() for _ in range(agreement_keys_count)]
        auth_keys = [generate_ed25519_keys_as_jwk_dict() for _ in range(auth_keys_count)]

        # 2. prepare the keys for peer DID lib
        agreem_keys_peer_did = [
            VerificationMaterialAgreement(
                type=VerificationMethodTypeAgreement.JSON_WEB_KEY_2020,
                format=VerificationMaterialFormatPeerDID.JWK,
                value=k[1],
            )
            for k in agreem_keys
        ]
        auth_keys_peer_did = [
            VerificationMaterialAuthentication(
                type=VerificationMethodTypeAuthentication.JSON_WEB_KEY_2020,
                format=VerificationMaterialFormatPeerDID.JWK,
                value=k[1],
            )
            for k in auth_keys
        ]

        # 3. generate service
        service = None
        if service_endpoint:
            service = json.dumps(
                DIDCommServicePeerDID(
                    id="new-id",
                    service_endpoint=service_endpoint, routing_keys=service_routing_keys,
                    accept=["didcomm/v2"]
                ).to_dict()
            )

        # 4. call peer DID lib
        # if we have just one key (auth), then use numalg0 algorithm
        # otherwise use numalg2 algorithm
        if len(auth_keys_peer_did) == 1 and not agreem_keys_peer_did and not service:
            did = peer_did.create_peer_did_numalgo_0(auth_keys_peer_did[0])
        else:
            did = peer_did.create_peer_did_numalgo_2(
                encryption_keys=agreem_keys_peer_did,
                signing_keys=auth_keys_peer_did,
                service=service,
            )

        # 5. set KIDs as in DID DOC for secrets and store the secret in the secrets resolver
        did_doc = DIDDocPeerDID.from_json(peer_did.resolve_peer_did(did))
        for auth_key, kid in zip(auth_keys, did_doc.auth_kids):
            private_key = auth_key[0]
            private_key["kid"] = kid
            asyncio.get_event_loop().run_until_complete(
                self.secrets_resolver.add_key(jwk_to_secret(private_key))
            )
        for agreem_key, kid in zip(agreem_keys, did_doc.agreement_kids):
            private_key = agreem_key[0]
            private_key["kid"] = kid
            asyncio.get_event_loop().run_until_complete(
                self.secrets_resolver.add_key(jwk_to_secret(private_key))
            )

        return did

    @staticmethod
    def resolve_peer_did(did: DID, format: VerificationMaterialFormatPeerDID.JWK) -> JSON:
        return peer_did.resolve_peer_did(did, format=format)

    def pack(self,
             msg: str,
             to: str,
             frm: Optional[str] = None,
             sign_frm: Optional[str] = None,
             config: Optional[PackEncryptedConfig] = None) -> PackEncryptedResult:
        message = Message(
            body={"msg": msg},
            id=id_generator_default(),
            type="my-protocol/1.0",
            frm=frm,
            to=[to],
        )
        config = config or PackEncryptedConfig(protect_sender_id=True)
        config.forward = False  # until it's support in all languages
        return asyncio.get_event_loop().run_until_complete(
            pack_encrypted(
                resolvers_config=self.resolvers_config,
                message=message,
                frm=frm,
                to=to,
                sign_frm=sign_frm,
                pack_config=config
            )
        )

    def unpack(self, packed_msg: str) -> (str, str, UnpackResult):
        res = asyncio.get_event_loop().run_until_complete(
            unpack(
                resolvers_config=self.resolvers_config,
                packed_msg=packed_msg
            )
        )
        msg = res.message.body["msg"]
        frm = get_did(res.metadata.encrypted_from) if res.metadata.encrypted_from else None
        to = get_did(res.metadata.encrypted_to[0])
        return msg, frm, to, res
