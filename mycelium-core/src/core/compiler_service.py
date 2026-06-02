"""
Компиляция Solidity-контрактов.
"""

from __future__ import annotations

import json
from pathlib import Path

from solcx import (
    compile_standard,
    install_solc,
    set_solc_version,
)

from src.utils.config import get_env_config
from src.utils.logger import get_logger
from src.utils.paths import (
    CONTRACT_SOL,
    CONTRACT_ABI,
)

logger = get_logger(__name__)


class CompilerService:

    def __init__(self) -> None:
        self.env = get_env_config()
        self.solidity_version = self.env.solidity_version

    # ─────────────────────────────────────────────────────────────

    def compile_contract(self) -> tuple[list, str]:
        """
        Компилирует VotingCore.sol.
        Returns:
            tuple(abi, bytecode)
        """

        if not CONTRACT_SOL.exists():
            raise FileNotFoundError(
                f"Contract not found: {CONTRACT_SOL}"
            )

        logger.info(
            "Installing solc version %s",
            self.solidity_version,
        )

        install_solc(self.solidity_version)

        set_solc_version(self.solidity_version)

        source = CONTRACT_SOL.read_text(encoding="utf-8")

        logger.info("Compiling contract: %s", CONTRACT_SOL.name)

        compiled = compile_standard(
            {
                "language": "Solidity",
                "sources": {
                    CONTRACT_SOL.name: {
                        "content": source
                    }
                },
                "settings": {
                    "optimizer": {
                        "enabled": True,
                        "runs": 200,
                    },
                    "outputSelection": {
                        "*": {
                            "*": [
                                "abi",
                                "evm.bytecode.object",
                            ]
                        }
                    },
                },
            }
        )

        contract_data = compiled["contracts"][
            CONTRACT_SOL.name
        ]["VotingCore"]

        abi = contract_data["abi"]

        bytecode = contract_data["evm"][
            "bytecode"
        ]["object"]

        self._save_artifacts(abi, bytecode)

        logger.info("Contract compiled successfully")

        return abi, bytecode

    # ─────────────────────────────────────────────────────────────

    def _save_artifacts(
        self,
        abi: list,
        bytecode: str,
    ) -> None:
        """
        Сохраняет ABI + bytecode.
        """

        CONTRACT_ABI.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "contract": "VotingCore",
            "abi": abi,
            "bytecode": bytecode,
        }

        CONTRACT_ABI.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

        logger.info(
            "Artifacts saved: %s",
            CONTRACT_ABI,
        )

    # ─────────────────────────────────────────────────────────────

    def load_artifacts(self) -> tuple[list, str]:
        """
        Загружает ABI и bytecode.
        """

        if not CONTRACT_ABI.exists():
            raise FileNotFoundError(
                "Compiled ABI artifact not found"
            )

        data = json.loads(
            CONTRACT_ABI.read_text(
                encoding="utf-8"
            )
        )

        abi = data["abi"]
        bytecode = data["bytecode"]

        return abi, bytecode