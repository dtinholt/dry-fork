# Scope decision, 21 Oct 2026 (Dinand: build from documentation, buy nothing)

- Deliverable 1: a clean-room engine that reads the DOS Wasteland data formats as documented
  by the community (wastelib docs, wllib as cross-check). Engine code original; no game assets
  anywhere in the repo; no decoded dumps of the game as fixtures.
- Deliverable 2: an original scenario authored by the lab in those same formats, with its own
  maps, tiles, portraits, strings, paragraph book, items and encounters, so the engine is
  playable with no Interplay content.
- Deliverable 3 (after the move): parity against Dinand's own Apple IIe disks once imaged
  (Applesauce or ADTPro), as a separate milestone with its own loader if the formats differ.
- Where the public documentation stops (map action semantics, scripts, combat and skill
  formulas), the spec defines "lab rules v1" explicitly, labelled as non-parity, so the
  builder never guesses silently. Parity on those rules waits for ground truth.
- The build runs unattended on the lab's local model pair through the harness in harness/, under a
  registration (PREREG-W1) that measures what a mid-tier open model achieves per day from a
  frozen spec and acceptance tests, with frontier review at milestones.
