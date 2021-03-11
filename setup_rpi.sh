# Setup file for the Raspberry pi controller

sudo apt-get update
if conda list > /dev/null
then
    echo "conda already installed"
    conda update conda
else
    echo "Berryconda not installed please install the appropriate version"
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
python -m pip install --upgrade pip

# installing MQTT dependencies
echo "================================================================================"
echo "==================== Installing MQTT Dependencies  ============================="
echo "================================================================================"

pip install paho-mqtt

# installing Gesutre dependencies
echo "================================================================================"
echo "==================== Installing Gesture Dependencies  =========================="
echo "================================================================================"
conda install pandas
python -m pip install Rpi.GPIO
sudo apt-get install git i2c-tools libi2c-dev
conda install numpy
python -m pip install smbus
python -m pip install PyQt5