import pytest

from gamehub.games.chinese_poker.credits import calculate_credits


@pytest.mark.parametrize(
    ("points", "expected"),
    [
        ([0, 0], [0, 0]),
        ([10, 10, 10], [0, 0, 0]),
        ([10, 15, 20], [500, 0, -500]),
        ([10, 23, 13, 18], [600, -700, 300, -200]),
    ],
)
def test_credits_are_proportional_to_distance_to_average(points, expected):
    players = ("Alice", "Bob", "Charlie", "Diana")
    points_dict = {player: pts for player, pts in zip(players, points)}
    expected_dict = {player: c for player, c in zip(players, expected)}
    assert expected_dict == calculate_credits(points_dict, credits_per_point=100)


@pytest.mark.parametrize(
    ("points", "expected"),
    [
        ([50, 33, 42], [-8, 8, 0]),
        ([10, 20, 20, 29], [9, 0, 0, -9]),
        ([1230, 1240, 1233, 1242], [6, -4, 3, -5]),
        ([0, 7, 5, 5], [4, -2, -1, -1]),
    ],
)
def test_credits_get_rounded_to_integer(points, expected):
    players = ("Alice", "Bob", "Charlie", "Diana")
    points_dict = {player: pts for player, pts in zip(players, points)}
    expected_dict = {player: c for player, c in zip(players, expected)}
    assert expected_dict == calculate_credits(points_dict, credits_per_point=1)
