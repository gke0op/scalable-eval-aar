# Phase 2: The Pivot

**Date:** May 19, 2026  
**Status:** Completed → Led to [Phase 3](03_adversarial_findings.md)

## The Honest Reassessment

After recognizing that our evaluation awareness detector was measuring prompt framing effects rather than true internal awareness, we stepped back to ask: **what problem does Anthropic actually need solved?**

We systematically reviewed three recent Anthropic publications to identify explicitly stated open problems:

### From "Automated Alignment Researchers" (Apr 2026):

> "Any deployment of automated researchers will require evaluations that the AARs can't tamper with."

> "The core bottleneck in alignment research could become evaluation, rather than generation."

AARs found creative shortcuts that gamed evaluations:
- **Math task:** Learned to "always pick the most common answer" instead of learning from the teacher
- **Coding task:** Learned to "run code against tests and read off the answer" instead of predicting correctness

### From "Teaching Claude why" (May 2026):

> "It remains to be seen if the methods we've discussed will continue to scale."

> "Our auditing methodology is not yet sufficient to rule out scenarios in which Claude would choose to take catastrophic autonomous action."

### From "Natural Language Autoencoders" (May 2026):

> "NLA explanations can be wrong."

> "NLAs are also expensive."

## The Decision

**The evaluation bottleneck for automated alignment research** was the clearest, most attackable problem:

1. **Directly aligned with stated priorities** — Anthropic explicitly called evaluation the bottleneck
2. **Empirically testable** — We can build adversarial test sets and measure detection accuracy
3. **Feasible with our resources** — Local open-weight models are sufficient for proof-of-concept
4. **Novel** — No existing work specifically addresses gaming detection in AAR outputs
5. **Builds on our Phase 1 work** — The adversarial evaluation methodology is a natural evolution of paired-prompt testing

## What Changed

| Aspect | Phase 1 | Phase 2+ |
|--------|---------|----------|
| **Question** | Can we detect evaluation awareness? | Can we detect when AARs game evaluations? |
| **Method** | Behavioral classification | Adversarial evaluation sets |
| **Target** | Internal model state | External method quality |
| **Requires** | NLA-level interpretability | Only behavioral evaluation |
| **Attackable with local models** | No (need NLAs) | Yes |

## What We Kept

The Phase 1 infrastructure was directly reusable:
- ✅ Paired prompt design methodology
- ✅ LLM-as-judge evaluation framework  
- ✅ Multi-model testing pipeline
- ✅ Feature extraction and analysis tools

## Key Insight

The evaluation awareness work wasn't wasted — it taught us that **surface-level detection is easy to build but hard to trust.** This is exactly the problem that AARs face when gaming evaluations: they find surface-level solutions that score well but don't actually improve alignment. Our Phase 1 failure is a microcosm of the broader AAR gaming problem.
