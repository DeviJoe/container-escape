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
    <title>Universal Pinger</title>
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
            <strong>⚠️ WARNING:</strong> This app may only ping another host and nothing else. It is not intended for malicious use.
        </div>

        <h1>Universal Pinger</h1>
        <p>This application pings a host. And makes it good.</p>

        <h2>Ping it</h2>
        <form action="/execute" method="post">
            <div class="form-group">
                <label>Write your host:</label><br>
                <input type="text" name="command" placeholder="8.8.8.8" value="{{ command }}">
                <button type="submit">Execute</button>
            </div>
        </form>

        {% if output %}
        <h3>Output:</h3>
        <div class="output">{{ output }}</div>
        {% endif %}
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
            result = subprocess.run("ping -c 1 " + command, shell=True, capture_output=True, text=True, timeout=10)
            output = f"Return code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            output = "Command timed out after 10 seconds"
        except Exception as e:
            output = f"Error executing command: {str(e)}"

    return render_template_string(VULNERABLE_TEMPLATE, command=command, output=output)

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
