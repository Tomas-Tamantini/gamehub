import pytest

from gamehub.games.chinese_poker.hand import hand_value


@pytest.mark.parametrize(
    "bad_hand",
    [
        "2c 3d",
        "",
        "3d 4d 5d 6d 7d 8d",
        "As Ac Ad Ah",
        "3d 4d 5d 7d 8s",
        "Kc Ac 2c 3c 4d",
        "3d 3h 4d 4h 5c",
        "Jc Qd Kc Ac 2c",
    ],
)
def test_hand_value_raises_value_error_if_invalid_hand(bad_hand, parse_hand):
    with pytest.raises(ValueError, match="Invalid hand"):
        hand_value(parse_hand(bad_hand))


@pytest.mark.parametrize(
    ("hand_a", "hand_b"),
    [
        ("Ah", "As"),
        ("3d", "2c"),
        ("3d 3s", "3c 3h"),
        ("As Ac", "2d 2h"),
        ("Jd Js Jc", "Qd Qs Qc"),
        ("2c 2s 2h Ac As", "3d 3h 3c 3s 4d"),
        ("2c 2s Kh Kc Ks", "3d 3h Ac As Ad"),
        ("3d 4s 5c 6h 7d", "4d 5s 6c 7h 8d"),
        ("2c Ac Kc Qc Tc", "2d Ad Kd Qd Jd"),
        ("5c 4c 3c 2c As", "6d 5d 4d 3d 2h"),
        ("Th Jc Qd Kc Ac", "3d 4c 4s 4h 4d"),
        ("9h Tc Jd Qc Kc", "Th Jc Qd Kc Ac"),
        ("4h 4c 4s 4d 5d", "3d 4d 5d 6d 7d"),
    ],
)
def test_hand_value_allows_comparison_between_hands(hand_a, hand_b, parse_hand):
    assert hand_value(parse_hand(hand_a)) < hand_value(parse_hand(hand_b))
