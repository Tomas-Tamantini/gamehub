def calculate_credits(points: dict[str, int]) -> dict[str, int]:
    total_points = sum(points.values())
    remainder = total_points % len(points)
    if remainder > 0:
        sorted_winners = sorted(points, key=points.get)
        for i in range(len(points) - remainder):
            points[sorted_winners[i]] += 1
            total_points += 1
    avg = total_points // len(points)
    return {player: avg - points[player] for player in points}
