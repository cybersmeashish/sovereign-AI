from datetime import datetime, timedelta, timezone
import pytest
from sovereign_ai.policy_bundle import BundleRejected, PolicyBundle, PolicyStore
from sovereign_ai.signing import HMACSigner

S = HMACSigner(b"k")
NOW = datetime(2026, 11, 3, tzinfo=timezone.utc)


def bundle(v, days=30, revoked=()):
    return PolicyBundle("site-a", v, (NOW - timedelta(days=1)).isoformat(), (NOW + timedelta(days=days)).isoformat(),
                        "0.1.0", {"placement": "package x"}, list(revoked)).sign(S)


def test_install_and_offline_expiry_fail_closed():
    st = PolicyStore(S); st.install(bundle(1), NOW)
    assert st.enforceable(NOW)
    assert not st.enforceable(NOW + timedelta(days=31))


def test_rejects_tamper_replay_revoked():
    st = PolicyStore(S); st.install(bundle(2), NOW)
    b = bundle(3); b.policies["placement"] = "evil"
    with pytest.raises(BundleRejected): st.install(b, NOW)
    with pytest.raises(BundleRejected): st.install(bundle(1), NOW)
    st.install(bundle(4, revoked=[5]), NOW)
    with pytest.raises(BundleRejected): st.install(bundle(5), NOW)


def test_wrong_key():
    with pytest.raises(BundleRejected):
        PolicyStore(HMACSigner(b"other")).install(bundle(1), NOW)
