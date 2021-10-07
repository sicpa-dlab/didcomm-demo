from didcomm_demo.didcomm_demo import DIDCommDemo

if __name__ == '__main__':
    print("\n")
    demo = DIDCommDemo()

    # 1. Bob creates a pairwise peer DID for the connection
    bob_peer_did = demo.create_peer_did(auth_keys_count=1, agreement_keys_count=1,
                                        service_endpoint="http://service",
                                        service_routing_keys=["key1", "key2"])
    print(f"Bob generates a new pairwise peer DID for communication with Alice: `{bob_peer_did}`.")
    print("\n")

    # 2. Alice creates a pairwise peer DID for the connection
    alice_peer_did = demo.create_peer_did()
    print(f"Alice generates a new pairwise peer DID for communication with Bob: `{alice_peer_did}`.")

    # 3. Alice sends message to Bob
    msg_bob = "Hello Bob!"
    packed_to_bob = demo.pack(msg="Hello Bob!", frm=alice_peer_did, to=bob_peer_did)
    print(f"Alice sends '{msg_bob}' to Bob.")
    print(
        f"The message is authenticated by Alice's peer DID `{alice_peer_did}` and encrypted to Bob's peer DID `{bob_peer_did}`")
    print("\n")

    # 4. Bob unpacks the message
    unpacked_msg, frm_did, to_did, _ = demo.unpack(packed_to_bob.packed_msg)
    print(f"Bob received '{unpacked_msg}' from Alice.")
    print(f"The message is authenticated by Alice's peer DID `{frm_did}` and encrypted to Bob's peer DID `{to_did}`.")
