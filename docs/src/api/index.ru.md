# Справочник API

Технические спецификации модулей ядра **MYCELIUM CORE**.

---

## Модули

| Модуль | Файл | Описание |
|---|---|---|
| **[AppController](./controller.ru.md)** | `app_controller.py` | Главный фасад между UI и доменными сервисами |
| **[VotingService](./voting-service.ru.md)** | `voting_service.py` | Управление блокчейн-транзакциями |
| **[AuditService](./audit-service.ru.md)** | `audit_service.py` | Верификация безопасности на основе событий |
| **[ErrorParser](./error-parser.ru.md)** | `error_parser.py` | Перевод RPC-ошибок в i18n-ключи |
| **[Precheck](./precheck.ru.md)** | `precheck.py` | 5-уровневая предголосовая валидация |
| **[GethManager](./geth-manager.ru.md)** | `geth_manager.py` | Жизненный цикл процесса Geth |
| **[NonceManager](./nonce-manager.ru.md)** | `nonce_manager.py` | Потокобезопасное отслеживание nonce |
| **[Web3Provider](./web3-provider.ru.md)** | `web3_provider.py` | Синглтон RPC-подключения |
| **[CompilerService](./compiler-service.ru.md)** | `compiler_service.py` | Компиляция Solidity |
| **[Models](./models.ru.md)** | `models.py` | Доменные DTO и dataclasses |