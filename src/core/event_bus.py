"""
Event hooks system for agentic-playwright-mcp.

Provides a centralized EventBus for registering lifecycle hooks on browser
actions.  Hooks fire before and after key operations (navigate, click, fill,
screenshot, script execution, etc.), enabling observability, custom logging,
analytics, and middleware-style interception.

Usage:
    from src.core.event_bus import get_event_bus, Event

    bus = get_event_bus()

    # Register a hook that logs every navigation
    @bus.on("navigate", phase="after")
    def log_nav(event: Event):
        print(f"Navigated to {event.data['url']} -> {event.result}")

    # Register a hook that validates selectors before clicking
    @bus.on("click", phase="before")
    def validate_click(event: Event):
        if not event.data.get("selector_list"):
            raise ValueError("Empty selector list")

    # One-shot hook (fires once then auto-removes)
    bus.once("browser_launch", lambda e: print("Browser ready!"))
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generator
from contextlib import contextmanager

from src.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Event names — canonical constants
# ---------------------------------------------------------------------------

# Browser lifecycle
EVENT_BROWSER_LAUNCH = "browser_launch"
EVENT_BROWSER_CLOSE = "browser_close"

# Navigation
EVENT_GOTO = "navigate"
EVENT_GO_BACK = "go_back"
EVENT_GO_FORWARD = "go_forward"
EVENT_RELOAD = "reload"

# Element interaction
EVENT_CLICK = "click"
EVENT_FILL = "fill"

# Smart operations (Layer 2)
EVENT_SMART_CLICK = "smart_click"
EVENT_SMART_FILL = "smart_fill"

# Screenshot
EVENT_SCREENSHOT = "screenshot"

# Script execution
EVENT_SCRIPT_EXECUTE = "script_execute"

# Agent loop
EVENT_AGENT_STEP = "agent_step"
EVENT_AGENT_TASK = "agent_task"
EVENT_AGENT_OBSERVE = "agent_observe"
EVENT_AGENT_PLAN = "agent_plan"
EVENT_AGENT_ACT = "agent_act"
EVENT_AGENT_HEAL = "agent_heal"


class Phase(str, Enum):
    """Hook execution phase."""
    BEFORE = "before"
    AFTER = "after"


# ---------------------------------------------------------------------------
# Event data class
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """Represents a single event passing through the hook system.

    Attributes:
        name: Event name (use EVENT_* constants).
        phase: Whether this is a before or after hook.
        data: Mutable dict of event parameters.  ``before`` hooks may modify
              this to alter the action (e.g. rewrite a selector).
        result: Populated for ``after`` hooks with the action's return value.
        error: Populated for ``after`` hooks when the action raised.
        timestamp: Unix timestamp when the event was created.
        cancelled: If a ``before`` hook sets this to True, the action is
                   skipped (the caller checks this flag).
        metadata: Free-form metadata that hooks can stash for downstream
                  consumption (e.g. timing info, correlation IDs).
    """

    name: str
    phase: Phase
    data: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Exception | None = None
    timestamp: float = field(default_factory=time.time)
    cancelled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def cancel(self, reason: str = "") -> None:
        """Cancel the action (only meaningful in ``before`` hooks).

        Args:
            reason: Optional human-readable cancellation reason.  Stored in
                    ``self.metadata["cancel_reason"]``.
        """
        self.cancelled = True
        if reason:
            self.metadata["cancel_reason"] = reason


# ---------------------------------------------------------------------------
# Hook entry (internal)
# ---------------------------------------------------------------------------


@dataclass
class _HookEntry:
    """Internal bookkeeping for a registered hook."""
    callback: Callable[[Event], None]
    phase: Phase
    priority: int = 0
    once: bool = False


# ---------------------------------------------------------------------------
# EventBus
# ---------------------------------------------------------------------------


class EventBus:
    """Central event hook registry and dispatcher.

    Thread-safety note: the current implementation uses plain dicts and is
    safe for single-threaded MCP stdio usage.  If multi-threaded access is
    needed later, add a ``threading.Lock`` around ``_hooks`` mutations.
    """

    def __init__(self) -> None:
        # {event_name: [_HookEntry, ...]}
        self._hooks: dict[str, list[_HookEntry]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def on(
        self,
        event_name: str,
        *,
        phase: str | Phase = Phase.BEFORE,
        priority: int = 0,
    ) -> Callable:
        """Decorator to register a hook for an event.

        Args:
            event_name: Event to listen for (use EVENT_* constants).
            phase: ``"before"`` or ``"after"``.
            priority: Lower values fire first (default 0).

        Returns:
            Decorator that registers the function and returns it unchanged.
        """
        phase_enum = Phase(phase) if isinstance(phase, str) else phase

        def decorator(fn: Callable[[Event], None]) -> Callable[[Event], None]:
            self._add_hook(event_name, _HookEntry(
                callback=fn,
                phase=phase_enum,
                priority=priority,
                once=False,
            ))
            return fn

        return decorator

    def once(
        self,
        event_name: str,
        callback: Callable[[Event], None],
        *,
        phase: str | Phase = Phase.AFTER,
        priority: int = 0,
    ) -> None:
        """Register a one-shot hook that auto-removes after its first firing.

        Args:
            event_name: Event to listen for.
            callback: Hook function.
            phase: ``"before"`` or ``"after"``.
            priority: Lower values fire first.
        """
        phase_enum = Phase(phase) if isinstance(phase, str) else phase
        self._add_hook(event_name, _HookEntry(
            callback=callback,
            phase=phase_enum,
            priority=priority,
            once=True,
        ))

    def register(
        self,
        event_name: str,
        callback: Callable[[Event], None],
        *,
        phase: str | Phase = Phase.AFTER,
        priority: int = 0,
    ) -> Callable[[Event], None]:
        """Imperatively register a hook.  Returns the callback for easy
        removal via :meth:`unregister`.

        Args:
            event_name: Event name.
            callback: Hook function.
            phase: ``"before"`` or ``"after"``.
            priority: Lower values fire first.

        Returns:
            The callback (so callers can pass it to ``unregister`` later).
        """
        phase_enum = Phase(phase) if isinstance(phase, str) else phase
        self._add_hook(event_name, _HookEntry(
            callback=callback,
            phase=phase_enum,
            priority=priority,
            once=False,
        ))
        return callback

    def unregister(
        self,
        event_name: str,
        callback: Callable[[Event], None],
    ) -> bool:
        """Remove a previously registered hook.

        Args:
            event_name: Event the hook was registered on.
            callback: The exact function object passed to ``register`` or
                      decorated with ``@on``.

        Returns:
            True if the hook was found and removed, False otherwise.
        """
        entries = self._hooks.get(event_name)
        if not entries:
            return False
        before = len(entries)
        entries[:] = [e for e in entries if e.callback is not callback]
        return len(entries) < before

    def clear(self, event_name: str | None = None) -> None:
        """Remove all hooks, optionally scoped to a single event.

        Args:
            event_name: If given, clear only this event's hooks.  Otherwise
                        clear everything.
        """
        if event_name is None:
            self._hooks.clear()
        else:
            self._hooks.pop(event_name, None)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def emit(self, event: Event) -> Event:
        """Run all hooks for the event's name and phase.

        Hooks are executed in priority order (lowest first).  If a ``before``
        hook sets ``event.cancelled = True``, subsequent hooks still fire but
        the caller should check ``event.cancelled`` to decide whether to
        proceed.

        Args:
            event: The Event to dispatch.

        Returns:
            The same Event instance (mutated by hooks).
        """
        entries = self._hooks.get(event.name, [])
        to_remove: list[_HookEntry] = []

        for entry in entries:
            if entry.phase != event.phase:
                continue
            try:
                entry.callback(event)
            except Exception as exc:
                logger.warning(
                    "Hook error on %s/%s: %s",
                    event.name,
                    event.phase.value,
                    exc,
                    extra={
                        "event": event.name,
                        "phase": event.phase.value,
                        "error": str(exc),
                    },
                )
                # Attach error info but don't propagate — hooks are observers
                event.metadata.setdefault("hook_errors", []).append({
                    "callback": entry.callback.__qualname__,
                    "error": str(exc),
                })

            if entry.once:
                to_remove.append(entry)

        # Clean up one-shot hooks
        if to_remove:
            hook_list = self._hooks.get(event.name, [])
            for entry in to_remove:
                try:
                    hook_list.remove(entry)
                except ValueError:
                    pass

        return event

    # ------------------------------------------------------------------
    # Convenience context manager
    # ------------------------------------------------------------------

    @contextmanager
    def lifecycle(
        self,
        event_name: str,
        data: dict[str, Any] | None = None,
    ) -> Generator[Event, None, None]:
        """Context manager that emits ``before`` and ``after`` events
        automatically, including timing and error capture.

        Args:
            event_name: Event name.
            data: Initial event data.

        Yields:
            The ``before`` Event (hooks may have modified ``event.data``).

        Usage:
            with bus.lifecycle("navigate", {"url": url}) as event:
                page.goto(event.data["url"])
                event.result = page.url
        """
        before_event = Event(
            name=event_name,
            phase=Phase.BEFORE,
            data=dict(data) if data else {},
        )
        self.emit(before_event)

        if before_event.cancelled:
            reason = before_event.metadata.get("cancel_reason", "cancelled by hook")
            logger.info("Event %s cancelled: %s", event_name, reason)
            # Emit after event with cancellation info
            after_event = Event(
                name=event_name,
                phase=Phase.AFTER,
                data=before_event.data,
                metadata={**before_event.metadata, "cancelled": True},
            )
            self.emit(after_event)
            yield before_event
            return

        start = time.monotonic()
        after_event = Event(
            name=event_name,
            phase=Phase.AFTER,
            data=before_event.data,
            metadata=dict(before_event.metadata),
        )

        try:
            yield before_event
        except Exception as exc:
            after_event.error = exc
            raise
        finally:
            duration_ms = (time.monotonic() - start) * 1000
            after_event.metadata["duration_ms"] = round(duration_ms, 2)
            # Carry over result if the caller set it on before_event
            if before_event.result is not None and after_event.result is None:
                after_event.result = before_event.result
            self.emit(after_event)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_events(self) -> list[str]:
        """Return sorted list of event names that have registered hooks."""
        return sorted(self._hooks.keys())

    def hook_count(self, event_name: str | None = None) -> int:
        """Count registered hooks.

        Args:
            event_name: If given, count hooks for that event.  Otherwise
                        count all hooks.

        Returns:
            Number of registered hooks.
        """
        if event_name is not None:
            return len(self._hooks.get(event_name, []))
        return sum(len(entries) for entries in self._hooks.values())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add_hook(self, event_name: str, entry: _HookEntry) -> None:
        """Insert a hook entry, maintaining priority sort order."""
        if event_name not in self._hooks:
            self._hooks[event_name] = []
        entries = self._hooks[event_name]
        entries.append(entry)
        entries.sort(key=lambda e: e.priority)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_instance: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global singleton EventBus.

    Returns:
        The shared EventBus instance.
    """
    global _instance
    if _instance is None:
        _instance = EventBus()
    return _instance


def reset_event_bus() -> None:
    """Reset the global singleton (for testing).

    Clears all hooks and replaces the instance.
    """
    global _instance
    if _instance is not None:
        _instance.clear()
    _instance = None
