#!/bin/bash

ROOTS=$(pants roots --roots-sep=' ')
for ROOT in $ROOTS; do
    if [[ $ROOT == "libs/"* ]]; then
        echo "#################################################################"
        echo "Installing $ROOT locally"
        echo "#################################################################"
        pip install -e $ROOT
    fi
done
