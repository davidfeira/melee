"""One-shot helper: read controller priv_seed and derive the public key.

Workers need the controller's `server_public_key` to verify messages from
the controller. We don't want to serve the priv_seed over /kit (it's secret),
so we cache the derived pub_key in pah_config.toml once and the /kit/info
endpoint reads from there.

Usage:
    python tools/pah/derive-pubkey.py
        Reads build-linux/pah-controller-state/pah_config.toml, derives the
        Ed25519 public key from priv_seed, and writes it back as pub_key.

Requires pynacl. If not installed, runs:
    pip install --user pynacl
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "build-linux" / "pah-controller-state" / "pah_config.toml"


def main() -> int:
    try:
        import nacl.signing  # noqa: F401
    except ImportError:
        print("pynacl missing — install with: pip install --user pynacl", file=sys.stderr)
        return 1
    try:
        import toml
    except ImportError:
        print("toml missing — install with: pip install --user toml", file=sys.stderr)
        return 1

    if not CONFIG.exists():
        print(f"controller config not found: {CONFIG}", file=sys.stderr)
        print("run start-controller.ps1 first to initialize the state dir", file=sys.stderr)
        return 2

    data = toml.loads(CONFIG.read_text(encoding="utf-8"))
    priv_seed_hex = data.get("priv_seed")
    if not priv_seed_hex or len(priv_seed_hex) != 64:
        print("priv_seed missing or not 64-hex-chars in pah_config.toml", file=sys.stderr)
        return 3

    import binascii
    from nacl.signing import SigningKey

    seed = binascii.unhexlify(priv_seed_hex)
    sk = SigningKey(seed)
    pub_key_hex = sk.verify_key.encode().hex()

    if data.get("pub_key") == pub_key_hex:
        print(f"pub_key already cached, no change ({pub_key_hex[:16]}...)")
        return 0

    data["pub_key"] = pub_key_hex
    # Re-serialize preserving original key order roughly.
    out_lines = []
    for k, v in data.items():
        if isinstance(v, str):
            out_lines.append(f'{k} = "{v}"')
        else:
            out_lines.append(f"{k} = {v}")
    CONFIG.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"wrote pub_key = {pub_key_hex} -> {CONFIG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
