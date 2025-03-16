import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.request import Request, RequestType
from gamehub.core.events.request_events import (
    JoinGameById,
    JoinGameByType,
    MakeMove,
    RejoinGame,
    RequestFailed,
    WatchGame,
)
from gamehub.core.request_parser import RequestParser


@pytest.fixture
def output_events():
    async def _output_events(request: Request):
        event_bus = EventBus()
        parser = RequestParser(event_bus)
        events = []
        for event_type in (
            OutgoingMessage,
            JoinGameById,
            MakeMove,
            JoinGameByType,
            RejoinGame,
            WatchGame,
            RequestFailed,
        ):
            event_bus.subscribe(event_type, events.append)
        await parser.parse_request(request)
        return events

    return _output_events


@pytest.mark.asyncio
async def test_request_parser_returns_error_message_if_request_is_not_json(
    output_events,
):
    request = Request(player_id="Ana", raw_request="not json")
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0].player_id == "Ana"
    assert "not json" in output_events[0].error_msg


@pytest.mark.asyncio
async def test_request_parser_returns_error_message_if_bad_request_type(output_events):
    request = Request(player_id="Ana", raw_request='{"request_type": "bad_type"}')
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0].player_id == "Ana"
    assert "validation error" in output_events[0].error_msg


@pytest.mark.asyncio
async def test_request_parser_raises_join_game_by_id_event(
    output_events, build_request
):
    request = build_request(
        player_id="Ana",
        request_type=RequestType.JOIN_GAME_BY_ID,
        payload={"room_id": 123},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == JoinGameById(player_id="Ana", room_id=123)


@pytest.mark.asyncio
async def test_request_parser_raises_rejoin_game_event(output_events, build_request):
    request = build_request(
        player_id="Ana",
        request_type=RequestType.REJOIN_GAME,
        payload={"room_id": 123},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == RejoinGame(player_id="Ana", room_id=123)


@pytest.mark.asyncio
async def test_request_parser_raises_watch_game_event(output_events, build_request):
    request = build_request(
        player_id="Ana",
        request_type=RequestType.WATCH_GAME,
        payload={"room_id": 123},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == WatchGame(player_id="Ana", room_id=123)


@pytest.mark.asyncio
async def test_request_parser_raises_join_game_by_type_event(
    output_events, build_request
):
    request = build_request(
        player_id="Ana",
        request_type=RequestType.JOIN_GAME_BY_TYPE,
        payload={"game_type": "tic_tac_toe"},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == JoinGameByType(player_id="Ana", game_type="tic_tac_toe")


@pytest.mark.asyncio
async def test_request_parser_raises_make_move_event(output_events, build_request):
    request = build_request(
        player_id="Ana",
        request_type=RequestType.MAKE_MOVE,
        payload={"room_id": 123, "move": {"mock": "move"}},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == MakeMove(
        player_id="Ana", room_id=123, move={"mock": "move"}
    )
