package org.didcommx.didcomm.demo

fun main() {
    println()

    val demo = DIDCommDemoHelper()

    // 1. Bob creates a pairwise peer DID for the connection
    val bobPeerDID = demo.createPeerDID()
    println("Bob generates a new pairwise peer DID for communication with Alice: `$bobPeerDID`.")
    println()

    // 2. Alice creates a pairwise peer DID for the connection
    val alicePeerDID = demo.createPeerDID()
    println("Alice generates a new pairwise peer DID for communication with Bob: `$alicePeerDID`.")

    // 3. Alice sends message to Bob
    val msg = "Hello Bob!"
    val packedToBob = demo.pack(msg, from = alicePeerDID, to = bobPeerDID)
    println("Alice sends '$msg' to Bob.")
    println("The message is authenticated by Alice's peer DID `$alicePeerDID` and encrypted to Bob's peer DID `$bobPeerDID`")
    println()

    // 4. Bob unpacks the message
    val unpackResult = demo.unpack(packedToBob.packedMessage)
    println("Bob received '${unpackResult.message}' from Alice.")
    print("The message is authenticated by Alice's peer DID `${unpackResult.from}` and encrypted to Bob's peer DID `${unpackResult.to}`.")
}
