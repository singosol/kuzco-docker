# Kuzco根据显存容量多开实例/容器，监控，重启脚本

## 每个实例需要大概6G显存，因此不能多开超过显存容量(12G显存两个实例，24G显存4个实例)
### ❌️不适用于Mac
### ✅️适用于Linux单GPU多开容器 
### ✅️适用于Linux多GPU多开容器 
### ✅️适用于WSL2单GPU多开容器 
#### ❔理论上支持WSL2多GPU多开容器，但需要正确配置docker和nvidia-container-toolkit，确保Docker容器能单独使用其中一块GPU，本人没有WSL2的多卡机器，所以无法测试
### ⚠️在某些算力租赁平台租的GPU实例本身是docker就无法再使用docker

--------------------------------------------------------------------------------------------


## 1.安装NVIDIA/AMD驱动
NVIDIA:
`https://www.nvidia.com/drivers/lookup/`

验证驱动是否安装成功:
```
nvidia-smi
```

AMD:
`https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html`

验证驱动是否安装成功:

```
amd-smi
```
## 2.安装Docker
```
sudo apt-get update
sudo apt-get install docker.io
```
## 3.安装并配置NVIDIA Container Toolkit(ADM显卡忽略此步骤)
```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```
```
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## 4.拉取Kuzco镜像
```
docker pull kuzcoxyz/worker:latest
```
## 5.在Kuzco官网创建一个Docker类型的Worker（必须是Docker类型的Worker，如果你使用CLI类型Worker的启动代码将不起作用）
## 6.复制启动代码（如下图蓝色选中部分）
![image](https://github.com/user-attachments/assets/adbb25d5-31d9-4117-914b-7388006fda58)
## 7.[下载脚本](https://github.com/singosol/kuzco-docker/releases)
```
curl -LO https://github.com/singosol/kuzco-docker/releases/download/v0.13/kzco.py
```
## 8.使用nano打开并编辑脚本（也可使用vi、vim等编辑器）
```
nano kzco.py
```
## 9.找到以下代码（第15行），粘贴刚刚（第6步）在官网复制的启动代码到""内
`startup_code = ""  ##粘贴启动代码`

CTRL+O保存，CTRL+X退出
## 10.执行以下命令运行脚本
```
python3 kzco.py
```
------------------------------------------------------------------------------------------
#### 📄查看实例/容器日志（把 <容器id或名称> 替换成你的容器id或名称）
列出所有正在运行的容器
```
docker ps
```
查看容器所有日志
```
docker logs <容器id或名称>
```
实时查看容器日志
```
docker logs -f <容器id或名称>
```
