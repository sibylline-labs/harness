# Route the Finding, Don't Record It

> **Playbook for** [`route-the-finding-dont-record-it.md`](~/.claude/rules/route-the-finding-dont-record-it.md): the resident core carries the statement, trigger and red flags; this file is the full body.

**A finding is discharged only when it reaches the actor who will close it (you, if it sits inside
your own deliverable; the owning channel, if it does not) and never by being written down.**

## Pattern

Handling a finding has two halves. Describing it is cheap, satisfying, and produces an artifact.
Delivering it to someone who acts is a separate step with a different cost. Every container an agent
writes into holds a description perfectly: a plan's out-of-scope row, a risk table, a `NOTE:` comment,
a commit message, a PR body, a tracker comment, a handover list, a retro, a ticket. **None of them
acts.** Each is either unread, read only by someone who has already reached the defect, or read by a
queue that drops what it cannot absorb. The better the description, the more completely the
obligation feels discharged, so the failure is strongest in exactly the most careful work.

That is why this family keeps minting rules: the *container* changes with every incident, and each new
container looks like a new lesson. It is one substitution. The containers that have stood in for
delivery:

- a plan's "pre-existing and left untouched" row (the defect then lived for months);
- a commit message plus a `NOTE:` comment;
- a tracker comment saying "raise if you want these filed";
- a handover list saying "say the word and I'll file them";
- a filed ticket nobody opened (created and last-updated timestamps equal, a real dollar cost);
- a retro naming a rule file that was never written (several retros, several absent rules);
- a chip filed for a defect shipped in the same release.

The cases *look* like they contradict each other: file by default; don't flood a queue you've measured
as full; file without asking; don't file, fix it yourself. They don't. They are one routing decision
keyed on **who the actor is**:

| The finding is… | Actor | Route | Discharged when |
|---|---|---|---|
| A defect inside the thing you are producing right now | You | Fix it in this pass | Fixed and verified |
| A defect in your own tooling / harness | Its maintainer | Its reporting channel (`eris yak`), same turn, no permission | A receipt id exists |
| A finding in a class a peer owner has just claimed or sequenced ("I'll carve it; don't file") | That owner | A message to the owner naming the finding; file nothing yourself. The claim covers the class, not only the noun it names | The owner says where it goes |
| An adjacent defect in someone else's priority space | The priority owner | A ticket through `/linear-workflow`, queue depth visible | The ID is cited where the prose was, and the *risk* closes only when its control runs |
| A scope, priority, or policy choice | The human | One line with options, then stop | A decision is made |
| Nobody obvious | Unknown | Ask who owns it | An owner is named |

The only question legitimately handed back is the last row. "Shall I file these?" is the second or
third row misrouted to the fourth.

## The surfaces

| Surface | The sentence applied there |
|---|---|
| adjacent defects found mid-change | the actor is its priority owner's queue, not your diff, and a wrap-up instruction routes the remainder there immediately |
| declined defects in plans, risk tables, comments | a deferral sentence reaches no actor; the ticket ID it cites does |
| handovers and completion reports | a finding listed for the human's permission is written down, not routed: file first, report receipts |
| asking the human for a step only they can take (token, secret, dashboard setting) | an ask the human must research before acting is not yet routed: it carries the links, scopes and commands up front |
| defects in your own tooling | the actor is the harness's own channel, and routing there needs no permission |
| merging a delegated loop's PR under a merge grant | CI says the code passed; only the open asks and the hand-back say whether the grant covers the PR, and an open ask or unrouted hand-back question dies at the merge unless routed first |
| the tracker queue | a ticket reaches a queue, not an actor; discharge is the control running, which needs someone with capacity |

## Applying it on a new surface

1. **Name the finding's actor before writing anything about it.** Walk the routing table top to bottom
   and stop at the first row that fits. Row one wins ties: a defect inside your deliverable is never
   "adjacent".
2. **Find the actor's inbox and confirm something polls it.** A tool's `--help`, the team's tracker,
   the human in chat. A document, a comment, or a retro has no poller: if that is the only place the
   finding would land, you have not found the inbox yet.
3. **Route first, describe second.** The description then *cites* the delivery (`see ABC-123`, a yak
   receipt id) instead of standing in for it.
4. **Ask the discharge question of every item before you stop:** *who holds this after I stop typing,
   and will they see it without re-reading what I wrote?* "Me" means unfinished. "Nobody" means it was
   deleted politely.
5. **Record the route, not just the finding.** A report of the shape *filed (with ids) / fixed / yours
   to decide* is checkable; a findings list is not.

## Red Flags — class level

- A finding you are not fixing appears in something you wrote and no ID, receipt, or commit sits on
  the same line.
- You are writing "out of scope", "pre-existing", "deferred", "raise if you want", "say the word",
  "let me know", or "worth a follow-up".
- The container you are about to put a finding in is archived on merge, read once at review, or has no
  reader at all.
- Your report's findings list has one bucket.
- A retro, plan, or comment names an artifact (a rule file, a ticket, a test) in the present tense and
  you have not checked that it exists.
- The more carefully you are explaining a defect, the less you are planning to do about it.
- You filed a ticket about the artifact you are still actively producing.

## Related

A named gap is not a closed gap: the same substitution applies to **verification evidence**, which
belongs to [`ask-what-the-check-could-not-see.md`](~/.claude/rules/ask-what-the-check-could-not-see.md).
