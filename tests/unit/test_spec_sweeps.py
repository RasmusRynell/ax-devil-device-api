"""Sweeps over every generated API: anonymous operations and secret fields.

These guard the specs, not one API: a new spec that documents an anonymous
operation without ``auth: if_challenged``, or a credential field without
``x-masked``, fails here.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from ax_devil_device_api._protocols.base import Model
from ax_devil_device_api.features.registry import load_all

ENTRIES = load_all()


def _models(module: Any) -> list[type[Model]]:
    return [
        v for v in vars(module).values() if isinstance(v, type) and issubclass(v, Model) and v.__module__ == module.__name__
    ]


def test_anonymous_operations_do_not_send_credentials_first() -> None:
    offenders = []
    for entry in ENTRIES:
        for name, op in entry.operations.items():
            if op.access != "anonymous":
                continue
            auth = getattr(op.binding, "auth", "required")
            negotiation = getattr(op.binding, "negotiation", None)
            neg_auth = getattr(negotiation, "auth", None)
            if auth != "if_challenged" or (negotiation is not None and neg_auth not in (None, "if_challenged")):
                offenders.append(f"{entry.name}.{name}: auth={auth!r}")
    assert not offenders


@pytest.mark.parametrize("api", ["api_discovery", "systemready", "basic_device_info"])
def test_json_rpc_version_negotiation_of_anonymous_apis_is_challenge_only(api: str) -> None:
    entry = next(e for e in ENTRIES if e.name == api)
    for name, op in entry.operations.items():
        negotiation = getattr(op.binding, "negotiation", None)
        assert getattr(negotiation, "auth", None) == "if_challenged", f"{api}.{name}"


_SECRET_NAME = re.compile(
    r"(?i)^(.*pass(word|phrase|wd)|pwd|pass|(old|new)?pin|puk|psk|.*secret|.*community|.*private_?key|.*srtp_?key|.*pkcs12|.*pfx|oak|license_?key|.*mka_?cak)$"
)
# Payload fields that carry key material or secrets are recognised by their description as well.
_SECRET_TEXT = re.compile(r"(?i)pkcs ?#?12|\bpfx\b|private key|\bpassword\b|owner authentication key|\bsecret\b|\bCAK\b")
_NOT_SECRET_TEXT = re.compile(r"(?i)\b(public|whether|identifies?|ids?|name|token|chain)\b|^$")
# Not secret values despite the name: counters, flags, policies, lengths.
_NOT_A_VALUE = re.compile(r"(?i)(retries|length|timeout|set|policy|complexity|enabled|keep_existing|required)$")


def test_credential_fields_are_masked() -> None:
    offenders = []
    for entry in ENTRIES:
        module = __import__(entry.sync_class.__module__, fromlist=["x"])
        for model in _models(module):
            for name, field in model.model_fields.items():
                alias = field.alias or name
                text = field.description or ""
                by_text = bool(_SECRET_TEXT.search(text)) and not _NOT_SECRET_TEXT.search(text)
                if not (_SECRET_NAME.match(name) or _SECRET_NAME.match(alias) or by_text):
                    continue
                if _NOT_A_VALUE.search(name) or "str" not in repr(field.annotation):
                    continue
                if name not in model.__masked__:
                    offenders.append(f"{entry.name}: {model.__name__}.{name}")
    assert not offenders, offenders


@pytest.mark.parametrize("operation", ["change_sim_pin", "set_sim_protection", "unblock_sim", "verify_sim_pin"])
def test_sim_pin_and_puk_are_masked(operation: str) -> None:
    entry = next(e for e in ENTRIES if e.name == "network_settings")
    params = entry.operations[operation].params
    assert params is not None
    secrets = {n for n in params.model_fields if re.fullmatch(r"(old|new)?(pin|puk)", n)}
    assert secrets and secrets <= params.__masked__
