import logging
import math
import struct
import threading
import time
import os

from joyconrobotics import JoyconRobotics
import numpy as np

from lerobot_kinematics import lerobot_IK, lerobot_FK, get_robot
from joyconrobotics import JoyconRobotics
import mujoco

np.set_printoptions(linewidth=200)
os.environ["MUJOCO_GL"] = "egl"
JOINT_NAMES = ["Rotation", "Pitch", "Elbow", "Wrist_Pitch", "Wrist_Roll", "Jaw"]

class JoyConController:
    def __init__(
        self,
        name,
        initial_position=None,
        timeout = 60,
        *args,
        **kwargs,
    ):
        self.name = name
        self.xml_path = "./lerobot/common/robot_devices/controllers/scene.xml"
        self.mjmodel = mujoco.MjModel.from_xml_path(self.xml_path)
        self.qpos_indices = np.array([self.mjmodel.jnt_qposadr[self.mjmodel.joint(n).id] for n in JOINT_NAMES])
        self.mjdata = mujoco.MjData(self.mjmodel)
        
        self.robot = get_robot('so100')
        self.glimit = [[0.125, -0.4,  0.046, -3.1, -1.5, -1.5], 
                       [0.380,  0.4,  0.23,  3.1,  1.5,  1.5]]
        
        self.init_qpos = np.array([0.0, -3.14, 3.14, 0.0, -1.57, -0.157])
        self.target_qpos = self.init_qpos.copy() 
        self.init_gpos = lerobot_FK(self.init_qpos[1:5], robot=self.robot)
        self.target_gpos = self.init_gpos.copy() 
        
        self.mjdata.qpos[self.qpos_indices] = self.init_qpos   
        mujoco.mj_step(self.mjmodel, self.mjdata) 
        
        self.max_retries = timeout
        self.retries = 0
        self.offset_position_m = self.init_gpos[0:3]
        while self.retries < self.max_retries:
            try:
                self.joyconrobotics = JoyconRobotics(
                    device=name, 
                    horizontal_stick_mode='yaw_diff', 
                    close_y=True, 
                    limit_dof=True, 
                    offset_position_m=self.offset_position_m, 
                    glimit=self.glimit,
                    dof_speed=[1.0, 1.0, 1.0, 1.0, 1.0, 0.5], 
                    common_rad=False,
                    lerobot=True,
                    pitch_down_double=True
                )
                break  # 连接成功，跳出循环
            except Exception as e:
                self.retries += 1
                print(f"Failed to connect to {name} Joycon: {e}")
                print(f"Retrying ({self.retries}/{self.max_retries}) in 1 second...")
                time.sleep(1)  # 连接失败后等待 1 秒重试
        else:
            print("Failed to connect after several attempts.")
        
        self.target_gpos_last = self.init_gpos.copy() 
        self.joint_angles_last = self.init_qpos.copy() 
        
    def get_command(self, present_pose):
        
        target_pose, gripper_state, button_control = self.joyconrobotics.get_control()
        # print("target_pose:", [f"{x:.3f}" for x in target_pose])
        
        for i in range(6):
            if target_pose[i] < self.glimit[0][i]:
                target_pose[i] = self.glimit[0][i]  
            elif target_pose[i] > self.glimit[1][i]:
                target_pose[i] = self.glimit[1][i]  
            else:
                 target_pose[i]
                 
        x = target_pose[0] # init_gpos[0] + 
        z = target_pose[2] # init_gpos[2] + 
        _, _, _, roll, pitch, yaw = target_pose
        y = 0.01
        pitch = -pitch 
        roll = roll - math.pi/2 # lerobo末端旋转90度
        
        # 双臂朝中间偏
        # if self.name == 'left':
        #     yaw = yaw - 0.4
        # elif self.name == 'right':
        #     yaw = yaw + 0.4
        
        target_gpos = np.array([x, y, z, roll, pitch, 0.0])
        fd_qpos_mucojo = self.mjdata.qpos[self.qpos_indices][1:5]
        
        qpos_inv_mujoco, IK_success = lerobot_IK(fd_qpos_mucojo, target_gpos, robot=self.robot)
        if IK_success:
            self.target_qpos = np.concatenate(([yaw,], qpos_inv_mujoco[:4], [gripper_state,])) 

            self.mjdata.qpos[self.qpos_indices] = self.target_qpos
            mujoco.mj_step(self.mjmodel, self.mjdata)
            
            self.target_gpos_last = target_gpos.copy() 
            joint_angles = self.target_qpos
            
            joint_angles = np.rad2deg(self.target_qpos)
            joint_angles[1] = -joint_angles[1]
            joint_angles[0] = -joint_angles[0]
            joint_angles[4] = -joint_angles[4]
            self.joint_angles_last = joint_angles.copy() 

        else:
            self.target_gpos = self.target_gpos_last.copy()
            self.joyconrobotics.set_position(self.target_gpos[0:3])
            joint_angles = self.joint_angles_last
        
        # if button_control != 0:
        #     self.joyconrobotics.reset_joycon()
            
        return joint_angles, button_control