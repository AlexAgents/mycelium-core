"""
Менеджер процесса Geth.
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, IO, Optional

from src.utils.logger import get_logger
from src.utils.paths import (
    BIN_DIR,
    CHAIN_ACTIVE,
    CHAIN_ARCHIVES,
    GETH_BIN,
)

logger = get_logger(__name__)


class GethManager:
    def __init__(
        self,
        rpc_host: str = "127.0.0.1",
        rpc_port: int = 8545,
        network_id: int = 1337,
    ) -> None:
        self.rpc_host = rpc_host
        self.rpc_port = rpc_port
        self.network_id = network_id

        self._process: Optional[subprocess.Popen] = None
        self._crash_callback: Optional[Callable[[], None]] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._log_fh: Optional[IO] = None

        # режим запуска Geth
        self._mode: str = "dev"
        self._shutting_down: bool = False
        self._launch_args: list[str] = []

    # ─────────────────────────────────────────────────────────────
    # Свойства
    # ─────────────────────────────────────────────────────────────
    @property
    def mode(self) -> str:
        """
        Возвращает режим работы Geth.
        'dev' — стандартный dev-mode (--dev).
        'custom' — если аргументы были переопределены.
        """
        return self._mode

    @property
    def rpc_url(self) -> str:
        return f"http://{self.rpc_host}:{self.rpc_port}"

    # ─────────────────────────────────────────────────────────────
    def set_crash_callback(self, cb: Callable[[], None]) -> None:
        self._crash_callback = cb

    # ─────────────────────────────────────────────────────────────
    def start(self) -> None:
        if not GETH_BIN.exists():
            raise FileNotFoundError(f"Geth not found:\n{GETH_BIN}")

        if self.is_running():
            logger.warning("Geth already running")
            return

        # Сбросить флаг shutdown для нового запуска
        self._shutting_down = False

        # Страховка: убить зомби-процессы
        self._taskkill_all_geth()
        import time
        time.sleep(1.0)

        # Geth --dev несовместим с persistent chain-data:
        # state хранится в памяти, header'ы на диске,
        # после перезапуска получается corrupted DB.
        # Поэтому при каждом старте чистим chain-data.
        if CHAIN_ACTIVE.exists():
            logger.info("Cleaning chain-data for fresh dev start...")
            try:
                shutil.rmtree(CHAIN_ACTIVE, ignore_errors=True)
            except Exception as exc:
                logger.warning("Could not fully clean chain-data: %s", exc)

        CHAIN_ACTIVE.mkdir(parents=True, exist_ok=True)

        # Проверка: не занят ли порт 8545 другим процессом
        if self._is_port_in_use():
            logger.warning(
                "Port %d is already in use. Killing existing geth...",
                self.rpc_port,
            )
            self._taskkill_all_geth()
            import time
            time.sleep(2.0)
            if self._is_port_in_use():
                raise RuntimeError(
                    f"Port {self.rpc_port} is occupied by another process. "
                    f"Stop it manually and restart the application."
                )

        self._launch_geth()

        logger.info(
            "Geth started PID=%s mode=%s",
            self._process.pid if self._process else "unknown",
            self._mode,
        )

    # ─────────────────────────────────────────────────────────────

    def stop(self) -> None:
        """
        Останавливает Geth с гарантией.

        Выставляет _shutting_down=True ДО terminate, чтобы monitor_thread
        не интерпретировал намеренное завершение как crash.
        """
        import time

        # ВАЖНО: флаг ставим ПЕРВЫМ делом, до любых действий
        self._shutting_down = True

        if self._process is None:
            self._close_log_fh()
            return

        if self._process.poll() is not None:
            self._process = None
            self._close_log_fh()
            time.sleep(0.5)
            return

        pid = self._process.pid
        logger.info("Stopping Geth (PID=%s)...", pid)

        # Мягкое завершение
        try:
            self._process.terminate()
            self._process.wait(timeout=10)
            logger.info("Geth terminated gracefully")
        except subprocess.TimeoutExpired:
            logger.warning("Geth did not stop on terminate, killing...")
            try:
                self._process.kill()
                self._process.wait(timeout=5)
                logger.info("Geth killed via Popen.kill()")
            except Exception as exc:
                logger.warning("Popen.kill() failed: %s", exc)
        except Exception as exc:
            logger.warning("Geth.terminate() error: %s", exc)

        # Гарантированный taskkill
        self._force_kill_pid(pid)
        self._taskkill_all_geth()

        self._process = None
        self._close_log_fh()

        time.sleep(1.5)
        logger.info("Geth stopped")

    @staticmethod
    def _force_kill_pid(pid: int) -> None:
        """Принудительное завершение процесса по PID на уровне ОС."""
        import platform as _plat
        try:
            if _plat.system() == "Windows":
                import os
                os.system(f"taskkill /F /PID {pid} /T >nul 2>&1")
            else:
                import signal
                import os
                os.kill(pid, signal.SIGKILL)
            logger.info("Force killed PID %d", pid)
        except Exception as exc:
            logger.error("Failed to force kill PID %d: %s", pid, exc)

    @staticmethod
    def _taskkill_all_geth() -> None:
        """
        Страховка: убивает все geth.exe в системе.
        Только Windows.
        """
        import platform as _plat
        if _plat.system() != "Windows":
            return
        try:
            import os
            # /F = force, /IM = image name, /T = вместе с дочерними
            os.system("taskkill /F /IM geth.exe /T >nul 2>&1")
            logger.info("taskkill /IM geth.exe executed")
        except Exception as exc:
            logger.debug("taskkill /IM geth.exe failed: %s", exc)

    def _is_port_in_use(self) -> bool:
        """Проверка занятости порта RPC."""
        import socket
        try:
            with socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            ) as s:
                s.settimeout(0.5)
                result = s.connect_ex((self.rpc_host, self.rpc_port))
                return result == 0
        except Exception:
            return False


    # ─────────────────────────────────────────────────────────────
    def is_running(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    # ─────────────────────────────────────────────────────────────
    def purge_chain_data(self, archive: bool = True) -> None:
        if not CHAIN_ACTIVE.exists():
            return

        if archive:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = CHAIN_ARCHIVES / f"old_{ts}"
            CHAIN_ARCHIVES.mkdir(parents=True, exist_ok=True)
            shutil.move(str(CHAIN_ACTIVE), str(archive_path))
            logger.info("Chain archived: %s", archive_path)
        else:
            shutil.rmtree(CHAIN_ACTIVE, ignore_errors=True)
            logger.info("Chain deleted")

        # Страховка: убить зомби-процессы geth.exe от прошлого запуска
        self._taskkill_all_geth()
        import time
        time.sleep(2.0)

        CHAIN_ACTIVE.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # Внутренние методы
    # ─────────────────────────────────────────────────────────────
    def _launch_geth(self) -> None:
        log_file = CHAIN_ACTIVE / "geth.log"

        cmd = [
            str(GETH_BIN),
            "--dev",
            "--dev.period", "5",
            "--datadir", str(CHAIN_ACTIVE),
            "--http",
            "--http.addr", self.rpc_host,
            "--http.port", str(self.rpc_port),
            "--http.api",
            "eth,net,web3,personal,miner,admin,txpool",
            "--http.corsdomain", "*",
            "--networkid", str(self.network_id),
            "--allow-insecure-unlock",
            "--nodiscover",
            "--maxpeers", "0",
            "--verbosity", "3",
        ]

        # Определяем режим
        if "--dev" in cmd:
            self._mode = "dev"
        else:
            self._mode = "custom"

        self._launch_args = list(cmd)

        logger.info("Launching Geth in %s mode…", self._mode)

        self._log_fh = open(log_file, "a", encoding="utf-8")

        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW

        self._process = subprocess.Popen(
            cmd,
            stdout=self._log_fh,
            stderr=self._log_fh,
            stdin=subprocess.DEVNULL,
            creationflags=creation_flags,
        )

        self._monitor_thread = threading.Thread(
            target=self._monitor_process,
            daemon=True,
        )
        self._monitor_thread.start()

    # ─────────────────────────────────────────────────────────────
    def _close_log_fh(self) -> None:
        if self._log_fh is not None:
            try:
                self._log_fh.close()
            except OSError:
                pass
            finally:
                self._log_fh = None

    # ─────────────────────────────────────────────────────────────
    def _monitor_process(self) -> None:
        """
        Мониторит процесс Geth.

        Crash_callback вызывается ТОЛЬКО если процесс умер сам,
        без намеренного stop() (т.е. _shutting_down == False).
        """
        import time as _time

        # Период ожидания запуска
        grace_deadline = _time.monotonic() + 5.0
        died_during_grace = False

        while _time.monotonic() < grace_deadline:
            if self._shutting_down:
                return  # Намеренный shutdown
            if not self.is_running():
                died_during_grace = True
                logger.error(
                    "Geth FAILED TO START — process exited "
                    "during grace period. Check geth.log for details."
                )
                break
            _time.sleep(0.5)

        if not died_during_grace:
            # Нормальный мониторинг
            while self.is_running():
                if self._shutting_down:
                    return  # Намеренный shutdown
                _time.sleep(2)

            # Сюда попадаем если процесс умер сам.
            # Ещё раз проверяем shutting_down (race condition защита)
            if self._shutting_down:
                return
            logger.error("Geth terminated unexpectedly")

        # Сигнализируем UI ТОЛЬКО если это реальный crash
        if not self._shutting_down and self._crash_callback:
            try:
                self._crash_callback()
            except Exception as exc:
                logger.error("Crash callback failed: %s", exc)