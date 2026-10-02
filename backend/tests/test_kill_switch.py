import pytest
from app.core.kill_switch import KillSwitch


@pytest.mark.asyncio
async def test_kill_switch_activate():
    ks = KillSwitch()
    assert ks.is_active is False

    await ks.activate("test reason")
    assert ks.is_active is True
    assert ks.reason == "test reason"
    assert ks.activated_at is not None


@pytest.mark.asyncio
async def test_kill_switch_deactivate():
    ks = KillSwitch()
    await ks.activate("test")
    assert ks.is_active is True

    await ks.deactivate()
    assert ks.is_active is False
    assert ks.reason == ""


@pytest.mark.asyncio
async def test_kill_switch_check_raises():
    from app.core.exceptions import KillSwitchActiveError
    ks = KillSwitch()
    await ks.activate("test")

    with pytest.raises(KillSwitchActiveError):
        await ks.check()
