# Настройка GitHub App для Eva

## Зачем GitHub App, а не PAT?

- Не привязан к человеку (не сломается при уходе из команды)
- Отдельный identity: коммиты от `ievo-eva[bot]`
- Гранулярные permissions (только то, что нужно)
- Не занимает seat в организации
- Rate limit выше чем у PAT (5000 → 15000 req/h)

---

## Шаг 1: Создать App

1. Открой: https://github.com/organizations/ievo-ai/settings/apps/new
   (или GitHub → ievo-ai → Settings → Developer settings → GitHub Apps → New)

2. Заполни:

| Поле | Значение |
|------|----------|
| **App name** | `ievo-eva` |
| **Description** | Meta-evolution Mother agent for iEvo platform |
| **Homepage URL** | `https://ievo.ai` |
| **Webhook** | ❌ Убери галку "Active" (Eva сама поллит, не нужен webhook) |

3. **Permissions** (Repository permissions):

| Permission | Access | Зачем |
|-----------|--------|-------|
| **Issues** | Read | Читать issues для анализа |
| **Pull requests** | Read & Write | Читать PR comments + создавать PR |
| **Contents** | Read & Write | Читать файлы + пушить ветки для PR |
| **Metadata** | Read | Базовая инфо о репо (автоматически) |

4. **Where can this app be installed?** → Only on this account

5. **Create GitHub App**

---

## Шаг 2: Сгенерировать Private Key

1. После создания → в настройках App
2. Прокрутить до **Private keys**
3. **Generate a private key** → скачается `.pem` файл
4. Сохрани его в безопасное место

---

## Шаг 3: Установить App на репозитории

1. В настройках App → **Install App** (левая панель)
2. Выбрать организацию **ievo-ai**
3. **Only select repositories** → выбрать:
   - `cli`
   - `marketplace`
   - `sdk`
   - `eva`
   - `ievo.ai`
4. **Install**

---

## Шаг 4: Получить Installation Token

GitHub App аутентифицируется через JWT → Installation Token.
Для GitHub Actions это проще всего через action:

### В GitHub Actions (рекомендуемый способ)

Добавить секреты в `ievo-ai/eva` → Settings → Secrets → Actions:

| Secret | Значение |
|--------|----------|
| `APP_ID` | ID приложения (видно на странице App) |
| `APP_PRIVATE_KEY` | Содержимое `.pem` файла |

Затем обновить workflows — заменить PAT на App token:

```yaml
# Вместо:
# env:
#   EVA_GITHUB_TOKEN: ${{ secrets.EVA_GITHUB_TOKEN }}

# Используем:
- name: Generate token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
    owner: ievo-ai

- name: Run Eva scan
  env:
    EVA_GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
  run: |
    docker run --rm -e EVA_GITHUB_TOKEN eva:local scan
```

### Для локального тестирования / self-hosted

Можно сгенерировать токен через скрипт:

```bash
# Установить
pip install PyJWT cryptography

# Сгенерировать (см. scripts/generate-app-token.py)
python scripts/generate-app-token.py \
  --app-id 123456 \
  --private-key path/to/key.pem \
  --org ievo-ai
```

---

## Шаг 5: Обновить секреты

### Для GitHub Actions
- Удалить: `EVA_GITHUB_TOKEN`
- Добавить: `APP_ID`, `APP_PRIVATE_KEY`

### Для self-hosted Docker
```env
# .env
EVA_APP_ID=123456
EVA_APP_PRIVATE_KEY_PATH=/path/to/key.pem
```

---

## Проверка

```bash
# В Actions: запусти workflow вручную
# В Eva логах должно быть:
#   ✓ github_issues: N signals
#   (не 401/403 ошибки)
```

---

## Quick start (PAT для быстрого тестирования)

Если хочешь начать быстро, можно пока использовать Fine-grained PAT:

1. https://github.com/settings/tokens?type=beta
2. **Token name**: `eva-test`
3. **Resource owner**: `ievo-ai`
4. **Repository access**: Only select → все ievo repos
5. **Permissions**: Issues (read), Pull requests (read), Contents (read)
6. **Generate token**
7. Добавить в секреты как `EVA_GITHUB_TOKEN`

Потом перейти на GitHub App когда всё заработает.
