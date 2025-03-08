def calculate_credits(points: dict[str, int], credits_per_point: int) -> dict[str, int]:
    creds = {player: pts * credits_per_point for player, pts in points.items()}
    total_creds = sum(creds.values())
    remainder = total_creds % len(creds)
    if remainder > 0:
        sorted_players = sorted(creds, key=creds.get)
        for i in range(len(creds) - remainder):
            creds[sorted_players[i]] += 1
            total_creds += 1
    avg = total_creds // len(creds)
    return {player: avg - creds[player] for player in creds}
