import pytest
from drive_events import default_drive, EventInput


def test_order():
    @default_drive.make_event
    def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    def b(event: EventInput):
        return 2

    @default_drive.listen_groups([b])
    def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())


def test_multi_send():
    @default_drive.make_event
    def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    def b(event: EventInput):
        return 2

    @default_drive.listen_groups([a])
    def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())


def test_multi_recv():
    @default_drive.make_event
    def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    def a1(event: EventInput):
        return 1

    @default_drive.make_event
    def b(event: EventInput):
        return 2

    @default_drive.listen_groups([a1, b])
    def c(event: EventInput):
        return 3

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())


def test_loop():
    @default_drive.make_event
    def a(event: EventInput):
        return 1

    @default_drive.listen_groups([a])
    def b(event: EventInput):
        return 1

    a = default_drive.listen_groups([b])(a)

    @default_drive.listen_groups([a, b])
    def c(event: EventInput):
        return 1

    print(a.debug_string())
    print(b.debug_string())
    print(c.debug_string())
