#!/bin/bash

ROOTS=$(pants roots --roots-sep=' ')
python -c "print('PYTHONPATH=\"./' + ':./'.join(\"${ROOTS}\".split()) + ':\$PYTHONPATH\"')" >> .env
export $(cat .env | xargs)
