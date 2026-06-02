# Справочник API

Технические спецификации модулей ядра **MYCELIUM CORE**.

---

## Модули

| Модуль | Файл | Описание |
|---|---|---|
| **[AppController](./controller.md)** | `app_controller.py` | Главный фасад между UI и доменными сервисами |
| **[VotingService](./voting-service.md)** | `voting_service.py` | Управление блокчейн-транзакциями |
| **[AuditService](./audit-service.md)** | `audit_service.py` | Верификация безопасности на основе событий |
| **[ErrorParser](./error-parser.md)** | `error_parser.py` | Перевод RPC-ошибок в i18n-ключи |
| **[Precheck](./precheck.md)** | `precheck.py` | 5-уровневая предголосовая валидация |
| **[GethManager](./geth-manager.md)** | `geth_manager.py` | Жизненный цикл процесса Geth |
| **[NonceManager](./nonce-manager.md)** | `nonce_manager.py` | Потокобезопасное отслеживание nonce |
| **[Web3Provider](./web3-provider.md)** | `web3_provider.py` | Синглтон RPC-подключения |
| **[CompilerService](./compiler-service.md)** | `compiler_service.py` | Компиляция Solidity |
| **[Models](./models.md)** | `models.py` | Доменные DTO и dataclasses |