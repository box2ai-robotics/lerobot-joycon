# pip install ftservo-python-sdk
import time
from scservo_sdk import *              

# 加载端口
portHandler = PortHandler('/dev/ttyACM0') 
packetHandler = sms_sts(portHandler)
# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    quit()


# 先将偏置置零
for idx in range(1,7):
  txpacket = [packetHandler.scs_lobyte(0), packetHandler.scs_hibyte(0)]
  packetHandler.unLockEprom(idx)
  packetHandler.writeTxRx(idx, 31, 2, txpacket)
  packetHandler.LockEprom(idx)
  
# 读取当前位置
position = [0,0,0,0,0,0]
offset_encode = [0,0,0,0,0,0]
for idx in range(1,7):
  position[idx-1] = packetHandler.ReadPos(idx)[0]
  time.sleep(0.01)
print(position)

# 计算偏置
for idx in range(1,7):
  offset_encode[idx-1] = position[idx-1] - 2048

# 写当前位置为偏移 "Homing_Offset": (31, 2),
for idx in range(1,7):
  txpacket = [packetHandler.scs_lobyte(offset_encode[idx-1]), packetHandler.scs_hibyte(offset_encode[idx-1])]
  packetHandler.unLockEprom(idx)
  packetHandler.writeTxRx(idx, 31, 2, txpacket)
  packetHandler.LockEprom(idx)

# 测试
while(1):
  for idx in range(1,7):
    position[idx-1] = packetHandler.ReadPos(idx)[0]
  print(position)
  time.sleep(0.1)

# 关闭串口
portHandler.closePort()