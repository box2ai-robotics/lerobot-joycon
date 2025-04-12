# LeRobot-JoyCon: Making AI for Robotics more accessible and Portable with JoyCon

## Declaration

This is a Lerobot branch for local acquisition deployment for the Chinese community (for some reason), and adds portable controls for Joycon as well as positive and negative kinematics controls.

This repository is a fork of the following projects,:
- [lerobot](https://github.com/huggingface/lerobot)
- [joycon-robotics](https://github.com/box2ai-robotics/joycon-robotics)
- [lerobot-kinematics](https://github.com/box2ai-robotics/lerobot-kinematics)

&nbsp;

# LeRobot-JoyCon: 利用 JoyCon 让机器人具身智能更易于使用和携带

## (〇) 声明

这是一个LeRobot的中国社区分支，除了包含完整的安装和测试指令外，还主要有以下修改：

#### 1. 基础

(1) 端口号固定映射，根据驱动板出场serial序列固定端口号映射udev的配置，无需每次插线都检查USBttyACM，生怕校准文件错乱😨。

(2) 本地化采集训练和推理，免除网络问题卡死或者登录失败的情况，相关步骤配置修改的步骤也列出了🏫。

(3) 常见的问题给出了解决方案，也欢迎将发现的问题提出，会立即补充更新❌。

(4) 优化了数据集目录检测机制，自动检测数据集是否存在，如果存在不会报错，而是接续录制⏺。

#### 2. 进阶

(1) 归纳了几点模型、数据集优化意见🔨 

(2) Diffusion Transformer Policy 参数修改优化意见🌟

(3) 适配joycon遥操做控制数据采集🎮🎮🎮。

#### 3. 更多讨论

更多讨论和交流可以加入QQ群：948755626

&nbsp;

# (一) 安装Lerobot

### 0. 系统要求

  1. Ubuntu 20.04, 22.04 （双系统版，暂不支持虚拟机，WLS，Windows）
  2. 可连接蓝牙设备
  3. 有Nvidia独显
  
### 1. 安装MiniConda3
  
```shell
# 如果你没有安装conda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
```

### 2. 使用conda配置lerobot环境

```shell
conda create -y -n lerobot python=3.10
conda activate lerobot
# cd lerobot-joycon
pip install -e .

# 使用飞特舵机的版本SO100
pip install -e ".[feetech]"
conda install -y -c conda-forge ffmpeg
pip uninstall -y opencv-python
conda install -y -c conda-forge "opencv>=4.10.0"

# 配置库文件链接，如果您没有安装miniconda3，请将其中的miniconda3更换成你的conda环境，或许是miniforge
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/miniconda3/envs/lerobot/lib' >> ~/.bashrc 
source ~/.bashrc
conda activate lerobot

# 环境配置技巧，请保证你已经安装了nvidia-driver，在【软件与更新=>附加驱动 中查看】
# sudo apt install nvidia-driver-<切换成你的版本>
pip uninstall -y numpy pynput
pip install numpy==1.24.4 pynput==1.7.7
python -m pip uninstall -y torch torchvision torchaudio 
python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

- network网络报错，请查看[bugs_Q&A.md#L1](bugs_Q&A.md#L1)

### 3. Lerobot 目录简述

  (1) 主要的模型和配置文件在``lerobot``中，其余同级目录如docker,media等不重要
  
  (2) 主要**配置**文件夹是``lerobot/configs``，其中重点关注，
  - ``机器人(robot)``的``lerobot/configs/robot/so100.yaml``
  - ``模型(policy)``的``lerobot/configs/policy/act_so100_real.yaml``
  
  (3) ``lerobot/scripts``中的``lerobot/scripts/control_robot.py``是控制机器人的入口python程序。
  
  (4) **模型训练和推理**的主要文件是：``训练 lerobot/scripts/train.py``， ``推理 lerobot/scripts/eval.py``
  
  (5) 其余的文件和目录入门之后可自行探索。

Note: 建议``使用Vscode打开lerobot-joycon工程目录``，打开readme.md文件之后右上角从左到右第二个图标``"打开侧边栏预览"``，可以查看更加美观的排版哦~

&nbsp;

# (二) 机械臂配置

#### 配置单臂，请参考手册： [Single_tutorial.md](Single_tutorial.md)

#### 配置双臂，请参考手册： [Double_tutorial.md](Double_tutorial.md)


# (三)更多
1. 更多展示和相关视频可以关注[bilibili账号](https://space.bilibili.com/122291348)
2. 更多讨论和交流可以加入QQ群：948755626
3. [点击这里](https://item.taobao.com/item.htm?abbucket=16&detail_redpacket_pop=true&id=906794552661&ltk2=17440907659690jpsj3h7uiismft7vle37&ns=1&skuId=5933796995638) 可以跳转我们的淘宝店铺，选购经过我们精心微调的机械臂和手柄套装

如果你觉得这对你有帮助，请您帮我们点一颗小星星吧！ ⭐ ⭐ ⭐ ⭐ ⭐