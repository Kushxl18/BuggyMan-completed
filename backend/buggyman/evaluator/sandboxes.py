import os
import sys
import time
import tempfile
import subprocess
from abc import ABC, abstractmethod


class SandboxResult:
    def __init__(self, exit_code=0, stdout="", stderr="", timed_out=False, error=None, execution_time=0.0):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out
        self.error = error
        self.execution_time = execution_time

    def to_dict(self):
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timed_out": self.timed_out,
            "error": self.error,
            "execution_time": round(self.execution_time, 4)
        }


class SandboxRunner(ABC):
    """
    Abstract Base Class for code sandbox execution environments.
    Guarantees that runners provide an isolated workspace and execution bounds.
    """
    @abstractmethod
    def run(self, files, command, timeout=5.0, stdin_data=None):
        pass


class SubprocessSandboxRunner(SandboxRunner):
    """
    Local isolated process sandbox runner.
    
    Security controls implemented:
    - Filesystem isolation: executes in an ephemeral temporary directory created per run.
    - Environment scrubbing: removes all host Django environment variables, secret keys, and DB credentials.
    - Process isolation: executes command directly without a shell (shell=False).
    - Timeout enforcement: kills process tree if execution time exceeds timeout threshold.
    - Automatic cleanup: deletes temporary directory immediately after execution.
    """

    SAFE_ENV_KEYS = [
        "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "PATHEXT",
        "LANG", "LC_ALL", "HOME", "USER"
    ]

    MAX_OUTPUT_CHARS = 65536  # 64 KB maximum output buffer to prevent RAM exhaustion

    @staticmethod
    def _truncate_output(text):
        if text and len(text) > SubprocessSandboxRunner.MAX_OUTPUT_CHARS:
            return text[:SubprocessSandboxRunner.MAX_OUTPUT_CHARS] + "\n... [Output truncated after 64KB]"
        return text

    def run(self, files, command, timeout=5.0, stdin_data=None):
        start_time = time.time()
        
        with tempfile.TemporaryDirectory(prefix="buggyman_sandbox_") as temp_dir:
            # 1. Write workspace files safely inside temp directory
            for f in files:
                rel_path = f.get("name") or f.get("filename") or "main.txt"
                content = f.get("content") or ""

                # Prevent path traversal attacks (e.g., ../../etc/passwd)
                safe_rel_path = os.path.normpath(rel_path).lstrip("/\\")
                if safe_rel_path.startswith(".."):
                    continue

                full_path = os.path.join(temp_dir, safe_rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "w", encoding="utf-8", errors="replace") as out_file:
                    out_file.write(content)

            # 2. Build sanitized environment
            sanitized_env = {
                key: os.environ[key]
                for key in self.SAFE_ENV_KEYS
                if key in os.environ
            }
            # Prevent Python buffering and bytecode generation leaks
            sanitized_env["PYTHONUNBUFFERED"] = "1"
            sanitized_env["PYTHONDONTWRITEBYTECODE"] = "1"

            # 3. Configure platform-specific execution sandbox constraints
            preexec = None
            if sys.platform != "win32":
                def _linux_limits():
                    try:
                        import resource
                        # Cap process memory to 512MB
                        mem = 512 * 1024 * 1024
                        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                    except Exception:
                        pass
                    try:
                        os.setsid()
                    except Exception:
                        pass
                preexec = _linux_limits

            # 4. Execute subprocess
            timed_out = False
            error_msg = None
            stdout_text = ""
            stderr_text = ""
            exit_code = -1

            try:
                proc = subprocess.Popen(
                    command,
                    cwd=temp_dir,
                    stdin=subprocess.PIPE if stdin_data else subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=sanitized_env,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    preexec_fn=preexec
                )

                input_bytes = stdin_data if stdin_data else None
                out, err = proc.communicate(input=input_bytes, timeout=timeout)
                stdout_text = self._truncate_output(out or "")
                stderr_text = self._truncate_output(err or "")
                exit_code = proc.returncode

            except subprocess.TimeoutExpired:
                timed_out = True
                error_msg = f"Execution timed out after {timeout} seconds."
                exit_code = 124
                try:
                    if sys.platform != "win32" and hasattr(os, 'killpg'):
                        import signal
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    else:
                        proc.kill()
                except Exception:
                    proc.kill()
                try:
                    out, err = proc.communicate(timeout=1.0)
                    stdout_text = self._truncate_output(out or "")
                    stderr_text = self._truncate_output((err or "") + f"\n[TIMEOUT] Killed process after {timeout}s limit.")
                except Exception:
                    stderr_text = f"[TIMEOUT] Killed process after {timeout}s limit."

            except FileNotFoundError as e:
                error_msg = f"Runtime executable not found: {command[0]}"
                stderr_text = error_msg
                exit_code = 127

            except Exception as e:
                error_msg = f"Sandbox execution error: {str(e)}"
                stderr_text = error_msg
                exit_code = 1

            elapsed = time.time() - start_time
            return SandboxResult(
                exit_code=exit_code,
                stdout=stdout_text,
                stderr=stderr_text,
                timed_out=timed_out,
                error=error_msg,
                execution_time=elapsed
            )


class DockerSandboxRunner(SandboxRunner):
    """
    Production Docker container sandbox runner stub.
    Can be configured in production settings when Docker daemon is available.
    """
    def __init__(self, image_name="buggyman-runner:latest"):
        self.image_name = image_name

    def run(self, files, command, timeout=5.0, stdin_data=None):
        # Stub implementation falling back gracefully or returning error
        return SandboxResult(
            exit_code=1,
            stdout="",
            stderr="Docker sandbox is not configured in current environment. Use SubprocessSandboxRunner.",
            error="Docker sandbox unavailable"
        )
