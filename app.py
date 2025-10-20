#!/usr/bin/env python3
"""
Vulnerable Flask application for container security demonstration.
WARNING: This application contains intentional security vulnerabilities.
Use only in isolated testing environments for educational purposes.
"""

from flask import Flask, request, render_template_string, jsonify
import subprocess
import os
import sys

app = Flask(__name__)

# Vulnerable template for command injection
VULNERABLE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Container App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .warning { background: #ffeb3b; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { width: 300px; padding: 8px; }
        button { padding: 10px 20px; background: #2196f3; color: white; border: none; border-radius: 3px; }
        .output { background: #f5f5f5; padding: 15px; border-radius: 3px; white-space: pre-wrap; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <div class="warning">
            <strong>⚠️ WARNING:</strong> This is a vulnerable application for educational purposes only!
        </div>

        <h1>Container Security Demo</h1>
        <p>This application demonstrates various container security vulnerabilities.</p>

        <h2>Command Executor</h2>
        <form action="/execute" method="post">
            <div class="form-group">
                <label>Command to execute:</label><br>
                <input type="text" name="command" placeholder="ls -la" value="{{ command }}">
                <button type="submit">Execute</button>
            </div>
        </form>

        {% if output %}
        <h3>Output:</h3>
        <div class="output">{{ output }}</div>
        {% endif %}

        <h2>System Information</h2>
        <form action="/sysinfo" method="get">
            <button type="submit">Get System Info</button>
        </form>

        <h2>Container Capabilities</h2>
        <form action="/capabilities" method="get">
            <button type="submit">Check Capabilities</button>
        </form>

        <h2>Kernel Modules</h2>
        <form action="/modules" method="get">
            <button type="submit">List Kernel Modules</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(VULNERABLE_TEMPLATE)

@app.route('/execute', methods=['POST'])
def execute_command():
    """
    VULNERABILITY: Command Injection
    This endpoint allows arbitrary command execution
    """
    command = request.form.get('command', '')
    output = ""

    if command:
        try:
            # VULNERABLE: Direct command execution without sanitization
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = f"Return code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            output = "Command timed out after 10 seconds"
        except Exception as e:
            output = f"Error executing command: {str(e)}"

    return render_template_string(VULNERABLE_TEMPLATE, command=command, output=output)

@app.route('/sysinfo')
def system_info():
    """Get basic system information"""
    try:
        commands = [
            ("Hostname", "hostname"),
            ("User", "whoami"),
            ("UID/GID", "id"),
            ("Process List", "ps aux"),
            ("Mount Points", "mount"),
            ("Network Interfaces", "ip addr show"),
            ("Environment Variables", "env | sort")
        ]

        output = "=== SYSTEM INFORMATION ===\n\n"
        for name, cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                output += f"--- {name} ---\n{result.stdout}\n\n"
            except:
                output += f"--- {name} ---\nFailed to execute\n\n"

        return render_template_string(VULNERABLE_TEMPLATE, output=output)
    except Exception as e:
        return render_template_string(VULNERABLE_TEMPLATE, output=f"Error: {str(e)}")

@app.route('/capabilities')
def check_capabilities():
    """Check container capabilities"""
    try:
        commands = [
            ("Current Process Capabilities", "cat /proc/self/status | grep Cap"),
            ("Capability Bounds", "capsh --print"),
            ("Effective Capabilities", "getcap /proc/self/exe 2>/dev/null || echo 'No capabilities set'")
        ]

        output = "=== CONTAINER CAPABILITIES ===\n\n"
        for name, cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                output += f"--- {name} ---\n{result.stdout}\n\n"
            except:
                output += f"--- {name} ---\nFailed to execute\n\n"

        return render_template_string(VULNERABLE_TEMPLATE, output=output)
    except Exception as e:
        return render_template_string(VULNERABLE_TEMPLATE, output=f"Error: {str(e)}")

@app.route('/modules')
def list_modules():
    """List and manipulate kernel modules (requires CAP_SYS_MODULE)"""
    try:
        commands = [
            ("Loaded Modules", "lsmod"),
            ("Module Directory", "ls -la /lib/modules/ 2>/dev/null || echo 'Module directory not accessible'"),
            ("Kernel Version", "uname -a"),
            ("Module Info (dummy)", "modinfo dummy 2>/dev/null || echo 'Module info not available'")
        ]

        output = "=== KERNEL MODULES ===\n\n"
        output += "Note: CAP_SYS_MODULE allows loading/unloading kernel modules\n"
        output += "This can be used for container escape techniques!\n\n"

        for name, cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                output += f"--- {name} ---\n{result.stdout}\n\n"
            except:
                output += f"--- {name} ---\nFailed to execute\n\n"

        return render_template_string(VULNERABLE_TEMPLATE, output=output)
    except Exception as e:
        return render_template_string(VULNERABLE_TEMPLATE, output=f"Error: {str(e)}")

@app.route('/api/rce', methods=['POST'])
def api_rce():
    """
    API endpoint for RCE - JSON interface
    """
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"error": "Missing 'command' parameter"}), 400

        command = data['command']
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)

        return jsonify({
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "pid": os.getpid(),
        "user": os.getenv('USER', 'unknown'),
        "capabilities": "CAP_SYS_MODULE enabled"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚨 VULNERABLE CONTAINER APPLICATION STARTING 🚨")
    print("=" * 60)
    print("WARNING: This application contains intentional vulnerabilities!")
    print("Use only in isolated testing environments.")
    print("Current PID:", os.getpid())
    print("Running as user:", os.getenv('USER', 'unknown'))
    print("=" * 60)

    # Run on all interfaces to be accessible from outside container
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
