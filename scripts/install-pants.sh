#/bin/bash

curl --proto '=https' --tlsv1.2 -fsSL https://static.pantsbuild.org/setup/get-pants.sh > get-pants.sh

chmod +x get-pants.sh

./get-pants.sh

rm -f get-pants.sh
