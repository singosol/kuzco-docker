
### 此脚本不适用于MacOS以及AMD显卡，仅支持NVIDIA显卡 ###
## 支持Linux单GPU多开容器 ## 支持Linux多GPU多开容器 ## 支持WSL2单GPU多开容器 ## 理论上支持WSL2多GPU多开容器，但需要正确配置docker和nvidia-container-toolkit ##

import subprocess
import time
from datetime import datetime, timedelta
import os

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

startup_code = ""  ##粘贴启动代码
check_interval = 300  ## 检测时间间隔, 单位: 秒
model_vram_mib = 5920  ## 运行一个模型需要的显存, 单位: MiB
log_positions = {}
container_info = {}
log_dir = "kuzco_daily_log"
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, datetime.now().strftime("inference_log_%Y-%m-%d.log"))
current_day = datetime.now().date()

def run_command(command):
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {RED}💀 错误执行命令: {command}{RESET}\n错误信息: {e.stderr.strip()}")
        return None

def start_container(gpu_id):
    base_command = ['docker', 'run', '--rm', '--gpus', f'device={gpu_id}', '-d', 'kuzcoxyz/worker:latest'] + startup_code.split()
    output = run_command(base_command)
    if output:
        container_id = output.strip()
        container_info[container_id] = gpu_id
        log_positions[container_id] = 0
        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} 🛠️ 启动容器, 容器ID: {GREEN}{container_id[:12]}{RESET} GPU: {YELLOW}{gpu_id}{RESET}")
        return container_id
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {RED}❌ 容器启动失败, 在GPU {gpu_id} 上重试...{RESET}")
        time.sleep(5)
        return start_container(gpu_id)

def start_containers(gpu_id, vram_mib):
    num_containers = vram_mib // model_vram_mib
    print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} 📟️ [GPU:{YELLOW}{gpu_id}{RESET} 显存:{YELLOW}{vram_mib}{RESET}MiB] 最大启动数量: {YELLOW}{num_containers}{RESET}")
    time.sleep(2)
    for _ in range(num_containers):
        start_container(gpu_id)
        time.sleep(5)

def monitor_containers():
    finished_count = 0
    containers_to_remove = []
    for cid in list(container_info.keys()):
        inspect_command = ['docker', 'inspect', '--format', '{{.State.Status}}', cid]
        status = run_command(inspect_command)
        if status != 'running' or status is None:
            print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {YELLOW}⚠️ 容器 {cid[:12]} 不存在或已停止, 将启动一个新的容器{RESET}")
            gpu_id = container_info[cid]
            stop_and_clean_container(cid)
            start_container(gpu_id)
            continue

        logs_command = ['docker', 'logs', cid]
        full_logs = run_command(logs_command)
        if full_logs is None:
            print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {RED}⚠️ 无法获取容器 {cid[:12]} 的日志, 将跳过{RESET}")
            continue

        previous_position = log_positions.get(cid, 0)
        new_logs = full_logs[previous_position:]
        log_positions[cid] = len(full_logs)
        finished_occurrences = new_logs.count('finished')
        finished_count += finished_occurrences

        if finished_occurrences == 0:
            print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} ⚠️ 容器 {YELLOW}{cid[:12]}{RESET} 在本周期内未完成任何推理, 将重启新的容器")
            gpu_id = container_info[cid]
            stop_and_clean_container(cid)
            start_container(gpu_id)

    for cid in containers_to_remove:
        if cid in container_info:
            del container_info[cid]
        if cid in log_positions:
            del log_positions[cid]

    return finished_count

def load_daily_total():
    if os.path.exists(log_filename):
        with open(log_filename, 'r') as log_file:
            lines = log_file.readlines()
            if lines:
                last_line = lines[-1].strip()
                if '-' in last_line:
                    try:
                        date_str, total_str = last_line.rsplit('-', 1)
                        return int(total_str.strip())
                    except ValueError:
                        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {RED}⚠️ 无法解析日志文件中的最后一行: {last_line}{RESET}")
                        return 0
    return 0

def log_inference_count(finished_count, daily_total):
    daily_total += finished_count
    with open(log_filename, 'w') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d')} - {daily_total}\n")
    print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} 💻 {check_interval // 60}分钟推理量: {GREEN}{finished_count}{RESET} | 📊 今日推理总量: {GREEN}{daily_total}{RESET}")
    return daily_total

def stop_and_clean_container(cid):
    print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} 🪦 停止容器 {YELLOW}{cid[:12]}{RESET}...")
    run_command(['docker', 'stop', '-t', '10', cid])
    if cid in container_info:
        del container_info[cid]
    if cid in log_positions:
        del log_positions[cid]

def stop_all_containers():
    for cid in list(container_info.keys()):
        stop_and_clean_container(cid)

def main():
    global current_day
    gpu_info_output = run_command(["nvidia-smi", "--query-gpu=index,memory.total", "--format=csv,noheader,nounits"])
    if not gpu_info_output:
        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {RED}❌ 无法获取GPU信息, 请确保已安装NVIDIA驱动并配置nvidia-smi命令{RESET}")
        return

    for line in gpu_info_output.strip().split('\n'):
        gpu_id, total_mem = line.strip().split(',')
        gpu_id = gpu_id.strip()
        total_mem_mib = int(total_mem.strip())
        if total_mem_mib >= model_vram_mib:
            start_containers(gpu_id, total_mem_mib)
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {YELLOW}⚠️ GPU {gpu_id} 的显存不足, 跳过启动容器{RESET}")

    daily_total = load_daily_total()

    try:
        while True:
            time.sleep(check_interval)
            if datetime.now().date() != current_day:
                current_day = datetime.now().date()
                daily_total = 0
                global log_filename
                log_filename = os.path.join(log_dir, datetime.now().strftime("inference_log_%Y-%m-%d.log"))
                print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} 🌅 新的一天开始, 重置每日推理总量")

            finished_count = monitor_containers()
            daily_total = log_inference_count(finished_count, daily_total)
    except KeyboardInterrupt:
        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {YELLOW}⚠️ 接收到中断信号, 正在停止所有容器...{RESET}")
        stop_all_containers()
        print(f"{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')} {GREEN}✅ 所有容器已停止, 程序退出{RESET}")


if __name__ == "__main__":
    main()
