# UniStudent — Title-Based Corporation Group Sync

**UniStudent** automatically manages student access in AllianceAuth by linking:

✔ EVE Online corporation titles (via ESI)
➡ to
✔ AllianceAuth Groups

This allows your EVE corp to control access inside AllianceAuth based on in-game roles.

______________________________________________________________________

## ⚙ Initial Setup

### 1️⃣ Obtain and verify a valid ESI token

Navigate to:

```
/unistudent/
```

Or from the Sidebar:

> **UniStudent** (visible only to Directors)

You will be asked to grant ESI permissions:
`esi-corporations.read_titles.v1`

You can return to this page at any time to check token status and refresh it.

______________________________________________________________________

### 2️⃣ Confirm that EVE titles have synced

Once a valid token is granted, a background sync will pull your corporation’s titles.

Check in Admin:

```
/admin/unistudent/title/
```

If no titles are listed yet:

- wait for the next scheduled sync, or
- manually trigger the cron task early (instructions below)

______________________________________________________________________

### 3️⃣ Link an EVE title to an AllianceAuth Group

In the Admin:

```
/admin/unistudent/selectedtitle/
```

- Select your corporation
- Choose which title should represent “Student”
- Choose the AA Group to grant (e.g. *Students*)

> Only **one** title may be selected per corporation (expandable in the future)

______________________________________________________________________

### 4️⃣ Allow or trigger synchronization

Once the selected title is set, the next sync will:

✔ Check members’ in-game titles
✔ Add/remove users from the associated AA group accordingly

You may:

- wait for the next scheduled sync, or
- manually trigger it

______________________________________________________________________

## 🔄 Scheduling the Sync Task

This app uses a Celery beat task to keep AA groups updated automatically.

Example config for `local.py`:

```python
CELERYBEAT_SCHEDULE["unistudent_sync_all"] = {
    "task": "unistudent.tasks.pull_all_titles",
    "schedule": 86400,  # once per day (in seconds)
}
```

You may adjust the interval based on fleet size or operational needs:

| Schedule                 | Value  |
| ------------------------ | ------ |
| Every hour               | `3600` |
| Every 30 min             | `1800` |
| Every 5 min *(dev only)* | `300`  |

______________________________________________________________________

## ⚡ What UniStudent Currently Does

| Feature                               | Status |
| ------------------------------------- | :----: |
| Token validity tracking               |   ✔    |
| Pull corp titles                      |   ✔    |
| Store & clean title names             |   ✔    |
| Select one AA group per corp title    |   ✔    |
| Pull member → title mapping           |   ✔    |
| Bulk update AA group membership       |   ✔    |
| Automatic recover from expired tokens |   ✔    |

______________________________________________________________________

## 🛠 Planned Enhancements

| Feature                                   | Status    |
| ----------------------------------------- | --------- |
| Support multiple selected titles per corp | 🚧 future |
| UI visual indicators for student status   | planned   |
| Admin UI for sync discovery + logs        | planned   |
| Auto-sync on demand via UI                | planned   |
| Role-based auto-kick from Mumble/Discord  | planned   |

______________________________________________________________________

## 📌 Notes

✔ Data is only refreshed using **valid director tokens**
✔ The system automatically falls back to any other valid director if one token expires
✔ ESI cached responses are handled correctly to avoid rate limits
✔ All updates are logged for audit tra
