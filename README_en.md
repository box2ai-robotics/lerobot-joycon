# LeRobot-JoyCon: Making AI for Robotics more accessible and Portable with JoyCon

<p align="center">
  <a href="README_en.md">English</a> •
  <a href="README.md">中文</a> 
</p>

## Declaration

This is a Lerobot branch for local acquisition deployment for the Chinese community (for some reason), and adds portable controls for Joycon as well as positive and negative kinematics controls.

This repository is a fork of the following projects,:
- [lerobot](https://github.com/huggingface/lerobot)
- [joycon-robotics](https://github.com/box2ai-robotics/joycon-robotics)
- [lerobot-kinematics](https://github.com/box2ai-robotics/lerobot-kinematics)

&nbsp;

# LeRobot-JoyCon: Making Embodied AI Easier and More Portable Using JoyCon

## (〇) Statement

This is a Chinese community branch of LeRobot. In addition to providing complete installation and testing instructions, it mainly includes the following modifications:

#### 1. Basics

(1) Fixed port mapping: based on the factory serial number of the driver board, the udev configuration maps the port number, so there's no need to check USB ttyACM every time you plug in the cable, avoiding calibration file errors 😨.

(2) Localized data collection, training, and inference: avoids issues like network hangs or login failures. The steps for the related configuration changes are also provided 🏫.

(3) Solutions for common problems are listed, and you're welcome to report any issues you find — they will be promptly added ❌.

(4) Optimized dataset directory detection: it will automatically detect whether the dataset exists. If it does, recording will continue without error ⏺.

#### 2. Advanced

(1) Summarized several suggestions for model and dataset optimization 🔨

(2) Provided parameter tuning suggestions for the Diffusion Transformer Policy 🌟

(3) Integrated JoyCon remote control for data collection 🎮🎮🎮

#### 3. Further Discussion

For more discussion and communication, you can join the QQ group: 948755626

&nbsp;

# (1) Installing LeRobot

### 0. System Requirements

  1. Ubuntu 20.04 or 22.04 (Dual-boot version; Virtual machines, WSL, and Windows are not supported)
  2. Bluetooth connectivity
  3. Nvidia discrete GPU

### 1. Install MiniConda3

```shell
# If you haven't installed conda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

### 2. Configure the lerobot environment using conda

```shell
conda create -y -n lerobot python=3.10
conda activate lerobot
# cd lerobot-joycon
pip install -e .

# For Feetech servo version SO100
pip install -e ".[feetech]"
conda install -y -c conda-forge ffmpeg
pip uninstall -y opencv-python
conda install -y -c conda-forge "opencv>=4.10.0"

# Configure library path links. If you're not using miniconda3, replace it with your conda environment path, possibly miniforge
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/miniconda3/envs/lerobot/lib' >> ~/.bashrc 
source ~/.bashrc
conda activate lerobot

# Environment configuration tips: Please ensure you’ve installed the NVIDIA driver (check under Software & Updates => Additional Drivers)
# sudo apt install nvidia-driver-<replace with your version>
pip uninstall -y numpy pynput 
pip install numpy==1.24.4 pynput==1.7.7
python -m pip uninstall -y torch torchvision torchaudio 
python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

- For network-related errors, please refer to [bugs_Q&A.md#L1](bugs_Q&A.md#L1)

### 3. Lerobot Directory Overview

  (1) The main models and configuration files are located in the ``lerobot`` directory. Other sibling directories like docker, media, etc., are not important.
  
  (2) The main **configuration** folder is ``lerobot/configs``, with particular focus on:
  - ``Robot``: ``lerobot/configs/robot/so100.yaml``
  - ``Policy``: ``lerobot/configs/policy/act_so100_real.yaml``
  
  (3) The script ``lerobot/scripts/control_robot.py`` in ``lerobot/scripts`` is the main Python entry point to control the robot.
  
  (4) Main files for **model training and inference**:
    - Training: ``lerobot/scripts/train.py``
    - Inference: ``lerobot/scripts/eval.py``
  
  (5) Other files and directories can be explored freely after getting familiar with the basics.

Note: It is recommended to ``open the lerobot-joycon project directory using VSCode``. After opening the readme.md file, click the second icon from the left in the top right corner ``"Open Preview Side Panel"`` for a cleaner and more visually appealing layout~

&nbsp;

# (2) Robotic Arm Configuration

#### To configure 1 robotic arm + 1 JoyCon, please refer to the manual: [Single_tutorial.md](Single_tutorial_en.md)

#### To configure 2 robotic arms + 2 JoyCons, please refer to the manual: [Double_tutorial.md](Double_tutorial_en.md)

# (3) More

1. For more showcases and related videos, you can follow our [Bilibili account](https://space.bilibili.com/122291348)
2. For more discussions and communication, you can join the QQ group: 948755626
3. [Click here](https://item.taobao.com/item.htm?abbucket=16&detail_redpacket_pop=true&id=906794552661&ltk2=17440907659690jpsj3h7uiismft7vle37&ns=1&skuId=5933796995638) to visit our Taobao store and purchase our carefully fine-tuned robotic arm and JoyCon bundle

If you find this project helpful, please consider giving us a star! ⭐ ⭐ ⭐ ⭐ ⭐
