# Team Working Agreement — Smart Waste Classification System

This document exists so that when (not if) something slips — a deadline, a merge conflict, a "I thought you were doing that" — you have something to point at instead of having a vague argument. Fill in the bracketed sections before you start coding. An unfilled contract is just a README with extra steps.

**Since this is explicitly a dry run for hackathon collaboration, not a project where the classifier's accuracy matters:** TrashNet is a solved problem — almost any pretrained backbone gets you 90%+ with transfer learning, so don't mistake model tuning for the hard part. Section 3 (PR reviews) and Section 4 (communication) are the actual graded assignment here. Whether the three of you can hit a self-imposed deadline without one person going dark is what transfers to the hackathon. A model that works but was built by three people who never reviewed each other's code is a failed practice run, even if the demo works.

---

## 1. Team & Module Ownership

The project structure in the README already splits cleanly into three lanes. Assign one owner per lane — not "everyone helps with everything," which is how nothing gets finished.

| Owner | Module | Owns |
|---|---|---|
| **[Name 1]** | Data & Preprocessing | `data/`, `src/preprocessing/` — dataset sourcing, cleaning, augmentation pipeline |
| **Ali** | Model Development | `src/models/`, `notebooks/` — transfer learning experiments (PyTorch), training loop, evaluation metrics |
| **[Name 3]** | Application & Quality | `app/`, `src/utils/`, `tests/` — Streamlit interface, integration, test coverage |

**Exception:** `src/utils/config.py` (paths, hyperparameters, class label order) is shared, not owned by Person 3 alone. It's the one file all three modules read from — changes to it need a heads-up to the other two before merging, not just a normal PR. This is the file most likely to cause a silent shape-mismatch bug if someone edits it in isolation.

**Owner ≠ only contributor.** Owner means: final call on design decisions in that module, and the person accountable if it's late or broken at review time.

If you split this by something other than pipeline stage (e.g. by waste category, or by "whoever's strongest at what"), say so explicitly here — don't leave it implied.

---

## 2. Decisions the README Hasn't Made Yet

These are blocking. You cannot assign "Model Development" to someone with a straight face until these are answered:

- [x] **Dataset**: TrashNet
- [x] **Framework**: PyTorch
- [ ] **Base model**: not decided yet ("we'll see" is not a plan, it's a way to burn a week). Time-box it — cap architecture selection at 1–2 days. Try ResNet18, MobileNetV2, and EfficientNet-B0, keep whichever gets a working baseline fastest. Do not let this turn into an open-ended search; a hackathon judge doesn't care that you tried 6 architectures, they care that something worked
- [ ] **Deadline / milestones**: not set. No external deadline means no real pressure, which means this "practice" won't actually simulate hackathon conditions. Self-impose one — a hard 1–2 week end date with a mid-point check-in — or this exercise doesn't build what you're trying to build

Put these answers above the table once you have them, or the module split is guesswork.

---

## 3. Git Workflow

Based on the flow already in your README, made concrete:

- **Branch naming**: `feature/<module>-<short-description>` — e.g. `feature/preprocessing-augmentation`, `feature/model-resnet-baseline`
- **Commits**: small, one logical change each. Message format: `<module>: <what changed>` (e.g. `preprocessing: add rotation augmentation`)
- **Pull requests**: every merge to `main` requires **at least 1 review from a teammate outside that module** — not a self-approve
- **Review turnaround**: reviewer responds within [24h / 48h — pick one]. If you're the reviewer and you're busy, say so instead of going silent — a silent PR is worse than a delayed one
- **`main` stays working.** If your branch breaks the app or the training script, it doesn't merge, no exceptions
- **CI runs on every PR** (`.github/workflows/ci.yml`, running `pytest`). A red CI check blocks merge — this isn't a suggestion layered on top of the review requirement, it's what makes "at least 1 review" mean something instead of a rubber stamp

---

## 4. Communication

- **Standup cadence**: [e.g. async check-in every 2 days in group chat — "what I did / what's next / what's blocking me"]
- **Blockers**: post them the day they happen, not the day before a deadline
- **Missed commitment**: if someone can't hit what they said by when they said it, they flag it 24h ahead — not after

---

## 5. Definition of Done

A module isn't "done" because the code runs once on your machine. Done means:

- Code is merged to `main` via reviewed PR
- Has at least a basic test (in `tests/`) or a documented manual verification
- Doesn't require a teammate to ask "wait, how do I run this?"

---

## 6. Conflict Resolution

- Disagreement on a technical decision (e.g. model architecture): whoever owns that module has final say, after hearing the other two out
- Disagreement on scope/timeline: majority vote, 3 people, no tie
- If someone consistently misses commitments: raise it directly with them first, not around them

---

## Sign-off

By starting work on your assigned module, you're agreeing to the above. Update this file (via PR, like everything else) if the team decides to change any of it — don't just start ignoring it.

| Name | GitHub | Module |
|---|---|---|
| | | |
| | | |
| | | |
