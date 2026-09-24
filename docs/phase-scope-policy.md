# Phase scope correction

The shared recipe policy is injected at the public MCP response boundary for
refinement, start, continue, review, acceptance and feature completion.

Planning/documentation and initial/final checkpoint phases declare both assessment
flags false. This does not cancel explicit checkpoint commands or waive failures.
Test-only work has no production review; it executes assigned tests and assesses
the production behavior those tests must prove. Explicit production coverage stays
assigned, without measuring coverage of the tests themselves.

When correcting a mixed planning phase, move executable fixture work to a named
implementation/test owner before dependent changes. Retain stable task/criterion
identities, failed evidence, command obligations and an audited before/after
contract. The policy does not exempt phase numbers or mark artifacts accepted.

Validation: `cd DevCycleManager && python -m unittest discover` exercises all six
public recipe boundaries with phase identifiers 1 and 17. These tests verify
policy delivery; they cannot guarantee a client's LLM follows every instruction.
