"""Exercise the PSX game-code registry and the Api game-codes facade."""

from rom_manager.api_client import Api
from rom_manager.game_codes import psx_codes


def test_psx_codes_nonempty_dict():
    assert isinstance(psx_codes, dict)
    assert len(psx_codes) > 0


def test_lookup_known_code():
    code = next(iter(psx_codes))
    result = Api.lookup_game_code(code)
    assert result["code"] == code
    assert result["name"] == psx_codes[code]


def test_lookup_unknown_code():
    result = Api.lookup_game_code("DOES-NOT-EXIST-0000")
    assert result["name"] is None


def test_list_all_game_codes():
    listed = Api.list_game_codes()
    assert listed == dict(psx_codes)


def test_list_game_codes_with_prefix():
    sample_code = next(iter(psx_codes))
    prefix = sample_code[:4]
    filtered = Api.list_game_codes(prefix=prefix)
    assert filtered  # at least the sample matches
    assert all(k.startswith(prefix) for k in filtered)
