#!/bin/sh
cd didcomm-demo-python && pip install -e.[tests] && cd ..
cd didcomm-demo-jvm && ./gradlew installDist && cd ..