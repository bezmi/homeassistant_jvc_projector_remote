#!/bin/bash

# Copy over the jvcprojector component
mkdir -p /config/custom_components/jvcprojector
cp -f __init__.py /config/custom_components/jvcprojector/__init__.py
cp -f remote.py /config/custom_components/jvcprojector/remote.py
cp -f manifest.json /config/custom_components/jvcprojector/manifest.json
cp -f services.yaml /config/custom_components/jvcprojector/services.yaml
