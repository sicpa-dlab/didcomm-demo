package org.didcommx.didcomm.demo

import org.didcommx.didcomm.DIDComm
import org.didcommx.didcomm.message.Message
import org.didcommx.didcomm.model.PackEncryptedParams
import org.didcommx.didcomm.model.PackEncryptedResult
import org.didcommx.didcomm.model.UnpackParams
import org.didcommx.didcomm.secret.*
import org.didcommx.didcomm.utils.divideDIDFragment
import org.didcommx.didcomm.utils.toJson
import org.didcommx.peerdid.*
import java.util.*

class DIDCommDemoHelper(secretsResolver: SecretResolverEditable? = null) {

    data class UnpackResult(
        val message: String,
        val from: String?,
        val to: String,
        val res: org.didcommx.didcomm.model.UnpackResult
    )

    companion object {
        fun resolvePeerDID(did: String, format: VerificationMaterialFormatPeerDID) =
            org.didcommx.peerdid.resolvePeerDID(did, format)
    }

    val secretsResolver = secretsResolver ?: SecretResolverDemo()

    fun createPeerDID(
        authKeysCount: Int = 1,
        agreementKeysCount: Int = 1,
        serviceEndpoint: String? = null,
        serviceRoutingKeys: List<String>? = null
    ): String {
        // 1. generate keys in JWK format
        val x25519keyPairs = (1..agreementKeysCount).map { generateX25519Keys() }
        val ed25519keyPairs = (1..authKeysCount).map { generateEd25519Keys() }

        // 2. prepare the keys for peer DID lib
        val authPublicKeys = ed25519keyPairs.map {
            VerificationMaterialAuthentication(
                format = VerificationMaterialFormatPeerDID.JWK,
                type = VerificationMethodTypeAuthentication.JSON_WEB_KEY_2020,
                value = it.public
            )
        }
        val agreemPublicKeys = x25519keyPairs.map {
            VerificationMaterialAgreement(
                format = VerificationMaterialFormatPeerDID.JWK,
                type = VerificationMethodTypeAgreement.JSON_WEB_KEY_2020,
                value = it.public
            )
        }

        // 3. generate service
        val service = serviceEndpoint?.let {
            toJson(
                DIDCommServicePeerDID(
                    id = "new-id",
                    type = SERVICE_DIDCOMM_MESSAGING,
                    serviceEndpoint = it,
                    routingKeys = serviceRoutingKeys,
                    accept = listOf("didcomm/v2")
                ).toDict()
            )
        }

        // 4. call peer DID lib
        // if we have just one key (auth), then use numalg0 algorithm
        // otherwise use numalg2 algorithm
        val did = if (authPublicKeys.size == 1 && agreemPublicKeys.isEmpty() && service.isNullOrEmpty())
            createPeerDIDNumalgo0(authPublicKeys[0])
        else
            createPeerDIDNumalgo2(
                signingKeys = authPublicKeys,
                encryptionKeys = agreemPublicKeys,
                service = service
            )

        // 5. set KIDs as in DID DOC for secrets and store the secret in the secrets resolver
        val didDoc = DIDDocPeerDID.fromJson(resolvePeerDID(did, VerificationMaterialFormatPeerDID.JWK))
        didDoc.agreementKids.zip(x25519keyPairs).forEach {
            val privateKey = it.second.private.toMutableMap()
            privateKey["kid"] = it.first
            secretsResolver.addKey(jwkToSecret(privateKey))
        }
        didDoc.authenticationKids.zip(ed25519keyPairs).forEach {
            val privateKey = it.second.private.toMutableMap()
            privateKey["kid"] = it.first
            secretsResolver.addKey(jwkToSecret(privateKey))
        }

        return did
    }

    fun pack(
        data: String,
        to: String,
        from: String? = null,
        signFrom: String? = null,
        protectSender: Boolean = true
    ): PackEncryptedResult {
        val didComm = DIDComm(DIDDocResolverPeerDID(), secretsResolver)
        val message = Message.builder(
            id = UUID.randomUUID().toString(),
            body = mapOf("msg" to data),
            type = "my-protocol/1.0"
        ).build()
        var builder = PackEncryptedParams
            .builder(message, to)
            .forward(false)
            .protectSenderId(protectSender)
        builder = from?.let { builder.from(it) } ?: builder
        builder = signFrom?.let { builder.signFrom(it) } ?: builder
        val params = builder.build()
        return didComm.packEncrypted(params)
    }

    fun unpack(packedMsg: String): UnpackResult {
        val didComm = DIDComm(DIDDocResolverPeerDID(), secretsResolver)
        val res = didComm.unpack(UnpackParams.Builder(packedMsg).build())
        val msg = res.message.body["msg"].toString()
        val to = res.metadata.encryptedTo?.let { divideDIDFragment(it.first()).first() } ?: ""
        val from = res.metadata.encryptedFrom?.let { divideDIDFragment(it).first() }
        return UnpackResult(
            message = msg,
            from = from, to = to, res = res
        )
    }
}
