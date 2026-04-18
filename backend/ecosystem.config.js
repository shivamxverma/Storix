module.exports = {
  apps: [
    {
      name: "asyncdoc-api",
      script: "venv/bin/uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8020",
      cwd: ".",
      interpreter: "python3",
      watch: false,
      env: {
        NODE_ENV: "production",
      },
      env_file: ".env",
    },
    {
      name: "asyncdoc-worker",
      script: "venv/bin/celery",
      args: "-A app.worker.tasks worker --loglevel=info",
      cwd: ".",
      interpreter: "python3",
      watch: false,
      env: {
        NODE_ENV: "production",
        OBJC_DISABLE_INITIALIZE_FORK_SAFETY: "YES",
      },
      env_file: ".env",
    },
  ],
};
