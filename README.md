# Kuzco根据显存容量多开容器，监控，重启
![image](https://github.com/user-attachments/assets/fdc46626-16ca-423e-82a7-21e5e6969d5e)

--------------------------------------------------------------------------------------------

### ❌️不适用于MacOS以及AMD显卡，仅支持NVIDIA显卡
### ✅️适用于Linux单GPU多开容器 
### ✅️适用于Linux多GPU多开容器 
### ✅️适用于WSL2单GPU多开容器 
#### ❔理论上支持WSL2多GPU多开容器，但需要正确配置docker和nvidia-container-toolkit，确保Docker容器能单独使用其中一块GPU，本人没有WSL2的多卡机器，所以无法测试
### ⚠️在租赁平台租的GPU实例本身是docker就无法再使用docker，使用命令 ps -p 1 如果输出systemd就可以使用，如果是其他（如bash）则无法再使用

--------------------------------------------------------------------------------------------
## 1.安装Docker
`https://www.docker.com/`
## 2.安装正确的NVIDIA驱动
`https://www.nvidia.com/drivers/lookup/`
## 3.确保安装并正确配置NVIDIA Container Toolkit
`https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html`


## 4.拉取Kuzco镜像
```
docker pull kuzcoxyz/worker:latest
```

## 5.[下载脚本](https://github.com/singosol/kuzco-docker/releases)
## 6.在Kuzco创建一个Docker类型的worker（必须是Docker类型的worker，如果你使用CLI类型worker的启动代码将不起作用）
## 7.复制启动代码（如图蓝色选中部分）
![image](https://github.com/user-attachments/assets/adbb25d5-31d9-4117-914b-7388006fda58)

## 8.打开并编辑脚本，粘贴刚刚复制的启动代码到""内，保存
`startup_code = ""  ##粘贴启动代码`
## 9.在终端执行以下命令创建脚本
```
nano kzco.py
```
### 复制并粘贴刚刚编辑好的脚本，保存退出
## 10.在终端执行以下命令运行脚本
```
python3 kzco.py
```
