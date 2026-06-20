"""Tests for the event hooks system (src/core/event_bus.py)."""

from __future__ import annotations

import pytest

from src.core.event_bus import (
    EVENT_AGENT_ACT,
    EVENT_AGENT_HEAL,
    EVENT_AGENT_OBSERVE,
    EVENT_AGENT_PLAN,
    EVENT_AGENT_STEP,
    EVENT_AGENT_TASK,
    EVENT_BROWSER_CLOSE,
    EVENT_BROWSER_LAUNCH,
    EVENT_CLICK,
    EVENT_FILL,
    EVENT_GO_BACK,
    EVENT_GO_FORWARD,
    EVENT_GOTO,
    EVENT_RELOAD,
    EVENT_SCREENSHOT,
    EVENT_SCRIPT_EXECUTE,
    EVENT_SMART_CLICK,
    EVENT_SMART_FILL,
    Event,
    EventBus,
    Phase,
    get_event_bus,
    reset_event_bus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_bus():
    """Reset the global bus before and after each test."""
    reset_event_bus()
    yield
    reset_event_bus()


@pytest.fixture()
def bus() -> EventBus:
    return EventBus()


# ---------------------------------------------------------------------------
# Event data class
# ---------------------------------------------------------------------------


class TestEvent:
    def test_defaults(self):
        event = Event(name="test", phase=Phase.BEFORE)
        assert event.name == "test"
        assert event.phase == Phase.BEFORE
        assert event.data == {}
        assert event.result is None
        assert event.error is None
        assert event.cancelled is False
        assert event.metadata == {}
        assert isinstance(event.timestamp, float)

    def test_cancel(self):
        event = Event(name="test", phase=Phase.BEFORE)
        assert event.cancelled is False
        event.cancel("not allowed")
        assert event.cancelled is True
        assert event.metadata["cancel_reason"] == "not allowed"

    def test_cancel_without_reason(self):
        event = Event(name="test", phase=Phase.BEFORE)
        event.cancel()
        assert event.cancelled is True
        assert "cancel_reason" not in event.metadata

    def test_data_mutable_from_outside(self):
        event = Event(name="test", phase=Phase.BEFORE, data={"key": "original"})
        event.data["key"] = "mutated"
        assert event.data["key"] == "mutated"

    def test_metadata_mutable_from_outside(self):
        event = Event(name="test", phase=Phase.BEFORE)
        event.metadata["custom"] = 123
        assert event.metadata["custom"] == 123

    def test_result_settable(self):
        event = Event(name="test", phase=Phase.AFTER)
        event.result = {"status": 200}
        assert event.result == {"status": 200}

    def test_error_settable(self):
        event = Event(name="test", phase=Phase.AFTER)
        exc = RuntimeError("fail")
        event.error = exc
        assert event.error is exc

    def test_custom_timestamp(self):
        event = Event(name="test", phase=Phase.BEFORE, timestamp=12345.0)
        assert event.timestamp == 12345.0

    def test_multiple_cancels_last_reason_wins(self):
        event = Event(name="test", phase=Phase.BEFORE)
        event.cancel("first")
        event.cancel("second")
        assert event.metadata["cancel_reason"] == "second"


# ---------------------------------------------------------------------------
# Phase enum
# ---------------------------------------------------------------------------


class TestPhase:
    def test_before_value(self):
        assert Phase.BEFORE.value == "before"

    def test_after_value(self):
        assert Phase.AFTER.value == "after"

    def test_construct_from_string(self):
        assert Phase("before") == Phase.BEFORE
        assert Phase("after") == Phase.AFTER

    def test_is_string_subclass(self):
        assert isinstance(Phase.BEFORE, str)
        assert Phase.BEFORE == "before"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestRegistration:
    def test_on_decorator(self, bus: EventBus):
        calls = []

        @bus.on("my_event", phase="before")
        def handler(event: Event):
            calls.append(event)

        assert bus.hook_count("my_event") == 1
        bus.emit(Event(name="my_event", phase=Phase.BEFORE))
        assert len(calls) == 1

    def test_on_after_phase(self, bus: EventBus):
        calls = []

        @bus.on("my_event", phase="after")
        def handler(event: Event):
            calls.append(event)

        bus.emit(Event(name="my_event", phase=Phase.BEFORE))
        assert len(calls) == 0

        bus.emit(Event(name="my_event", phase=Phase.AFTER))
        assert len(calls) == 1

    def test_on_with_phase_enum(self, bus: EventBus):
        calls = []

        @bus.on("e", phase=Phase.AFTER)
        def handler(event: Event):
            calls.append(event)

        bus.emit(Event(name="e", phase=Phase.AFTER))
        assert len(calls) == 1

    def test_on_returns_undecorated_function(self, bus: EventBus):
        def handler(event: Event):
            pass

        result = bus.on("e")(handler)
        assert result is handler

    def test_register_imperative(self, bus: EventBus):
        calls = []
        cb = bus.register("my_event", lambda e: calls.append(e), phase="after")
        assert bus.hook_count("my_event") == 1
        bus.emit(Event(name="my_event", phase=Phase.AFTER))
        assert len(calls) == 1

    def test_register_returns_callback(self, bus: EventBus):
        def handler(event: Event):
            pass

        returned = bus.register("e", handler)
        assert returned is handler

    def test_register_with_phase_enum(self, bus: EventBus):
        calls = []
        bus.register("e", lambda e: calls.append(e), phase=Phase.BEFORE)
        bus.emit(Event(name="e", phase=Phase.BEFORE))
        assert len(calls) == 1

    def test_once(self, bus: EventBus):
        calls = []
        bus.once("my_event", lambda e: calls.append(e))
        bus.emit(Event(name="my_event", phase=Phase.AFTER))
        bus.emit(Event(name="my_event", phase=Phase.AFTER))
        assert len(calls) == 1
        assert bus.hook_count("my_event") == 0

    def test_once_before_phase(self, bus: EventBus):
        calls = []
        bus.once("e", lambda e: calls.append(e), phase="before")
        bus.emit(Event(name="e", phase=Phase.BEFORE))
        bus.emit(Event(name="e", phase=Phase.BEFORE))
        assert len(calls) == 1
        assert bus.hook_count("e") == 0

    def test_once_with_phase_enum(self, bus: EventBus):
        calls = []
        bus.once("e", lambda e: calls.append(e), phase=Phase.AFTER)
        bus.emit(Event(name="e", phase=Phase.AFTER))
        assert len(calls) == 1

    def test_unregister(self, bus: EventBus):
        calls = []

        def handler(event: Event):
            calls.append(event)

        bus.register("my_event", handler)
        assert bus.hook_count("my_event") == 1

        removed = bus.unregister("my_event", handler)
        assert removed is True
        assert bus.hook_count("my_event") == 0

        bus.emit(Event(name="my_event", phase=Phase.AFTER))
        assert len(calls) == 0

    def test_unregister_nonexistent(self, bus: EventBus):
        assert bus.unregister("nope", lambda e: None) is False

    def test_unregister_wrong_callback(self, bus: EventBus):
        bus.register("e", lambda e: None)
        result = bus.unregister("e", lambda e: None)  # different object
        assert result is False
        assert bus.hook_count("e") == 1

    def test_clear_specific_event(self, bus: EventBus):
        bus.register("a", lambda e: None)
        bus.register("b", lambda e: None)
        bus.clear("a")
        assert bus.hook_count("a") == 0
        assert bus.hook_count("b") == 1

    def test_clear_all(self, bus: EventBus):
        bus.register("a", lambda e: None)
        bus.register("b", lambda e: None)
        bus.clear()
        assert bus.hook_count() == 0

    def test_clear_nonexistent_event(self, bus: EventBus):
        bus.clear("does_not_exist")  # should not raise


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------


class TestPriority:
    def test_hooks_fire_in_priority_order(self, bus: EventBus):
        order = []
        bus.register("e", lambda e: order.append("low"), phase="after", priority=10)
        bus.register("e", lambda e: order.append("high"), phase="after", priority=1)
        bus.register("e", lambda e: order.append("mid"), phase="after", priority=5)
        bus.emit(Event(name="e", phase=Phase.AFTER))
        assert order == ["high", "mid", "low"]

    def test_same_priority_maintains_insertion_order(self, bus: EventBus):
        order = []
        bus.register("e", lambda e: order.append("first"), phase="after", priority=0)
        bus.register("e", lambda e: order.append("second"), phase="after", priority=0)
        bus.register("e", lambda e: order.append("third"), phase="after", priority=0)
        bus.emit(Event(name="e", phase=Phase.AFTER))
        assert order == ["first", "second", "third"]

    def test_priority_default_is_zero(self, bus: EventBus):
        order = []
        bus.register("e", lambda e: order.append("default"), phase="after")
        bus.register("e", lambda e: order.append("explicit"), phase="after", priority=0)
        bus.emit(Event(name="e", phase=Phase.AFTER))
        # Both have priority 0, insertion order preserved
        assert order == ["default", "explicit"]

    def test_negative_priority(self, bus: EventBus):
        order = []
        bus.register("e", lambda e: order.append("normal"), phase="after", priority=5)
        bus.register("e", lambda e: order.append("urgent"), phase="after", priority=-10)
        bus.emit(Event(name="e", phase=Phase.AFTER))
        assert order == ["urgent", "normal"]


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


class TestDispatch:
    def test_emit_returns_event(self, bus: EventBus):
        event = Event(name="e", phase=Phase.BEFORE)
        result = bus.emit(event)
        assert result is event

    def test_before_hook_can_modify_data(self, bus: EventBus):
        def rewrite(event: Event):
            event.data["url"] = "https://modified.com"

        bus.register("navigate", rewrite, phase="before")
        event = Event(name="navigate", phase=Phase.BEFORE, data={"url": "https://original.com"})
        bus.emit(event)
        assert event.data["url"] == "https://modified.com"

    def test_before_hook_can_cancel(self, bus: EventBus):
        def blocker(event: Event):
            event.cancel("blocked")

        bus.register("navigate", blocker, phase="before")
        event = Event(name="navigate", phase=Phase.BEFORE)
        bus.emit(event)
        assert event.cancelled is True

    def test_hook_error_does_not_propagate(self, bus: EventBus):
        def bad_hook(event: Event):
            raise RuntimeError("boom")

        bus.register("e", bad_hook, phase="after")
        event = Event(name="e", phase=Phase.AFTER)
        bus.emit(event)  # Should not raise
        assert "hook_errors" in event.metadata

    def test_hook_error_recorded_in_metadata(self, bus: EventBus):
        def bad_hook(event: Event):
            raise ValueError("bad value")

        bus.register("e", bad_hook, phase="after")
        event = Event(name="e", phase=Phase.AFTER)
        bus.emit(event)

        errors = event.metadata["hook_errors"]
        assert len(errors) == 1
        assert "bad value" in errors[0]["error"]

    def test_multiple_hook_errors_all_recorded(self, bus: EventBus):
        def bad1(event: Event):
            raise RuntimeError("err1")

        def bad2(event: Event):
            raise RuntimeError("err2")

        bus.register("e", bad1, phase="after")
        bus.register("e", bad2, phase="after")
        event = Event(name="e", phase=Phase.AFTER)
        bus.emit(event)

        errors = event.metadata["hook_errors"]
        assert len(errors) == 2

    def test_no_hooks_is_noop(self, bus: EventBus):
        event = Event(name="nonexistent", phase=Phase.BEFORE)
        bus.emit(event)  # Should not raise

    def test_only_matching_phase_hooks_fire(self, bus: EventBus):
        before_calls = []
        after_calls = []

        bus.register("e", lambda e: before_calls.append(1), phase="before")
        bus.register("e", lambda e: after_calls.append(1), phase="after")

        event = Event(name="e", phase=Phase.AFTER)
        bus.emit(event)

        assert len(before_calls) == 0
        assert len(after_calls) == 1

    def test_multiple_hooks_all_fire(self, bus: EventBus):
        calls = []
        bus.register("e", lambda e: calls.append("a"), phase="after")
        bus.register("e", lambda e: calls.append("b"), phase="after")
        bus.register("e", lambda e: calls.append("c"), phase="after")
        bus.emit(Event(name="e", phase=Phase.AFTER))
        assert calls == ["a", "b", "c"]

    def test_emit_does_not_mutate_original_data(self, bus: EventBus):
        """Emit should not make a defensive copy; hooks mutate the event in-place."""
        original = {"key": "value"}

        def modifier(event: Event):
            event.data["key"] = "changed"

        bus.register("e", modifier, phase="before")
        event = Event(name="e", phase=Phase.BEFORE, data=original)
        bus.emit(event)

        # The event's data dict is the same object
        assert event.data is original
        assert original["key"] == "changed"


# ---------------------------------------------------------------------------
# Introspection
# ---------------------------------------------------------------------------


class TestIntrospection:
    def test_list_events(self, bus: EventBus):
        bus.register("b", lambda e: None)
        bus.register("a", lambda e: None)
        bus.register("c", lambda e: None)
        assert bus.list_events() == ["a", "b", "c"]

    def test_list_events_empty(self, bus: EventBus):
        assert bus.list_events() == []

    def test_hook_count_all(self, bus: EventBus):
        bus.register("a", lambda e: None)
        bus.register("a", lambda e: None)
        bus.register("b", lambda e: None)
        assert bus.hook_count() == 3

    def test_hook_count_specific(self, bus: EventBus):
        bus.register("a", lambda e: None)
        bus.register("a", lambda e: None)
        bus.register("b", lambda e: None)
        assert bus.hook_count("a") == 2
        assert bus.hook_count("b") == 1
        assert bus.hook_count("c") == 0

    def test_hook_count_all_empty(self, bus: EventBus):
        assert bus.hook_count() == 0


# ---------------------------------------------------------------------------
# Lifecycle context manager
# ---------------------------------------------------------------------------


class TestLifecycle:
    def test_lifecycle_emits_before_and_after(self, bus: EventBus):
        phases_seen = []

        def tracker(event: Event):
            phases_seen.append(event.phase)

        bus.register("my_action", tracker, phase="before")
        bus.register("my_action", tracker, phase="after")

        with bus.lifecycle("my_action", {"key": "value"}) as event:
            assert phases_seen == [Phase.BEFORE]
            assert event.data["key"] == "value"

        assert phases_seen == [Phase.BEFORE, Phase.AFTER]

    def test_lifecycle_captures_result(self, bus: EventBus):
        results = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                results.append(event.result)

        bus.register("my_action", capture, phase="after")

        with bus.lifecycle("my_action") as event:
            event.result = "done"

        assert results == ["done"]

    def test_lifecycle_captures_error(self, bus: EventBus):
        errors = []

        def capture(event: Event):
            if event.phase == Phase.AFTER and event.error:
                errors.append(str(event.error))

        bus.register("my_action", capture, phase="after")

        with pytest.raises(ValueError, match="oops"):
            with bus.lifecycle("my_action"):
                raise ValueError("oops")

        assert len(errors) == 1
        assert "oops" in errors[0]

    def test_lifecycle_cancel_skips_body(self, bus: EventBus):
        body_ran = False

        def blocker(event: Event):
            event.cancel("nope")

        bus.register("my_action", blocker, phase="before")

        with bus.lifecycle("my_action"):
            body_ran = True

        # Body still runs (Python context manager), but the event is cancelled
        assert body_ran is True

    def test_lifecycle_cancelled_emits_after_with_metadata(self, bus: EventBus):
        after_events = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                after_events.append(event)

        def blocker(event: Event):
            event.cancel("blocked")

        bus.register("my_action", blocker, phase="before")
        bus.register("my_action", capture, phase="after")

        with bus.lifecycle("my_action"):
            pass

        assert len(after_events) == 1
        assert after_events[0].metadata.get("cancelled") is True

    def test_lifecycle_cancel_reason_preserved(self, bus: EventBus):
        after_events = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                after_events.append(event)

        def blocker(event: Event):
            event.cancel("security violation")

        bus.register("my_action", blocker, phase="before")
        bus.register("my_action", capture, phase="after")

        with bus.lifecycle("my_action"):
            pass

        assert after_events[0].metadata.get("cancel_reason") == "security violation"

    def test_lifecycle_without_data(self, bus: EventBus):
        phases = []

        def tracker(event: Event):
            phases.append(event.phase)
            assert event.data == {}

        bus.register("e", tracker, phase="before")
        bus.register("e", tracker, phase="after")

        with bus.lifecycle("e"):
            pass

        assert phases == [Phase.BEFORE, Phase.AFTER]

    def test_lifecycle_data_copied_not_shared(self, bus: EventBus):
        """The before event's data dict should be a copy of the input, not the same object."""
        original = {"key": "value"}
        captured_data = []

        def capture(event: Event):
            captured_data.append(event.data)

        bus.register("e", capture, phase="before")

        with bus.lifecycle("e", original):
            pass

        # The lifecycle makes a copy of the input data
        assert captured_data[0] is not original
        assert captured_data[0] == original

    def test_lifecycle_duration_in_after_metadata(self, bus: EventBus):
        after_events = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                after_events.append(event)

        bus.register("e", capture, phase="after")

        with bus.lifecycle("e"):
            pass

        assert "duration_ms" in after_events[0].metadata
        assert after_events[0].metadata["duration_ms"] >= 0

    def test_lifecycle_error_still_emits_after(self, bus: EventBus):
        after_events = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                after_events.append(event)

        bus.register("e", capture, phase="after")

        with pytest.raises(RuntimeError):
            with bus.lifecycle("e"):
                raise RuntimeError("fail")

        assert len(after_events) == 1
        assert after_events[0].error is not None

    def test_lifecycle_before_event_data_mutable_in_body(self, bus: EventBus):
        after_events = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                after_events.append(event)

        bus.register("e", capture, phase="after")

        with bus.lifecycle("e", {"original": True}) as event:
            event.data["added_in_body"] = True

        # The after event should see the mutations (same data dict)
        assert after_events[0].data.get("added_in_body") is True

    def test_lifecycle_result_carried_from_before_to_after(self, bus: EventBus):
        after_events = []

        def capture(event: Event):
            if event.phase == Phase.AFTER:
                after_events.append(event)

        bus.register("e", capture, phase="after")

        with bus.lifecycle("e") as event:
            event.result = "from_before"

        assert after_events[0].result == "from_before"


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_event_bus_returns_same_instance(self):
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2

    def test_reset_event_bus_clears_hooks(self):
        bus = get_event_bus()
        bus.register("x", lambda e: None)
        assert bus.hook_count() == 1
        reset_event_bus()
        new_bus = get_event_bus()
        assert new_bus.hook_count() == 0
        assert new_bus is not bus

    def test_reset_event_bus_safe_when_none(self):
        reset_event_bus()  # no instance exists, should not raise
        reset_event_bus()  # call again

    def test_get_after_reset_creates_new(self):
        bus1 = get_event_bus()
        reset_event_bus()
        bus2 = get_event_bus()
        assert bus1 is not bus2


# ---------------------------------------------------------------------------
# Event name constants
# ---------------------------------------------------------------------------


class TestEventConstants:
    ALL_BROWSER_CONSTANTS = [
        EVENT_BROWSER_LAUNCH,
        EVENT_BROWSER_CLOSE,
        EVENT_GOTO,
        EVENT_GO_BACK,
        EVENT_GO_FORWARD,
        EVENT_RELOAD,
        EVENT_CLICK,
        EVENT_FILL,
        EVENT_SMART_CLICK,
        EVENT_SMART_FILL,
        EVENT_SCREENSHOT,
        EVENT_SCRIPT_EXECUTE,
    ]

    ALL_AGENT_CONSTANTS = [
        EVENT_AGENT_STEP,
        EVENT_AGENT_TASK,
        EVENT_AGENT_OBSERVE,
        EVENT_AGENT_PLAN,
        EVENT_AGENT_ACT,
        EVENT_AGENT_HEAL,
    ]

    def test_all_browser_constants_are_strings(self):
        for c in self.ALL_BROWSER_CONSTANTS:
            assert isinstance(c, str), f"{c!r} is not a string"

    def test_all_agent_constants_are_strings(self):
        for c in self.ALL_AGENT_CONSTANTS:
            assert isinstance(c, str), f"{c!r} is not a string"

    def test_all_constants_unique(self):
        all_consts = self.ALL_BROWSER_CONSTANTS + self.ALL_AGENT_CONSTANTS
        assert len(all_consts) == len(set(all_consts))

    def test_phase_enum(self):
        assert Phase.BEFORE.value == "before"
        assert Phase.AFTER.value == "after"
        assert Phase("before") == Phase.BEFORE

    def test_browser_launch_value(self):
        assert EVENT_BROWSER_LAUNCH == "browser_launch"

    def test_browser_close_value(self):
        assert EVENT_BROWSER_CLOSE == "browser_close"

    def test_navigate_value(self):
        assert EVENT_GOTO == "navigate"

    def test_click_value(self):
        assert EVENT_CLICK == "click"

    def test_fill_value(self):
        assert EVENT_FILL == "fill"

    def test_screenshot_value(self):
        assert EVENT_SCREENSHOT == "screenshot"

    def test_script_execute_value(self):
        assert EVENT_SCRIPT_EXECUTE == "script_execute"
