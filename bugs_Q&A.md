### 安装/下载/pip/apt/make通用报错

！！ 如果你遇到报错，请检查是否报错中存在 ``network`` ， ``timeout``等网络问题，请检查pip是否更换为国内镜像源，具体参考[pip清华源替换](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)，[Ubuntu apt清华源替换](https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/)

另外推荐Clash梯子为终端开启全局代理，并且为终端开启代理
```shell
  export http_proxy=http://127.0.0.1:7890
  export https_proxy=$http_proxy
```

### 官方机械臂端口号查询预设值(不推荐)

使用步骤：
  (1) 插上机械臂驱动板，
  
  (2) 打开一个终端窗口，输入如下指令
  
```shell
python lerobot/scripts/find_motors_bus_port.py
```
  (3) **拔掉**机械臂的驱动板USB，
  
  (4) 在输入指令的终端窗口敲击回车，即可检测到拔掉的是哪个端口
  
  (5) 更新到 ``lerobot/configs/robot/so100.yaml`` 中的 ``port``中，对应好主臂和从臂

### 校准/连接机械臂通用报错
报错ConnectionError: Read failed due to communication error on port /dev/lerobot_right for group_key Torque_Enable_shoulder_pan_shoulder_lift_elbow_flex_wrist_flex_wrist_roll_gripper: [TxRxResult] There is no status packet!

请检查``机械臂电源``和``USB线``以及``机械臂关节舵机的插线是否松了``，可以使用螺丝刀一个一个顶一下。

### 官方主臂校准图

| 1. Leader Zero position | 2. Leader Rotated position | 3. Leader Rest position |
|---|---|---|
| <img src="./media/so100/leader_zero.webp?raw=true" alt="SO-100 leader arm zero position" title="SO-100 leader arm zero position" style="max-width: 300px; height: auto;"> | <img src="./media/so100/leader_rotated.webp?raw=true" alt="SO-100 leader arm rotated position" title="SO-100 leader arm rotated position" style="max-width: 300px; height: auto;"> | <img src="./media/so100/leader_rest.webp?raw=true" alt="SO-100 leader arm rest position" title="SO-100 leader arm rest position" style="max-width: 300px; height: auto;"> |

### 机械臂遥操作校准数据异常问题
如果报错``ValueError: No integer found between bounds [low_factor=-0.00146484375, upp_factor=-0.00146484375]``,

说明双臂校准的时候主从比刚好反了，请重新运行上面的指令重新校准，从左边的机械臂开始。

### 手柄控制OpenGL/GLX报错
如果遇到错误 "GLFWError: (65543) b'GLX: Failed to create context: BadValue (integer paraneter out of range for operation)'
warnings.warn(nessage,GLFWError) the Mu ERROR: could not create window"，并且使用的是 ubuntu 21.04，

这可能是因为你的电脑默认使用集成显卡，不支持 mujoco 可视化，请运行以下命令切换到独立显卡。
```shell
sudo prime-select nvidia
sudo reboot
```

### 开启摄像头之后程序卡死/毫无反应/无报错问题/从臂不跟着主臂一起动
因为opencv没办法可视化(display)的问题，具体与opencv和cuda有关
```shell
conda install -y -c conda-forge ffmpeg
pip uninstall -y opencv-python
conda install -y -c conda-forge "opencv>=4.10.0"

pip uninstall -y numpy pynput
pip install numpy==1.24.4 pynput==1.7.7
python -m pip uninstall -y torch torchvision torchaudio 
python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

### 找不到摄像头/查看相机ID/查看摄像头设备问题
```shell
python lerobot/common/robot_devices/cameras/opencv.py
```
输出信息中应当关注的是：

```bash
  # OpenCVCamera(2, fps=10, width=640, height=480, color_mode=rgb)
  # OpenCVCamera(0, fps=30, width=640, height=480, color_mode=rgb)
```

其中0是笔记本电脑的自带摄像头，(但是如果开机的时候插着摄像头，系统自检的时候可能会优先给usb相机赋索引号为0)

### 配置相机为60Hz

进入``lerobot/configs/robot/so100.yaml``中修改``camera``信息，如果没有使用到手机则注释掉
```yaml
# phone:
  #   _target_: lerobot.common.robot_devices.cameras.opencv.OpenCVCamera
  #   camera_index: 1
  #   fps: 30
  #   width: 640
  #   height: 480
```

如果使用Box-Arm-V1 Camera 60Hz相机，则需要对应camera_index改为2，需要到 ``lerobot/common/robot_devices/cameras/opencv.py`` 的339行加入，如下代码选择相机的视频格式：上面的代码是：“self.camera = cv2.VideoCapture(camera_idx)”

```python
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G"))
        self.camera.set(cv2.CAP_PROP_FPS, 60)
```

### 本地化训练配置(本仓库已设置)

 1. 修改模型配置文件：[lerobot/configs/policy/act_so100_real.yaml](lerobot/configs/policy/act_so100_real.yaml)中，注释掉所有有关``phone``摄像头的段落，如下：

```yaml
    ...
    24: #  observation.images.phone:
    25: #   # stats from imagenet, since we use a pretrained vision model
    26: #   mean: [[[0.485]], [[0.456]], [[0.406]]]  # (c,1,1)
    27: #   std: [[[0.229]], [[0.224]], [[0.225]]]  # (c,1,1)
    ...
    63: # observation.images.phone: [3, 480, 640]
    ...
    71: # observation.images.phone: mean_std
    ...
```

  2. 修改数据集读取位置：在[lerobot/common/datasets/factory.py](lerobot/common/datasets/factory.py:99)的``video_backend=cfg.video_backend,``后面，加入如下代码：
  
```python
    local_files_only=cfg.local_only.enable,
    root=cfg.local_only.path,
```
  3. 增加hydra参数列表：[lerobot/configs/default.yaml](lerobot/configs/default.yaml:131)，文件末尾加入如下参数结构：

```shell
  local_only:
  enable: true
  path: ???
```

### URDF的STL模型bug相关
如果你遇到报错与“Base_Motor.stl”相关，
请将[lerobot-kinematics/example](https://github.com/box2ai-robotics/lerobot-kinematics/tree/main/examples)中的``assets``和``meshes``文件夹都复制替换到``lerobot/common/robot_devices/controllers``下面。

### 数据集损坏，非正常结束采集程序报错
如果你在训练的时候，遇到如下报错：
“dataset.meta.stats[key][stats_type] = torch.tensor(stats, dtype=torch.float32)
TypeError: 'NoneType' object is not subscriptable”
原因是数据集破损，请在结束录制的时候按ESC键，而不是直接Ctrl+C结束程序


### 手柄常见bug
#### 无法连接/连接成功后无振动
1. 重新运行 `install` 命令验证依赖安装
2. 短按配对按钮关闭
3. 从电脑蓝牙列表中删除设备
4. 重新启动电脑
5. 长按配对按钮并通过蓝牙重新连接

#### Q2: 频繁断开连接，数据不稳定
1. 给控制器充电 30 分钟（自动关机表示电池电量不足）
2. 重新启动控制器和电脑
 - *注意：Ubuntu 存在已知的蓝牙兼容性问题*

#### 它支持 Windows、VM、WSL 或 Mac 吗？ 
目前不支持 - 因为需要内核级驱动程序。 
已测试系统：  
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
*（其他系统可能正常运行，但不支持）*。