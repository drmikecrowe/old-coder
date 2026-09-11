# SPEC - probe fixture

Not a real spec. This file exists so the positive control has something inside
the scope to read. If the reviewer can quote the marker below, the hook allowed
a Read inside the scoped directory.

Marker: PROBE-ALLOW-OK-8831

## Orientation

- **Change:** nothing. This is a fixture.
- **Why:** a hook proven only to deny is not proven. A handler that denied
  every Read would pass the negative control perfectly.

## Scenarios

```gherkin
Feature: the fixture is readable
  Scenario: the reviewer reads its own spec
    Given the artifact root's scope pointer names this directory
    When  the reviewer reads SPEC.md
    Then  it can quote the marker
```
