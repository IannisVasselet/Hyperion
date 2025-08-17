// api/static/js/ssh_wasm.js
let pyodide = null;

async function loadPyodideAndPackages() {
    if (pyodide !== null) return;

    pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/"
    });

    await pyodide.loadPackage("paramiko");
    await pyodide.runPythonAsync(`
    from pyodide.http import pyfetch
    response = await pyfetch("/static/utils/ssh_client.py")
    with open("ssh_client.py", "wb") as f:
        f.write(await response.bytes())
    from ssh_client import SSHClient
  `);
}

async function createSSHClient() {
    await loadPyodideAndPackages();
    return pyodide.runPython(`
    client = SSHClient()
    client
  `);
}

async function connectSSH() {
    const host = document.getElementById('host').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const client = await createSSHClient();
        const connected = await client.connect(host, username, password);

        if (connected === true) {
            appendToTerminal('Connected successfully!');
        } else {
            appendToTerminal('Connection failed: ' + connected);
        }
    } catch (err) {
        appendToTerminal('Error: ' + err.message);
    }
}

async function executeCommand() {
    const command = document.getElementById('command').value;

    try {
        const output = await pyodide.runPythonAsync(`
            client.execute("${command}")
        `);
        appendToTerminal('$ ' + command);
        appendToTerminal(output);
    } catch (err) {
        appendToTerminal('Error: ' + err.message);
    }
}

function appendToTerminal(text) {
    const terminal = document.getElementById('terminal-output');
    terminal.innerHTML += text + '\n';
    terminal.scrollTop = terminal.scrollHeight;
}