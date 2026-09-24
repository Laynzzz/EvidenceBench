# Local Docker startup investigation, 2026-09-24

Outcome: the joint socket refresh restored Docker Engine 29.0.1. The existing
`evidencebench-db-1` container started with its retained volume and reached healthy
status using `docker compose up -d --no-deps --pull never --wait --wait-timeout 45 db`.
The application container was not started as part of this recovery.
The database-enabled software suite then passed **194 tests**, with two existing
Starlette deprecation warnings, in 12.43 seconds. The earlier failed run is retained
below as part of the diagnosis. This did not execute a real model workload.

The database-enabled software suite passed 193 tests and failed its PostgreSQL
integration check with a connection timeout. Docker's Linux engine pipe was absent.
Docker Desktop 4.53.0.211793 failed before the database started. This is an
infrastructure failure, not evidence that the new span-ID model protocol failed.

The user supplied an Inference manager error: Docker could not remove its
`dockerInference` runtime socket. Local inspection found a zero-byte reparse-point
file dated September 16 in `%LOCALAPPDATA%/Docker/run`. The directory contained only
that file and `userAnalyticsOtlpHttp.sock`, also zero bytes. Docker processes were
stopped and only the `docker-desktop` WSL distribution was terminated. Renaming the
individual socket still failed with a Windows accessibility error.

The runtime directory was preserved under a sibling backup name and an empty
replacement was created. Docker then reached a second error: the secrets-engine
`engine.sock` socket was inaccessible. That directory was inspected and contained
only the zero-byte socket. It was also preserved and replaced. The intervening
restart recreated an inaccessible inference socket, so a final recovery attempt
refreshed both socket locations while Docker was stopped before starting once.

These observations match firsthand reports in Docker's issue tracker:
[inference socket startup failure](https://github.com/docker/desktop-feedback/issues/448)
and [failures across inference and secrets-engine sockets](https://github.com/docker/desktop-feedback/issues/531).
Those reports support the stale-socket diagnosis, not a guarantee of recovery or
proof of the Windows kernel mechanism on this machine.

Preserved local runtime backups:

- `%LOCALAPPDATA%/Docker/run.stale-evidencebench-20260924`
- `%LOCALAPPDATA%/Docker/run.stale-evidencebench-20260924-2`
- `%LOCALAPPDATA%/docker-secrets-engine.stale-evidencebench-20260924`

Each directory's resolved source/destination and zero-byte socket-only contents
were checked before renaming. No recursive deletion, factory reset, Docker upgrade,
settings change, disk-image operation, database-volume operation or model-cache
operation was performed. Other WSL distributions were not terminated. The backups
are deliberately retained, outside Git. No model training or evaluation was run.
