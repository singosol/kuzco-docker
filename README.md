# Kuzco根据显存容量多开容器,监控，重启
![image](https://github.com/user-attachments/assets/fdc46626-16ca-423e-82a7-21e5e6969d5e)

### ❌️不适用于MacOS以及AMD显卡，仅支持NVIDIA显卡
### ✅️适用于Linux单GPU多开容器 
### ✅️适用于Linux多GPU多开容器 
### ✅️适用于WSL2单GPU多开容器 
### 理论上支持WSL2多GPU多开容器，但需要正确配置docker和nvidia-container-toolkit，确保Docker容器能单独使用其中一块GPU，本人没有WSL2的多卡机器，所以无法测试

# 安装Docker
`https://www.docker.com/`
# 安装正确的NVIDIA驱动
`https://www.nvidia.com/drivers/lookup/`
# 对于多卡机器，确保安装并正确配置NVIDIA Container Toolkit（单卡机器请忽略）
`https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html`
# 拉取Kuzco镜像
`docker pull kuzcoxyz/worker:latest`
