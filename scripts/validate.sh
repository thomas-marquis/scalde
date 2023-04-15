#!/bin/bash

set -e

pants tailor --check update-build-files --check ::
pants lint ::
pants test ::
