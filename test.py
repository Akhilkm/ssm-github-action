import subprocess
p = subprocess.Popen("echo hello; sleep 10; echo hello", shell=True)
print(p.pid)
