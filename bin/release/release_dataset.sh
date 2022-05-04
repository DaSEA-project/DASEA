#!/usr/bin/env bash

datasetFileName=$(poetry run dasea release)
echo "$datasetFileName"

# Release in Sandbox https://sandbox.zenodo.org/
# poetry run dasea push --sandbox --no-verify "data/out/$datasetFileName"

# Release in Zenodo https://zenodo.org/
poetry run dasea push --no-verify "data/out/$datasetFileName"
