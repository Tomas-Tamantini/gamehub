class GameRoom:
    @property
    def room_id(self) -> int:
        raise NotImplementedError()

    async def join(self, player_id: str) -> None:
        raise NotImplementedError()
