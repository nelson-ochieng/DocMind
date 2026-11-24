import psutil

def recommendation():
    ram=psutil.virtual_memory().total/1024**3
    return ram, 'qwen3:14b' if ram>=30 else 'qwen3:8b' if ram>=15 else 'llama3.2:3b'
