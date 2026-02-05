#!/bin/bash
# wrapper to ensure ~/.local/bin is on PATH and run chimera setup
export PATH="$HOME/.local/bin:$PATH"
echo "PATH="$PATH
bash chimera-setup.sh
