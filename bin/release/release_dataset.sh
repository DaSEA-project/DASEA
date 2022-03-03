#!/usr/bin/env bash

datasetFileName=$(poetry run dasea release)
echo "$datasetFileName"

# FIXME: should change the ZENODO_API_TOKEN when we move away from the sandbox
poetry run dasea push --sandbox --no-verify "data/out/$datasetFileName"