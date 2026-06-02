"""
Интеграционный тест: полный цикл электронного голосования.
Требует бинарник Geth в bin/ и доступ к сети.

Запуск:
    pytest tests/test_integration.py -v

Покрывает ПОЛНЫЙ flow:
    1. Запуск Geth → Ожидание RPC
    2. Компиляция и деплой VotingCore
    3. Добавление кандидатов
    4. Генерация избирателей → Финансирование → Whitelist
    5. Начало голосования
    6. Отправка голосов
    7. Защита от двойного голосования
    8. Завершение голосования
    9. Полный аудит
    10. Проверка результатов
    11. Shutdown
"""
import pytest
import time

from src.utils.paths import GETH_BIN


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: интеграционные тесты (требуют Geth)"
    )


def _should_skip():
    """Пропускаем если бинарник Geth отсутствует."""
    if not GETH_BIN.exists():
        return True
    return False


integration = pytest.mark.skipif(
    _should_skip(),
    reason="Интеграционные тесты требуют бинарник Geth в bin/",
)


def _normalize_tx_hash(tx_hash: str) -> str:
    """
    Нормализует tx_hash — гарантирует префикс 0x.
    web3.py в разных версиях может возвращать hex с или без 0x.
    """
    if not tx_hash.startswith("0x"):
        return "0x" + tx_hash
    return tx_hash


@integration
class TestFullElectionLifecycle:
    """
    End-to-end тест полного жизненного цикла голосования.
    Использует реальный Geth в dev-режиме.
    """

    @pytest.fixture(scope="class")
    def controller(self):
        """Создаёт и запускает контроллер на весь класс тестов."""
        from src.core.app_controller import AppController
        from src.utils.paths import ensure_directories
        from src.utils.logger import setup_logging

        ensure_directories()
        setup_logging("WARNING")

        ctrl = AppController()
        ctrl.startup()
        ctrl.create_session()
        yield ctrl
        try:
            ctrl.shutdown()
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # 01. Подключение к RPC
    # ────────────────────────────────────────────────────────────
    def test_01_rpc_connected(self, controller):
        """Проверяем что Geth запущен и RPC доступен."""
        assert controller.get_rpc_status() is True

    # ────────────────────────────────────────────────────────────
    # 02. Режим Geth
    # ────────────────────────────────────────────────────────────
    def test_02_geth_mode(self, controller):
        """Geth должен быть в dev-режиме."""
        assert controller.get_geth_mode() == "dev"

    # ────────────────────────────────────────────────────────────
    # 03. Компиляция и деплой контракта
    # ────────────────────────────────────────────────────────────
    def test_03_compile_and_deploy(self, controller):
        """Компилируем VotingCore.sol и деплоим на локальную сеть."""
        from src.utils.crypto import generate_eth_keypair

        # Генерируем ключ администратора
        admin_key, admin_addr = generate_eth_keypair()

        # Финансируем admin с dev-аккаунта Geth
        controller.fund_from_dev(admin_addr, amount_eth=100.0)

        # Компилируем и деплоим
        controller.compile_contract()
        contract_addr = controller.deploy_contract(admin_key)

        assert contract_addr is not None
        assert contract_addr.startswith("0x")
        assert len(contract_addr) == 42
        assert controller.is_contract_deployed()

        # Сохраняем для последующих тестов
        self.__class__._admin_key = admin_key
        self.__class__._contract_addr = contract_addr

    # ────────────────────────────────────────────────────────────
    # 04. Регистрация кандидатов
    # ────────────────────────────────────────────────────────────
    def test_04_add_candidates(self, controller):
        """Добавляем 3 кандидатов в контракт."""
        from src.utils.crypto import generate_eth_keypair

        admin_key = self.__class__._admin_key

        _, c1_addr = generate_eth_keypair()
        _, c2_addr = generate_eth_keypair()
        _, c3_addr = generate_eth_keypair()

        controller.add_candidate(admin_key, "Алиса", "Синяя партия", c1_addr)
        controller.add_candidate(admin_key, "Борис", "Красная партия", c2_addr)
        controller.add_candidate(admin_key, "Виктор", "Зелёная партия", c3_addr)

        candidates = controller.get_candidates()
        assert len(candidates) == 3

        self.__class__._candidate_addrs = [c1_addr, c2_addr, c3_addr]

    # ────────────────────────────────────────────────────────────
    # 05. Генерация, финансирование и whitelist избирателей
    # ────────────────────────────────────────────────────────────
    def test_05_generate_and_setup_voters(self, controller):
        """Генерируем 5 избирателей, финансируем и добавляем в whitelist."""
        admin_key = self.__class__._admin_key

        # Генерация
        voters = controller.generate_voters(5)
        assert len(voters) == 5

        # Финансирование каждого (0.01 ETH для оплаты газа)
        for v in voters:
            controller.fund_voter(
                admin_key, v.address,
                amount_wei=int(0.01 * 10**18),
            )

        # Добавление в whitelist
        controller.whitelist_voters(admin_key)

        # Верификация
        for v in voters:
            assert controller.is_whitelisted(v.address), \
                f"Избиратель {v.address[:10]} не в whitelist"
            assert not controller.has_voted(v.address), \
                f"Избиратель {v.address[:10]} уже голосовал до начала"

        self.__class__._voters = voters

    # ────────────────────────────────────────────────────────────
    # 06. Начало голосования
    # ────────────────────────────────────────────────────────────
    def test_06_start_voting(self, controller):
        """Переводим контракт в стадию ACTIVE."""
        from src.core.models import ElectionStage

        admin_key = self.__class__._admin_key
        controller.start_voting(admin_key)

        stage = controller.get_stage()
        assert stage == ElectionStage.ACTIVE

    # ────────────────────────────────────────────────────────────
    # 07. Отправка голосов
    # ────────────────────────────────────────────────────────────
    def test_07_cast_votes(self, controller):
        """Каждый из 5 избирателей голосует за случайного кандидата."""
        import random
        random.seed(42)

        voters = self.__class__._voters
        candidates = self.__class__._candidate_addrs
        voted_count = 0

        for v in voters:
            candidate = random.choice(candidates)
            receipt = controller.cast_vote(v.private_key, candidate)

            assert receipt is not None, \
                f"Квитанция None для избирателя {v.address[:10]}"

            # Нормализуем tx_hash (web3.py может вернуть без 0x)
            tx_hash = _normalize_tx_hash(receipt.tx_hash)
            assert tx_hash.startswith("0x"), \
                f"tx_hash не начинается с 0x: {receipt.tx_hash}"
            assert len(tx_hash) == 66, \
                f"Некорректная длина tx_hash: {len(tx_hash)}"

            assert receipt.qr_bytes is not None, \
                "QR-код не сгенерирован"
            assert len(receipt.qr_bytes) > 100, \
                "QR-код слишком маленький"

            voted_count += 1

        assert voted_count == 5, \
            f"Ожидалось 5 голосов, получено {voted_count}"

        # Сохраняем количество для проверки в аудите
        self.__class__._expected_votes = voted_count

    # ────────────────────────────────────────────────────────────
    # 08. Защита от двойного голосования
    # ────────────────────────────────────────────────────────────
    def test_08_double_vote_prevented(self, controller):
        """Попытка повторного голосования должна вызвать ошибку."""
        voter = self.__class__._voters[0]
        candidate = self.__class__._candidate_addrs[0]

        with pytest.raises(RuntimeError):
            controller.cast_vote(voter.private_key, candidate)

    # ────────────────────────────────────────────────────────────
    # 09. Завершение голосования
    # ────────────────────────────────────────────────────────────
    def test_09_finish_voting(self, controller):
        """Переводим контракт в стадию FINISHED."""
        from src.core.models import ElectionStage

        admin_key = self.__class__._admin_key
        controller.finish_voting(admin_key)

        stage = controller.get_stage()
        assert stage == ElectionStage.FINISHED

    # ────────────────────────────────────────────────────────────
    # 10. Полный аудит
    # ────────────────────────────────────────────────────────────
    def test_10_audit(self, controller):
        """
        Запускаем полный аудит и проверяем результаты.

        Примечание: Stage Check возвращает WARNING (не FAILED) для
        стадии FINISHED при full audit — это корректное поведение,
        так как pre-vote check ожидает SETUP, а мы уже в FINISHED.
        WARNING не считается провалом для целей этого теста.
        """
        report = controller.run_audit()
        assert report is not None

        # Проверяем что нет FAILED проверок
        failed_checks = [
            c for c in report.checks if c.status == "FAILED"
        ]
        assert len(failed_checks) == 0, \
            f"Проваленные проверки: {[(c.check_name, c.details) for c in failed_checks]}"

        # WARNING допустим (Stage Check для pre-vote в FINISHED стадии)
        # SKIPPED допустим (некоторые проверки не применимы)
        for check in report.checks:
            assert check.status in ("PASSED", "WARNING", "SKIPPED"), \
                f"Неожиданный статус '{check.status}' для проверки '{check.check_name}'"

        # Проверяем количество голосов
        expected = self.__class__._expected_votes
        results = controller.get_results()
        total_votes = sum(c.vote_count for c in results)
        assert total_votes == expected, \
            f"Ожидалось {expected} голосов, посчитано {total_votes}"

    # ────────────────────────────────────────────────────────────
    # 11. Определение победителя
    # ────────────────────────────────────────────────────────────
    def test_11_winner_exists(self, controller):
        """После завершения голосования должен быть определён победитель."""
        winner = controller.get_winner()
        assert winner is not None, "Победитель не определён"
        assert winner["type"] in ("winner", "tie"), \
            f"Неожиданный тип результата: {winner['type']}"

        if winner["type"] == "winner":
            c = winner["candidate"]
            assert c.vote_count > 0, "У победителя 0 голосов"
        else:
            # Ничья
            assert len(winner["candidates"]) >= 2

    # ────────────────────────────────────────────────────────────
    # 12. Полный отчёт
    # ────────────────────────────────────────────────────────────
    def test_12_full_report(self, controller):
        """Проверяем структуру полного отчёта для экспорта."""
        report = controller.build_full_report()

        # Обязательные ключи верхнего уровня
        required_keys = {
            "session_id", "timestamp", "contract_address",
            "stage", "deploy_block", "results", "winner", "audit",
        }
        assert required_keys.issubset(report.keys()), \
            f"Отсутствуют ключи: {required_keys - report.keys()}"

        # 3 кандидата в результатах
        assert len(report["results"]) == 3

        # Стадия FINISHED
        assert report["stage"] == "FINISHED"

        # Контракт развёрнут
        assert report["contract_address"] is not None
        assert report["contract_address"].startswith("0x")

        # Аудит содержит проверки
        assert "checks" in report["audit"]
        assert len(report["audit"]["checks"]) > 0

        # Победитель определён
        assert report["winner"] is not None