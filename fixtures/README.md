# Pre-recorded model output

The opening hook is the only moment in Session 01 that touches a model. It has one
job — to fail memorably — and it must not depend on the network, or on the shared
inference budget being resolved.

`opening-hook.md` holds the transcript. **It ships as a placeholder and must be
recorded before the session**; the placeholder shows the required shape and must
not be read to the room as a real response.

WHY a fixture rather than a live call: a hook that does not run is a hook that does
not land, and the point being made is about confident wrongness, not about latency.
