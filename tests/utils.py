from dataclasses import dataclass

from gamehub.core.message import MessageEvent, MessageType


@dataclass(frozen=True)
class ExpectedBroadcast:
    recipients: list[str]
    message_type: MessageType
    payload: dict

    def check_messages(self, messages: list[MessageEvent]) -> None:
        assert all(m.message.message_type == self.message_type for m in messages)
        assert all(m.message.payload == self.payload for m in messages)
        assert [m.player_id for m in messages] == self.recipients


def check_messages(
    messages: list[MessageEvent], expected_broadcasts: list[ExpectedBroadcast]
) -> None:
    current_idx = 0
    for expected in expected_broadcasts:
        expected.check_messages(
            messages[current_idx : current_idx + len(expected.recipients)]
        )
        current_idx += len(expected.recipients)

    assert current_idx == len(messages)
