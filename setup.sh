#!/bin/bash

if conda list > /dev/null
then
    echo "conda already installed"
    conda update conda
else
    echo "conda not installed please install the appropriate version"
fi

#setup conda environment
if conda env list |grep meat > /dev/null
then
    echo "Installing dependencies to Conda envrionment : meat"
else
    conda create -n meat python=3.6
fi

# activate conda environment
conda init bash
eval "$(conda shell.bash hook)"
conda activate meat

# installing audio dependencies
echo "================================================================================"
echo "==================== Installing Audio Dependencies ============================="
echo "================================================================================"
sudo apt-get install portaudio19-dev python-all-dev python3-all-dev libpulse-dev swig

python -m pip install --upgrade pip pyaudio setuptools wheel

python -m pip install --upgrade pocketsphinx

python -m pip install SpeechRecognition

# installing MQTT dependencies
echo "================================================================================"
echo "==================== Installing MQTT Dependencies  ============================="
echo "================================================================================"

conda install -c conda-forge paho-mqtt

# installing Homography dependencies
echo "================================================================================"
echo "==================== Installing Homography Dependencies  ======================="
echo "================================================================================"
conda install -c conda-forge opencv=4.1.1

# installing Gesutre dependencies
echo "================================================================================"
echo "==================== Installing Gesture Dependencies  =========================="
echo "================================================================================"
conda install -c conda-forge cvxpy
conda install pandas

# installing UI dependencies
echo "================================================================================"
echo "==================== Installing UI Dependencies  ==============================="
echo "================================================================================"
conda install -c anaconda pyqt
conda install numpy=1.19

echo "Dependency setup done!"