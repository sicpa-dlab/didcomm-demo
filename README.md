# didcomm-demo
Showcase DIDComm V2 implementation.

- It shows how peerdid and didcomm libraries can be used together on the application level.
- It shows interoperability between Python and Java/Kotlin libraries.

### Content
- `didcomm-demo-jvm` - how [peerdid JVM](https://github.com/sicpa-dlab/peer-did-jvm) and [didcomm JVM](https://github.com/sicpa-dlab/didcomm-jvm) can be used together on the application level.
  - `didcomm-demo` module - peerdid+didcomm working together
  - [Demo.kt](didcomm-demo-jvm/didcomm-demo/src/main/kotlin/org/didcommx/didcomm/demo/Demo.kt) - JVM demo script
  - `didcomm-demo-cli` module - a simple CLI for demo purposes 
   
- `didcomm-demo-python` - how [peerdid Python](https://github.com/sicpa-dlab/peer-did-python) and [didcomm Python](https://github.com/sicpa-dlab/didcomm-python) can be used together on the application level.
  - [didcomm_demo.py](didcomm-demo-python/didcomm_demo/didcomm_demo.py) - peerdid+didcomm working together
  - [demo.py](didcomm-demo-python/demo.py) - Python demo script
  - [didcomm-cli](didcomm-demo-python/didcomm_demo/didcomm_cli.py) - a simple CLI for demo purposes 

### Installation
Prerequisites: Python 3.7+, Java 8+.

1) Create virtual environment for Python. For example,
    ```
    python3 -m venv ./venv
    source ./venv/bin/activate
    ```
2) Install Python part
  `cd didcomm-demo-python && pip install -e.[tests] && cd ..` 
3) Build and Install JVM part 
   `cd didcomm-demo-jvm && ./gradlew installDist && cd ..`

Steps 2 and 3 can be run via `./install.sh` on Linux.

### Running The Demo
After installation is done, just run `python3 demo.py` from the root repository folder. 

The Demo uses Python and JVM Demo CLIs to pass commands and prove interoperability.

### Demo CLI
Both Python and JVM Demo CLIs have the same interface.

They can work with peer DIDs only.

Secrets are stored in local files, so the Demo CLIs should be used for demo and test purposes only.

Commands:
- `create-peer-did`
- `resolve-peer-did <peer-did>`
- `pack <msg> --from <from-peer-did> --to <to-peer-did>`
- `unpack <msg>`

## Conforming Interoperability with 3d Party
If there is another DIDComm library implementation, one can check interoperability with these libs
(assuming the usage of peer DIDs only) by:
- passing a packed message from 3d party lib to the Demo CLI's `unpack` command
- pack a message via Demo CLI's `pack` command and pass the resulted JSON to the 3d party lib's unpack method
