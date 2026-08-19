#!/bin/bash
echo "Setting up AEGIS Environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Setup Complete."
