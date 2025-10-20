# Container Escape Demonstration

⚠️ **WARNING: This repository contains intentionally vulnerable applications for educational purposes only!**

This project demonstrates various container security vulnerabilities, particularly focusing on Docker container escapes using the `CAP_SYS_MODULE` capability.

## 🎯 Purpose

This demonstration is designed for:
- Security researchers studying container escape techniques
- DevOps engineers learning about container security
- Educational purposes in cybersecurity courses
- Penetration testing training

## 🚨 Security Warning

**NEVER run this in production environments!**

This application contains:
- Remote Code Execution (RCE) vulnerabilities
- Dangerous kernel module loading capabilities
- Container escape techniques
- Privilege escalation vectors

## 📋 What's Included

### Vulnerable Components

1. **Flask Web Application** (`app.py`)
   - Command injection vulnerabilities
   - Unrestricted command execution
   - System information exposure
   - Capability enumeration endpoints

2. **Docker Container** (`Dockerfile`)
   - Runs with `CAP_SYS_MODULE` capability
   - Non-privileged but dangerous configuration
   - Access to host kernel modules

3. **Docker Compose** (`docker-compose.yml`)
   - Adds `CAP_SYS_MODULE` capability
   - Mounts host filesystem components
   - Network configuration for exploitation

4. **Exploit Script** (`exploit.py`)
   - Automated container escape demonstration
   - Kernel module loading techniques
   - Host filesystem access methods

## 🛠 Setup and Installation

### Prerequisites

- Docker Engine (version 20.0+)
- Docker Compose (version 2.0+)
- Linux host system (required for kernel modules)
- Python 3.8+ (for exploit script)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd container-escapes
   ```

2. **Build and start the vulnerable container:**
   ```bash
   docker-compose up --build -d
   ```

3. **Verify the application is running:**
   ```bash
   curl http://localhost:5000/health
   ```

4. **Install exploit dependencies:**
   ```bash
   pip3 install requests
   ```

## 🎮 Usage

### Web Interface

Access the vulnerable application at: http://localhost:5000

The web interface provides:
- **Command Executor**: Direct command injection interface
- **System Information**: Container and host system details
- **Capabilities Check**: Current container capabilities
- **Kernel Modules**: Module listing and manipulation

### API Endpoints

- `GET /` - Main web interface
- `POST /execute` - Command execution (form-based)
- `POST /api/rce` - JSON API for remote code execution
- `GET /sysinfo` - System information
- `GET /capabilities` - Container capabilities
- `GET /modules` - Kernel module information
- `GET /health` - Health check

### Running the Exploit

Execute the automated exploit script:

```bash
python3 exploit.py http://localhost:5000
```

## 🔍 Container Escape Techniques Demonstrated

### 1. CAP_SYS_MODULE Exploitation

The container has the `CAP_SYS_MODULE` capability, which allows:
- Loading arbitrary kernel modules
- Modifying kernel behavior
- Accessing host system resources
- Bypassing container isolation

### 2. Host Filesystem Access

Through various techniques:
- `/proc/1/root` access to host filesystem
- Kernel module backdoors
- Syscall table manipulation

### 3. Privilege Escalation

- Kernel-level code execution
- Host process manipulation
- Root access acquisition

## 🔬 Technical Details

### Dockerfile Configuration

```dockerfile
# Key vulnerability: CAP_SYS_MODULE capability
cap_add:
  - SYS_MODULE

# Required mounts for exploitation
volumes:
  - /lib/modules:/lib/modules:ro
  - /proc:/host/proc:ro
  - /sys:/host/sys:ro
```

### Exploitation Flow

1. **Initial Access**: RCE via web application
2. **Capability Check**: Verify `CAP_SYS_MODULE` is available
3. **Kernel Module Creation**: Build malicious kernel module
4. **Module Loading**: Use `insmod` to load escape module
5. **Host Access**: Execute commands on host system
6. **Persistence**: Maintain access through various methods

## 🛡️ Mitigation Strategies

### Container Security Best Practices

1. **Remove Unnecessary Capabilities**
   ```yaml
   cap_drop:
     - ALL
   cap_add:
     - NET_BIND_SERVICE  # Only add what's needed
   ```

2. **Use Security Profiles**
   ```yaml
   security_opt:
     - apparmor:docker-default
     - seccomp:default
   ```

3. **Read-only Root Filesystem**
   ```yaml
   read_only: true
   tmpfs:
     - /tmp:noexec,nosuid,size=100m
   ```

4. **User Namespaces**
   ```yaml
   user_ns_mode: "host"
   ```

5. **Network Isolation**
   ```yaml
   network_mode: "none"
   # or use custom networks with restrictions
   ```

### Additional Security Measures

- **Runtime Security**: Use tools like Falco, Sysdig
- **Image Scanning**: Scan images for vulnerabilities
- **Least Privilege**: Run containers as non-root users
- **Resource Limits**: Implement CPU, memory, and I/O limits
- **Regular Updates**: Keep base images and dependencies updated

## 🧪 Testing Environment

### Recommended Setup

1. **Isolated VM**: Use a dedicated virtual machine
2. **Network Segmentation**: Isolate from production networks
3. **Monitoring**: Enable detailed logging and monitoring
4. **Snapshots**: Take VM snapshots before testing

### Docker Commands for Testing

```bash
# Check container capabilities
docker exec vulnerable-container capsh --print

# Monitor container behavior
docker logs -f vulnerable-container

# Inspect container configuration
docker inspect vulnerable-container

# Check mounted volumes
docker exec vulnerable-container mount
```

## 📚 Educational Resources

### Learning Objectives

After using this demonstration, you should understand:
- How container capabilities can be exploited
- The importance of least-privilege principles
- Container escape techniques and detection
- Proper container security configuration

### Related Topics

- Linux capabilities system
- Kernel module development
- Container runtime security
- Docker security best practices
- Kubernetes security

## 🐛 Troubleshooting

### Common Issues

1. **Module Loading Fails**
   ```bash
   # Check kernel headers
   docker exec vulnerable-container ls /lib/modules/$(uname -r)/build
   
   # Install build tools
   apt-get update && apt-get install linux-headers-$(uname -r)
   ```

2. **Permission Denied**
   ```bash
   # Check capabilities
   docker exec vulnerable-container capsh --print
   
   # Verify mounts
   docker exec vulnerable-container mount | grep modules
   ```

3. **Network Issues**
   ```bash
   # Check port binding
   docker port vulnerable-container
   
   # Test connectivity
   curl -v http://localhost:5000/health
   ```

## 📖 References and Further Reading

- [Docker Security Documentation](https://docs.docker.com/engine/security/)
- [Linux Capabilities Manual](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Container Escape Techniques](https://book.hacktricks.xyz/linux-unix/privilege-escalation/docker-breakout)
- [NIST Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)

## 📄 License

This project is for educational purposes only. Use at your own risk and only in authorized testing environments.

## 🤝 Contributing

This is an educational project. If you find issues or have improvements:
1. Ensure changes maintain educational value
2. Test in isolated environments only
3. Document security implications
4. Follow responsible disclosure practices

---

**Remember: Use this knowledge responsibly and only in authorized environments!**