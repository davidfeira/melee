# Local p@h Cluster

Docker-based permuter@home cluster for distributing permuter runs across LAN machines. Used by `permute.py diff --auto-permute --cluster`.

Read `tools/pah/README.md` before touching anything here.

## Images

- `melee-pah-controller:local` — controller image
- `melee-pah-worker:local` — worker image

## State

- Local controller state: `build-linux/pah-controller-state/`
- Root `pah.conf` — gitignored, contains p@h secret material

## Worker setup

**LAN worker bootstrap:**
1. On the controller PC: `tools/pah/serve-worker-kit.ps1`
2. Run the printed one-liner on the worker laptop

**Local WSL worker:** `tools/pah/start-wsl-worker.ps1`

> Windows-native p@h workers currently fail on Docker Desktop named pipes. Use the WSL worker script for local workers.

## Docker Desktop bind mount quirk

The vendored p@h worker maps WSL `/mnt/c/...` source bind mounts to Docker Desktop's `/run/desktop/mnt/host/c/...` path when needed.

## Hard-stop

- Never stop a p@h worker, controller, or distributed client you did not launch.
