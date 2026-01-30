#!/bin/bash

# Define virtual environment path
VENV_PATH="/root/clawd/composio_venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv $VENV_PATH
fi

# Activate virtual environment and install packages
echo "Activating virtual environment and installing Composio packages..."
source $VENV_PATH/bin/activate

pip install composio-core composio-openai -q

echo "\nVerifying Composio installation..."
python3 -c "import composio_core; import composio_openai; print('Composio packages successfully imported.')"

# Then execute the composio_integration.py script using the venv's python
echo "\nRunning composio_integration.py..."
python3 /root/clawd/composio_integration.py

# Deactivate virtual environment (optional, but good practice)
deactivate
