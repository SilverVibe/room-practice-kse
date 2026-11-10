from booking.models import Room, Reservation
from booking.rules import validate

ROOMS = [Room(id="R1", name="소회의실 A", capacity=4, floor=3)]


def make(**kw):
    base = dict(id=1, room_id="R1", title="회의", booker="김민수", team="기획팀", phone="",
                date="2026-11-10", start="10:00", end="11:00", attendees=3)
    base.update(kw)
    return Reservation(**base)


def test_정상_예약은_통과한다():
    assert validate(make(), ROOMS, []) == []


def test_없는_회의실은_막는다():
    assert "없는 회의실입니다: R9" in validate(make(room_id="R9"), ROOMS, [])


def test_끝이_시작보다_빠르면_막는다():
    errors = validate(make(start="11:00", end="10:00"), ROOMS, [])
    assert "끝나는 시간은 시작 시간보다 늦어야 합니다." in errors


def test_운영_시간_전에_시작하면_막는다():
    errors = validate(make(start="08:00", end="09:00"), ROOMS, [])
    assert "운영 시간(09:00~18:00) 밖입니다." in errors


def test_겹치는_예약은_막고_예약_정보를_표시한다():
    existing = make(id=2)
    errors = validate(make(start="10:30", end="11:30"), ROOMS, [existing])
    assert errors == [
        "이미 예약된 시간입니다 (예약 번호: 2, 시간: 10:00~11:00)"
    ]


def test_끝과_시작이_맞닿는_예약은_통과한다():
    errors = validate(make(start="11:00", end="12:00"), ROOMS, [make(id=2)])
    assert errors == []


def test_다른_회의실의_같은_시간_예약은_통과한다():
    other_room = make(id=2, room_id="R2")
    errors = validate(make(), ROOMS, [other_room])
    assert errors == []


def test_다른_날짜의_같은_시간_예약은_통과한다():
    other_date = make(id=2, date="2026-11-11")
    errors = validate(make(), ROOMS, [other_date])
    assert errors == []


def test_기존_예약을_완전히_감싸는_예약은_막는다():
    errors = validate(make(start="09:30", end="11:30"), ROOMS, [make(id=2)])
    assert "이미 예약된 시간입니다 (예약 번호: 2, 시간: 10:00~11:00)" in errors


def test_같은_id의_예약은_비교에서_제외한다():
    errors = validate(make(), ROOMS, [make()])
    assert errors == []


def test_정원을_넘는_예약은_막는다():
    errors = validate(make(attendees=5), ROOMS, [])
    assert "정원을 넘었습니다" in errors


def test_정원과_같은_인원은_통과한다():
    errors = validate(make(attendees=4), ROOMS, [])
    assert errors == []
