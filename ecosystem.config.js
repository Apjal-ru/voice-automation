module.exports = {
  apps: [
    {
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
    {
      name: "voltagent",
      script: "npm",
      args: "run dev",
      cwd: "/home/afzal/project-ragrs/darsi_doctor",
      watch: false,
      ignore_watch: ["node_modules", "dist"],
      exec_mode: "fork",
      env: {
        NODE_ENV: "development",
      }
    },
    {
      name: "assistant-ui",
      script: "npm",
      args: "run dev",
      cwd: "/home/afzal/project-ragrs/darsi_doctor/assistant-ui",
      watch: false,
      ignore_watch: ["node_modules", ".next"],
      exec_mode: "fork",
      env: {
        NODE_ENV: "development",
      }
    }
  ]
}
