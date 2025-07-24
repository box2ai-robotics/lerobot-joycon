# Configuration Guide for 1 Robotic Arm + 1 JoyCon (Single Arm Operation)
<p align="center">
  <a href="Single_tutorial_en.md">English</a> •
  <a href="Single_tutorial.md">中文</a> 
</p>

&nbsp;

## (1) Device ID Binding

We do **not recommend** using the [original port configuration method](./bugs_Q&A.md#L11).
**Reason**: By mapping port IDs using udev rules, we ensure that even if the robotic arms are plugged in different sequences, they will still be correctly identified. This prevents errors in reading calibration files which could lead to incorrect execution and damage to the robotic arm. Follow these steps:

(1) Connect the driver board of the robotic arm to the computer via Type-C USB. Then run the following command:

```shell
udevadm info -a -n /dev/ttyACM* | grep serial
```

```shell
# Output will look like:
#     ATTRS{serial}=="58FA083324"
#     ATTRS{serial}=="0000:00:14.0"
```

(2) Copy the output serial code (`ATTRS{serial}`) to the first line of the file [lerobot/configs/robot/rules/99-lerobot-serial.rules](lerobot/configs/robot/rules/99-lerobot-serial.rules).

(3) Run the following commands to write the rules file to Ubuntu's system directory. The system will then automatically recognize the left and right robotic arms:

```shell
sudo cp lerobot/configs/robot/rules/99-lerobot-serial.rules /etc/udev/rules.d/
sudo chmod +x /etc/udev/rules.d/99-lerobot-serial.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
# If a password is requested, re-run the command. (A brief mouse freeze is normal.)
```

&nbsp;

## (2) Robotic Arm Calibration

(1) Insert the robotic arm and connect its power, then run the following command in the terminal:

```shell
# For single arm calibration
python lerobot/scripts/control_robot.py calibrate \
    --robot-path lerobot/configs/robot/so100_single.yaml \
    --robot-overrides '~cameras'
```

Follow the images below to place the robotic arm in the specified positions. Press `Enter` in the terminal after positioning the arm to proceed to the next pose.

| 1. Follower Zero Position | 2. Follower Rotated Position | 3. Follower Rest Position |
|---|---|---|
| ![](./media/so100/follower_zero.webp?raw=true) | ![](./media/so100/follower_rotated.webp?raw=true) | ![](./media/so100/follower_rest.webp?raw=true) |

**Note:** For the ``2. Rotated Position``, carefully observe the orientation. Do not rotate joints too quickly to avoid damaging the motors.

- For "failed due to communication error" issues, refer to [bugs_Q&A.md#L27](bugs_Q&A.md#L27)

If the main arm's gears have not been removed, you can still use it as a follower controlled by the JoyCon. Refer to the double-arm setup guide [Double_tutorial.md](Double_tutorial.md), and [main arm calibration image](bugs_Q&A.md#L32).

&nbsp;

## (3) JoyCon Library Installation

### 0. Dependencies

The JoyCon remote operation depends on Joycon-Robotics for drivers and control strategies, and Lerobot-Kinematics for forward/inverse kinematics.

- [joycon-robotics](https://github.com/box2ai-robotics/joycon-robotics)
- [lerobot-kinematics](https://github.com/box2ai-robotics/lerobot-kinematics)

Install with the following commands:

```shell
# joycon-robotics
conda activate lerobot
git clone https://github.com/box2ai-robotics/joycon-robotics.git
cd joycon-robotics

pip install -e .
sudo apt-get update
sudo apt-get install -y dkms libevdev-dev libudev-dev cmake
make install
# Test JoyCon with joyconrobotics_tutorial.ipynb before proceeding

# lerobot-kinematics
conda activate lerobot
git clone https://github.com/box2ai-robotics/lerobot-kinematics.git
cd lerobot-kinematics
pip install -e .
```

- For network issues, refer to [bugs_Q&A.md#L1](bugs_Q&A.md#L1)

If you only want to play with kinematic control, copy [lerobot/.cache/calibration/so100/main_follower.json](lerobot/.cache/calibration/so100/main_follower.json) to the ``lerobot-kinematics/examples`` folder and follow its README.

### 1. Bluetooth Connection

(1) First connection: ``Hold the small round side button on the controller for 3 seconds to enter pairing mode``. The JoyCon will appear as "Joy-Con(R)" in your PC's Bluetooth search. Click to pair.

(2) Once connected, the controller will start vibrating at regular intervals. For single controller mode, hold both trigger buttons for 3 seconds. For dual controllers, wait until both are vibrating and then press the top triggers (`L` on left JoyCon and `R` on right JoyCon).

![](media/bocon/bocon_pair.png)
![](media/bocon/bocon_connection.png)

(3) For subsequent connections to the same computer, simply press the top trigger button to auto-connect within 5 seconds.

### 2. JoyCon Teleoperation

#### (1) Single Arm with JoyCon (no camera view):

```shell
# Rename calibration file for JoyCon
cp .cache/calibration/so100/main_follower.json .cache/calibration/so100/right_follower.json

python lerobot/scripts/control_robot.py teleoperate \
    --robot-path lerobot/configs/robot/so100_joycon_single.yaml \
    --robot-overrides '~cameras'
```
- For "No integer found" error, refer to [bugs_Q&A.md#L38](bugs_Q&A.md#L38)

#### (2) Usage Guide

##### Coordinate System
- Forward: `X+`
- Right: `Y+`
- Up: `Z+`

##### Joystick (First-Person View)
- Up: Move forward
- Down: Move backward
- Left: Move left
- Right: Move right

##### Button Functions
1. **Reset**:
   - Right JoyCon `Home` or Left JoyCon `Screenshot` button: reset to initial position
   ![](media/bocon/bocon_home.png)

2. **Gripper Control**:
   - Right `ZR` or Left `ZL`: toggle gripper open/close

3. **Height Control**:
   - Press joystick down: lower Z-axis
   - Press `L`/`R`: raise Z-axis

4. **Forward/Backward Movement**:
   - Left up or Right `X`: move forward (X+)
   - Left down or Right `B`: move backward (X-)

5. **Recording Control**:
   - Right `A`: save current data and begin next
   - Right `Y`: re-record current episode if error

&nbsp;

## (4) JoyCon Dataset Collection

### 1. Teleoperation with Camera View

```shell
python lerobot/scripts/control_robot.py teleoperate \
    --robot-path lerobot/configs/robot/so100_joycon_single.yaml
```

- For JoyCon connection bugs: [bugs_Q&A.md#L140](bugs_Q&A.md#L140)
- GLX/OpenGL errors: [bugs_Q&A.md#L43](bugs_Q&A.md#L43)
- STL file issues: [bugs_Q&A.md#L129](bugs_Q&A.md#L129)
- Program freeze: [bugs_Q&A.md#L53](bugs_Q&A.md#L53)
- Camera not found: [bugs_Q&A.md#L66](bugs_Q&A.md#L66)

### 2. Record Dataset

```shell
python lerobot/scripts/control_robot.py record \
    --robot-path lerobot/configs/robot/so100_joycon_single.yaml \
    --fps 30 \
    --tags so100 tutorial \
    --warmup-time-s 5 \
    --episode-time-s 40 \
    --reset-time-s 5 \
    --num-episodes 20 \
    --push-to-hub 0 \
    --local-files-only 1 \
    --root datasets/pick_put \
    --repo-id task/pick \
    --single-task pick_put \
    --resume 1
```

(1) Important Parameters:

  - ``robot-path``: robot config file
  - ``root``: save path
  - ``reset-time-s``: reset wait time
  - ``num-episodes``: how many episodes
  - ``fps``: camera frame rate

(2) Instructions:

  - Recording starts with warmup frame
  - Right `A`: save current, start next
  - Right `Y`: re-record after 10s
  - ``ESC key``: end recording. Ctrl+C might result in missing stats.

### 3. Visualize Dataset

```shell
python lerobot/scripts/visualize_dataset.py \
    --root datasets/pick_put \
    --local-files-only 1 \
    --mode 0 \
    --repo-id task/pick_put \
    --episode-index 0 \
    --save 1 \
    --output-dir datasets/pick_put/visualize

rerun datasets/pick_put/visualize/task_pick_put_episode_0.rrd
```

![](media/rerun.png)

### 4. Replay Dataset

```shell
DATA_DIR=data python lerobot/scripts/control_robot.py replay \
    --robot-path lerobot/configs/robot/so100_joycon_single.yaml \
    --fps 30 \
    --root datasets/pick_put \
    --repo-id task/pick_put \
    --episode 0 \
    --local-files-only 1
```

... *(remaining sections to follow in the next update)*


## (5) Local Training and Inference

Hugging Face recommends using their cloud hosting, but for local training, additional configuration is needed. This repository has already prepared such settings ([see here](bugs_Q&A.md#L98)).

### 1. Model Training

The key policy config is in: [act_so100_real.yaml:30](lerobot/configs/policy/act_so100_real.yaml:30), where you can set training steps (`offline_steps`) and save frequency (`save_freq`).

```shell
python lerobot/scripts/train.py \
  policy=act_so100_real_single \
  env=so100_real_single \
  device=cuda \
  wandb.enable=false \
  local_only.enable=true \
  dataset_repo_id=task/pick_put \
  hydra.run.dir=outputs/train/act_pick_put \
  hydra.job.name=act_pick_put \
  local_only.path=datasets/pick_put
```

- For training errors, refer to [bugs_Q&A.md#L133](bugs_Q&A.md#L133)

### 2. Model Inference

It is recommended to use the `record` function with the `tags` set to `eval`. This also saves the inference process into datasets prefixed with `eval_`.

```shell
python lerobot/scripts/control_robot.py record \
  --robot-path lerobot/configs/robot/so100_joycon_single.yaml \
  --fps 30 \
  --tags so100 tutorial eval \
  --warmup-time-s 5 \
  --episode-time-s 40 \
  --reset-time-s 5 \
  --num-episodes 10 \
  --push-to-hub 0 \
  --local-files-only 1 \
  --root datasets/eval_pick_put \
  --repo-id task/eval_pick_put \
  --single-task eval_pick_put \
  -p outputs/train/act_pick_put/checkpoints/last/pretrained_model
```

## (6) Advanced Tips

If you completed:
```
① Arm setup => ② Dataset recording => ③ Model training => ④ Model inference => ⑤ Arm moves as expected
```
Then congratulations, you're up and running! Take a break, and reflect on how far you've come—from dual-booting Ubuntu, installing NVIDIA drivers, PyTorch setup, etc. You’re now contributing to one of the most exciting fields in AI: Embodied Intelligence.

### 1. Minimal Workflow for Future Use

```shell
# 1. Data Recording
python lerobot/scripts/control_robot.py record \
    --robot-path lerobot/configs/robot/so100.yaml \
    --fps 30 \
    --tags so100 tutorial \
    --warmup-time-s 5 \
    --episode-time-s <max seconds> \
    --reset-time-s <wait time in seconds> \
    --num-episodes <number of episodes> \
    --push-to-hub 0 \
    --local-files-only 1 \
    --root datasets/<your_task_name> \
    --repo-id task/<your_task_name> \
    --single-task <your_task_name> \
    --resume 1

# 2. Model Training
python lerobot/scripts/train.py \
  policy=act_so100_real \
  env=so100_real \
  device=cuda \
  wandb.enable=false \
  local_only.enable=true \
  dataset_repo_id=task/<your_task_name> \
  hydra.run.dir=outputs/train/<your_task_name> \
  hydra.job.name=<your_task_name> \
  local_only.path=datasets/<your_task_name>

# 3. Model Inference
python lerobot/scripts/control_robot.py record \
  --robot-path lerobot/configs/robot/so100.yaml \
  --fps 30 \
  --tags so100 tutorial eval \
  --warmup-time-s 5 \
  --episode-time-s 40 \
  --reset-time-s 5 \
  --num-episodes 10 \
  --local-files-only 1 \
  --repo-id task/eval_<your_task_name> \
  --single-task eval_<your_task_name> \
  -p outputs/train/act_<your_task_name>/checkpoints/last/pretrained_model
```

### 2. Optimization Tips

If the model doesn't perform as expected:

- **Tune Key Params**
  - `offline_steps`: Train longer for better results
  - `vision_backbone`: Use stronger image encoders like `resnet34`
  - **Dataset quality matters the most**

- **Dataset Guidelines**
  - Keep objects visible to at least one camera throughout
  - More complex tasks need larger datasets
  - Uniform data distribution is essential for generalization

### 3. Advanced Model - Diffusion Transformer

Diffusion Policy is more generalizable than ACT but harder to train. Minimum 50 samples recommended.

Suggested params to adjust in [diffusion.yaml](lerobot/configs/policy/diffusion.yaml):

- `n_action_steps`: Increase to 100 for better inference planning
- `observation.imag`: Set to `[3, 480, 640]` for better view
- `crop_shape`: `[440, 560]` for faster convergence

Example training command with transformer:

```shell
python lerobot/scripts/train.py \
  policy=diffusion_aloha \
  policy.use_transformer=true \
  env=aloha \
  env.task=AlohaTransferCube-v0 \
  device=cuda \
  wandb.enable=false \
  local_only.enable=false \
  hydra.run.dir=outputs/train/diffusion_transformer_sim_transfer \
  hydra.job.name=<your_task_name> \
  local_only.path=None
```

## (7) Custom Task Collection with JoyCon

```shell
# 1. Data Recording
python lerobot/scripts/control_robot.py record \
    --robot-path lerobot/configs/robot/so100_joycon.yaml \
    --fps 30 \
    --tags so100 tutorial \
    --warmup-time-s 5 \
    --episode-time-s 40 \
    --reset-time-s 5 \
    --num-episodes <episodes> \
    --push-to-hub 0 \
    --local-files-only 1 \
    --root datasets/<your_task> \
    --repo-id task/<your_task> \
    --single-task <your_task> \
    --resume 1

# 2. Model Training
python lerobot/scripts/train.py \
  policy=act_so100_real_double \
  env=so100_real \
  device=cuda \
  wandb.enable=false \
  local_only.enable=true \
  dataset_repo_id=task/<your_task> \
  hydra.run.dir=outputs/train/<your_task> \
  hydra.job.name=<your_task> \
  local_only.path=datasets/<your_task>

# 3. Model Inference
python lerobot/scripts/control_robot.py record \
  --robot-path lerobot/configs/robot/so100_joycon.yaml \
  --fps 30 \
  --tags so100 tutorial eval \
  --warmup-time-s 5 \
  --episode-time-s <max seconds> \
  --reset-time-s <wait time in seconds> \
  --num-episodes <episodes> \
  --repo-id task/eval_<your_task> \
  --single-task eval_<your_task> \
  -p outputs/train/act_<your_task>/checkpoints/last/pretrained_model
```

## (8) More
1. Follow our [Bilibili channel](https://space.bilibili.com/122291348) for more demos and videos
2. Join our QQ group for discussions: 948755626
3. [Visit our Taobao store](https://item.taobao.com/item.htm?abbucket=16&detail_redpacket_pop=true&id=906794552661&ltk2=17440907659690jpsj3h7uiismft7vle37&ns=1&skuId=5933796995638) to purchase our fine-tuned robotic arm + JoyCon kits

If this helped you, please give us a star! ⭐ ⭐ ⭐ ⭐ ⭐

