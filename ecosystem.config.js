module.exports = {
  apps: [{
    name: "demo-rsi",
    interpreter: "./venv/bin/python3",
    script: "uvicorn",
    args: "main:app --host 10.9.23.205 --port 8088",
    watch: false,
    ignore_watch: ["uploads", "node_modules"],
    exec_mode: "fork",
    cwd: "/home/afzal/project-ragrs",
    env: {
      PATH: "/usr/bin",
    }
  },
  ]
}
