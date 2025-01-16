import logging
import math
import struct
import threading
import time
import os

from joyconrobotics import JoyconRobotics

# 1. 获取到手柄姿态，x,y,z,r,p,y
# 2. 逆解成关节角度

# from lerobot_kinematics import lerobot_IK, lerobot_FK


# from glm import vec3
# import hid
# from joycon_robot import ConnectJoycon
# from joycon_lerobot import FK, IK
import numpy as np

from lerobot_kinematics import lerobot_IK, lerobot_FK, get_robot2, feetech_arm
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
        *args,
        **kwargs,
    ):
        self.xml_path = "./lerobot/common/robot_devices/controllers/scene.xml"
        self.mjmodel = mujoco.MjModel.from_xml_path(self.xml_path)
        self.qpos_indices = np.array([self.mjmodel.jnt_qposadr[self.mjmodel.joint(n).id] for n in JOINT_NAMES])
        self.mjdata = mujoco.MjData(self.mjmodel)
        
        
        
        self.robot = get_robot2()
        self.glimit = [[0.120, -0.4,  0.046, -3.1, -1.5, -1.5], 
          [0.380,  0.4,  0.23,  3.1,  1.5,  1.5]]
        
        self.init_qpos = np.array([0.0, -3.14, 3.14, 0.0, -1.57, -0.157])
        self.target_qpos = self.init_qpos.copy() 
        self.init_gpos = lerobot_FK(self.init_qpos[1:5], robot=self.robot)
        self.target_gpos = self.init_gpos.copy() 
        
        self.mjdata.qpos[self.qpos_indices] = self.init_qpos   
        mujoco.mj_step(self.mjmodel, self.mjdata) 

        self.joyconrobotics = JoyconRobotics(device=name, 
                                      horizontal_stick_mode='yaw_diff', 
                                      close_y=True, 
                                      limit_dof=True, 
                                      init_gpos=self.init_gpos, 
                                    #   dof_speed=[0.5, 0.5, 0.5, 0.5, 0.5, 0.1], 
                                    dof_speed=[1.0, 1.0, 1.0, 1.0, 1.0, 0.5], 
                                      common_rad=False,
                                      lerobot = True)
                            
        self.target_gpos_last = self.init_gpos.copy()      
        
        
    
    def get_command(self, present_pose):
        
        target_pose, gripper_state_r = self.joyconrobotics.update()
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
        
        right_target_gpos = np.array([x, y, z, roll, pitch, 0.0])
        fd_qpos_mucojo = self.mjdata.qpos[self.qpos_indices][1:5]
        
        qpos_inv_mujoco, IK_success = lerobot_IK(fd_qpos_mucojo, right_target_gpos, robot=self.robot)
        
        if IK_success:
            self.target_qpos = np.concatenate(([yaw,], qpos_inv_mujoco[:4], [gripper_state_r,])) 

            self.mjdata.qpos[self.qpos_indices] = self.target_qpos
            mujoco.mj_step(self.mjmodel, self.mjdata)
            self.target_gpos_last = right_target_gpos.copy() 
            
            joint_angles = np.rad2deg(self.target_qpos)
            joint_angles[1] = -joint_angles[1]
            joint_angles[0] = -joint_angles[0]
            joint_angles[4] = -joint_angles[4]
            
            return joint_angles

        else:
            self.target_gpos = self.target_gpos_last.copy()
            self.joyconrobotics.set_position = self.target_gpos[0:3]
            
            return self.target_qpos
        
    
        
        
        
        
        
       
        # self.initial_position = np.array(initial_position) if initial_position else np.array([0.0, -3.14, 3.14, 0.0, 1.57, -0.157])
        #                           
        # self.target_qpos = self.initial_position.copy()
        # self.initial_gpos = FK(self.initial_position[1:5])
        
        # self.zero_pos = self.initial_gpos[:3]
        # self.zero_euler = self.initial_gpos[3:]
        
        # self.joycon_gyro, self.joycon_button, self.joycon, self.attitude_estimator = ConnectJoycon(names)
        # self.target_qpos_last = None
    
    
        
        
        # present_pose[1] = -present_pose[1]
        # present_pose[0] = -present_pose[0]
        # present_pose = np.deg2rad(present_pose)
        # target_pose, gripper_status = self.joyconrobotics.update()
        # x, y, z, roll, pitch, yaw = target_pose
        
        # qpos_inv = lerobot_IK(present_pose, target_pose)
        
        
        # attitude_estimator_value = self.attitude_estimator.update(self.joycon_gyro.gyro_in_rad[0],  self.joycon_gyro.accel_in_g[0])
        # roll_r, pitch_r, yaw_r = attitude_estimator_value[0], attitude_estimator_value[1], attitude_estimator_value[2]
        # pitch_r = -pitch_r # 手柄
        # yaw_r = -yaw_r * math.pi/2 #* 10
        # yaw_r -= yaw_diff
        # roll_r = roll_r + math.pi/2 # lerobo末端旋转90度
        
        # if pitch_r > 0:
        #     pitch_r = pitch_r * 3.0
        
        # yaw_rad_T = math.pi/2
        # pitch_rad_T = math.pi/2
        # pitch_r = pitch_rad_T if pitch_r > pitch_rad_T else (-pitch_rad_T/2 if pitch_r < -pitch_rad_T/2 else pitch_r) 
        # yaw_r = yaw_rad_T if yaw_r > yaw_rad_T else (-yaw_rad_T if yaw_r < -yaw_rad_T else yaw_r) 
        
        # direction_vector_r = vec3(math.cos(pitch_r) * math.cos(yaw_r), math.cos(pitch_r) * math.sin(yaw_r), math.sin(pitch_r))

        # ########### 复位/夹爪按键 #############
        # if self.joycon.get_button_home() == 1:
        #     self.joycon_gyro.reset_orientation
        #     self.attitude_estimator.reset_yaw()
        #     yaw_reset = self.target_qpos[0]
        #     yaw_diff = 0
        #     while 1:
        #         ################right
        #         x = x - 0.001 if x > self.zero_pos[0]+0.001 else (self.target_qpos + 0.001 if x < self.zero_pos[0]-0.001 else x) 
        #         y = y - 0.001 if y > self.zero_pos[1]+0.001 else (y + 0.001 if y < self.zero_pos[1]-0.001 else y)
        #         z = z - 0.001 if z > self.zero_pos[2]+0.001 else (z + 0.001 if z < self.zero_pos[2]-0.001 else z)
        #         yaw_reset = yaw_reset - 0.001 if yaw_reset > 0.001 else (yaw_reset + 0.001 if yaw_reset < 0-0.001 else yaw_reset)
                
        #         target_gpos = np.array([x, y, z, roll_r, pitch_r, 0.0])
        #         # qpos_inv = rtb_kinematics.rtb_inverse_kinematics(mjdata.qpos[qpos_indices][1:5], self.target_gpos)
        #         # qpos_inv = rtb_kinematics.rtb_inverse_kinematics(self.target_qpos[1:5], target_gpos)
        #         qpos_inv = IK(self.target_qpos[1:5], target_gpos)
        #         self.target_qpos = np.concatenate(([yaw_reset,], qpos_inv, [gripper_state,]))
                
        #         if abs(x-self.zero_pos[0]) < 0.05 and abs(y-self.zero_pos[1]) < 0.05 and abs(z-self.zero_pos[2]) <0.05:
        #             break
                
        # # 这里需要添加左joycon的监听事件
        # for event_type, status in self.joycon_button.events():
        #     if event_type == 'plus' and status == 1:
        #         self.joycon_gyro.calibrate()
        #         self.joycon_gyro.reset_orientation
        #         self.attitude_estimator.reset_yaw()
        #         time.sleep(2)
        #         self.joycon_gyro.calibrate()
        #         self.joycon_gyro.reset_orientation
        #         self.attitude_estimator.reset_yaw()
        #         time.sleep(2)
        #     elif event_type == 'r':
        #         if status == 1:
        #             if gripper_state == 1:
        #                 gripper_state = -0.1
        #             else:
        #                 gripper_state = 1
                    
        #     print(f'{event_type}')
            
        
        # ########### 位移 #############
        # joycon_stick_v = self.joycon.get_stick_right_vertical()
        # if joycon_stick_v > 4000: # 向前移动：朝着方向矢量的方向前进 0.1 的速度
        #     x += 0.001 * direction_vector_r[0]
        #     z -= 0.001 * direction_vector_r[2]
        # elif joycon_stick_v < 1000: # 向后移动：朝着方向矢量的反方向移动 0.1 的速度
        #     x -= 0.001 * direction_vector_r[0]
        #     z += 0.001 * direction_vector_r[2]

        # joycon_stick_h = self.joycon.get_stick_right_horizontal()
        # if joycon_stick_h > 4000 and yaw_diff < math.pi/2: 
        #     yaw_diff +=0.002
        # elif joycon_stick_h < 1000 and yaw_diff > -math.pi/2: 
        #     yaw_diff -=0.002
        
        # # 自定义按键 
        # ########### 输出Joycon位姿 #############
        # self.target_gpos = np.array([x, y, z, roll_r, pitch_r, 0.0])

        # # qpos_inv = rtb_kinematics.rtb_inverse_kinematics(self.target_qpos[1:5], self.target_gpos)
        # qpos_inv = IK(self.target_qpos[1:5], self.target_gpos)
        # if qpos_inv[0] != -1.0 and qpos_inv[1] != -1.0 and qpos_inv[2] != -1.0 and qpos_inv[3] != -1.0:
        #     self.target_qpos = np.concatenate(([yaw_r,], qpos_inv, [gripper_state,])) # 使用陀螺仪控制yaw
            
        #     joint_angles = np.rad2deg(self.target_qpos)
        #     joint_angles[1] = -joint_angles[1]
        #     joint_angles[0] = -joint_angles[0]
        #     # joint_angles[5] = joint_angles[5]
        #     self.target_qpos = joint_angles
        #     #仅需返回关节角度
        #     # follower_arm.write("Goal_Position", joint_angles)
            
        #     # position = follower_arm.read("Present_Position")
            
        #     self.target_gpos_last = self.target_gpos.copy() # 保存备份
        # else:
        #     self.target_gpos = self.target_gpos_last.copy()
        
        # # time.sleep(0.001)
        # return self.target_qpos