# didcomm-demo
Showcase DIDComm V2 implementation.

- It shows how peerdid and didcomm libraries can be used together on the application level.
- It shows interoperability between Python and Java/Kotlin libraries.

## Content
- `didcomm-demo-jvm` - how [peerdid JVM](https://github.com/sicpa-dlab/peer-did-jvm) and [didcomm JVM](https://github.com/sicpa-dlab/didcomm-jvm) can be used together on the application level.
  - `didcomm-demo` module - peerdid+didcomm working together
  - [Demo.kt](didcomm-demo-jvm/didcomm-demo/src/main/kotlin/org/didcommx/didcomm/demo/Demo.kt) - JVM demo script
  - `didcomm-demo-cli` module - a simple CLI for demo purposes 
   
- `didcomm-demo-python` - how [peerdid Python](https://github.com/sicpa-dlab/peer-did-python) and [didcomm Python](https://github.com/sicpa-dlab/didcomm-python) can be used together on the application level.
  - [didcomm_demo.py](didcomm-demo-python/didcomm_demo/didcomm_demo.py) - peerdid+didcomm working together
  - [demo.py](didcomm-demo-python/demo.py) - Python demo script
  - [didcomm-cli](didcomm-demo-python/didcomm_demo/didcomm_cli.py) - a simple CLI for demo purposes 

## Installation
Prerequisites: Python 3.7+, Java 8+.

1) Create virtual environment for Python
2) Install Python part
  `cd didcomm-demo-python && pip install -e.[tests] && cd ..` 
3) Build JVM part 
   `cd didcomm-demo-jvm && ./gradlew build && cd ..`

## Running The Demo
After installation is done, just run `python demo.py` from the root repository folder. 
