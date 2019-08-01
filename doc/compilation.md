# Compilation

Sylva compiles code in multiple phases.

## Phase 1

Phase 1 builds a tree of all modules.  No references are resolved; i.e.
schemas/functions that reference non-existent schemas won't be detected here.

## Phase 2

Phase 2 resolves all references, which can require multiple passes.

## Phase 3

Phase 3 validates all checks.

## Phase 4

Phase 4 generates code.
