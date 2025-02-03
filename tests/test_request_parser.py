import pytest

from gamehub.core.event_bus import EventBus
from gamehub.core.events.join_game import JoinGameById, JoinGameByType, RejoinGame
from gamehub.core.events.make_move import MakeMove
from gamehub.core.events.outgoing_message import OutgoingMessage
from gamehub.core.events.query_rooms import QueryRooms
from gamehub.core.events.request import Request, RequestType
from gamehub.core.message import MessageType
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
            QueryRooms,
            RejoinGame,
        ):
            event_bus.subscribe(event_type, events.append)
        await parser.parse_request(request)
        return events

    return _output_events


@pytest.mark.asyncio
async def test_request_parser_returns_error_message_if_bad_request(output_events):
    request = Request(
        player_id="Ana",
        request_type=RequestType.JOIN_GAME_BY_ID,
        payload={"bad_key": 1},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0].player_id == "Ana"
    assert output_events[0].message.message_type == MessageType.ERROR
    assert "bad_key" in output_events[0].message.payload["error"]


@pytest.mark.asyncio
async def test_request_parser_raises_join_game_by_id_event(output_events):
    request = Request(
        player_id="Ana",
        request_type=RequestType.JOIN_GAME_BY_ID,
        payload={"room_id": 123},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == JoinGameById(player_id="Ana", room_id=123)


@pytest.mark.asyncio
async def test_request_parser_raises_rejoin_game_event(output_events):
    request = Request(
        player_id="Ana",
        request_type=RequestType.REJOIN_GAME,
        payload={"room_id": 123},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == RejoinGame(player_id="Ana", room_id=123)


@pytest.mark.asyncio
async def test_request_parser_raises_join_game_by_type_event(output_events):
    request = Request(
        player_id="Ana",
        request_type=RequestType.JOIN_GAME_BY_TYPE,
        payload={"game_type": "tic_tac_toe"},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == JoinGameByType(player_id="Ana", game_type="tic_tac_toe")


@pytest.mark.asyncio
async def test_request_parser_raises_make_move_event(output_events):
    request = Request(
        player_id="Ana",
        request_type=RequestType.MAKE_MOVE,
        payload={"room_id": 123, "move": {"mock": "move"}},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == MakeMove(
        player_id="Ana", room_id=123, move={"mock": "move"}
    )


@pytest.mark.asyncio
async def test_request_parser_raises_query_rooms_event(output_events):
    request = Request(
        player_id="Ana",
        request_type=RequestType.QUERY_ROOMS,
        payload={"game_type": "tic_tac_toe"},
    )
    output_events = await output_events(request)
    assert len(output_events) == 1
    assert output_events[0] == QueryRooms(player_id="Ana", game_type="tic_tac_toe")
