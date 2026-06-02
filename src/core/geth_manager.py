"""
Geth process manager.
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
        # FIX: храним файловый дескриптор, чтобы закрыть его при остановке
        self._log_fh: Optional[IO] = None

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
        CHAIN_ACTIVE.mkdir(parents=True, exist_ok=True)
        self._launch_geth()
        logger.info(
            "Geth started PID=%s",
            self._process.pid if self._process else "unknown",
        )

    # ─────────────────────────────────────────────────────────────
    def stop(self) -> None:
        if self._process is None:
            return
        if self._process.poll() is not None:
            self._process = None
            self._close_log_fh()
            return

        logger.info("Stopping Geth...")
        try:
            self._process.terminate()
            self._process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logger.warning("Force killing Geth")
            self._process.kill()
            self._process.wait()
        finally:
            self._process = None
            # FIX: закрываем лог-файл после завершения процесса
            self._close_log_fh()
            logger.info("Geth stopped")

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
        CHAIN_ACTIVE.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    @property
    def rpc_url(self) -> str:
        return f"http://{self.rpc_host}:{self.rpc_port}"

    # ─────────────────────────────────────────────────────────────
    # Internal
    # ─────────────────────────────────────────────────────────────
    def _launch_geth(self) -> None:
        log_file = CHAIN_ACTIVE / "geth.log"
        cmd = [
            str(GETH_BIN),
            "--dev",
            "--datadir", str(CHAIN_ACTIVE),
            "--http",
            "--http.addr", self.rpc_host,
            "--http.port", str(self.rpc_port),
            "--http.api", "eth,net,web3,personal,miner,admin,txpool",
            "--http.corsdomain", "*",
            "--networkid", str(self.network_id),
            "--allow-insecure-unlock",
            "--nodiscover",
            "--maxpeers", "0",
            "--verbosity", "3",
        ]
        logger.info("Launching Geth...")

        # FIX: сохраняем дескриптор в self._log_fh для последующего закрытия
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
        """Закрывает файловый дескриптор лога, если он открыт."""
        if self._log_fh is not None:
            try:
                self._log_fh.close()
            except OSError:
                pass
            finally:
                self._log_fh = None

    # ─────────────────────────────────────────────────────────────
    def _monitor_process(self) -> None:
        while self.is_running():
            time.sleep(2)
        logger.error("Geth terminated unexpectedly")
        if self._crash_callback:
            self._crash_callback()