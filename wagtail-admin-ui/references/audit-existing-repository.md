# Audit an existing Wagtail repository

Use this workflow only for a repository-wide compliance or alignment request.
Use the native admin checklist as the rule set. The audit is complete when every
discovered custom admin surface has a disposition and every finding has evidence
and a proposed validation method.

## Establish scope and standard

Read the repository instructions and capture:

- the exact Wagtail version and any pending upgrade target;
- project-owned admin conventions, supported devices, themes, languages, and
  accessibility requirements;
- applications and packages included in the audit; and
- existing worktree changes, so user work is not mistaken for an audit finding
  or overwritten during later remediation.

Use the installed version's generic views, templates, component source, and
tests as the comparison standard. Pair each custom surface with the closest
built-in analogue. Record a documented project convention as an intentional
exception only when it still meets the workflow, accessibility, responsive, and
security outcomes in the checklist.

## Inventory every custom admin surface

Search the full application scope, honoring repository ignores. Build an
inventory from all of these entry points:

- `wagtail_hooks.py` modules and registrations for admin URLs, viewsets, menu
  items, CSS, JavaScript, reports, bulk actions, and chooser behavior;
- `SnippetViewSet`, `ModelViewSet`, `ChooserViewSet`, base `ViewSet`, generic
  admin view subclasses, and standalone registered Django views;
- custom template prefixes and templates extending or overriding
  `wagtailadmin/*`, including full pages, result fragments, confirmation pages,
  modals, and shared partials;
- panels, admin model forms, table/column classes, button components, permission
  policies, and message calls;
- project-owned admin CSS, JavaScript, Stimulus controllers, icons, and template
  tags; and
- route, view, browser, screenshot, accessibility, and permission tests covering
  those surfaces.

Follow references from registrations to their view, form, template, assets, and
tests. Include screens reachable only through row menus, object actions, bulk
actions, chooser modals, or permission-specific navigation. Consolidate shared
partials as one implementation source while listing every screen they affect.

Create an inventory table with:

| Surface | Route or entry point | Kind | Implementation | Native analogue | Coverage | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| People list | `people:index` | Listing | view/template paths | Snippet listing | tests or none | Pending |

Do not stop at the first violations. Every discovered surface must end as
**pass**, **violation**, **intentional exception**, or **unverified**.

## Static compliance pass

Apply every relevant section of the native admin checklist. In particular,
inspect for:

- a custom page bypassing viewsets or generic views without a workflow reason;
- complete template replacement where a view property, component, or small
  block override would work;
- missing or duplicate page titles, headings, icons, slim headers, or breadcrumb
  trails;
- raw, obsolete, or hand-styled buttons in place of current Wagtail components;
- crowded header actions, missing `header_more_buttons`, or unlabeled dots and
  row-action menus;
- custom tables missing native columns, accessible row identity, sorting,
  filtering, pagination, counts, bulk semantics, or distinct empty states;
- read-only detail values rendered as disabled form controls;
- editable list, detail, create, or edit screens without native fields, widget
  media, validation behavior, unsaved-change handling, or sticky save actions;
- state changes over GET, missing CSRF, divergent endpoint and button permission
  rules, or incomplete destructive confirmations;
- headers or controls incorrectly placed inside replaceable result fragments;
- custom chooser/modal behavior that loses native focus, keyboard, loading, or
  selection semantics;
- feedback that is silent, color-only, ephemeral, or inconsistent with Wagtail
  messages and progress controls;
- CSS that hard-codes colors or physical direction, assumes unavailable utility
  classes, breaks dark/forced-color themes, or broadly overrides Wagtail; and
- missing coverage for permissions, invalid submissions, fragments, responsive
  layout, keyboard access, and materially different visual states.

Static patterns are leads, not automatic verdicts. Read the surrounding code
and exact installed-version API before reporting a violation.

## Rendered behavior pass

When the repository can run safely, render every custom full-page surface at
least once with an appropriate authorized user. Exercise modal-only and
permission-only entry points too. For each surface, inspect the relevant states:

- populated, empty, filtered-empty, invalid, success, protected, and loading;
- narrow phone and wide desktop widths;
- long object names, action labels, breadcrumbs, help, and error text;
- keyboard-only operation and visible focus; and
- light/dark theme, zoom, RTL, and forced colors when supported.

Prioritize runtime checks for overflow menus, sticky footers, dropdown clipping,
AJAX updates, validation focus, chooser focus return, and mobile keyboards.
Capture current evidence according to repository policy. If the application,
data, credentials, or environment prevents a runtime check, mark the surface
**unverified** and state the missing evidence. Do not convert inability to render
into a pass or a confirmed visual failure.

## Write evidence-based findings

Assign stable finding IDs such as `WAI-001`. Each finding contains:

- severity: **critical**, **high**, **medium**, or **low**;
- confidence: **confirmed** or **probable**;
- affected screen or shared component;
- violated checklist outcome;
- exact source and/or rendered evidence;
- user impact, including mobile, keyboard, permission, or upgrade impact;
- the smallest native Wagtail remediation; and
- how the remediation will be verified.

Use severity consistently:

- **critical**: unauthorized access or mutation, data-loss risk, or an unusable
  primary workflow for a class of users;
- **high**: inaccessible or mobile-blocked primary action, unsafe HTTP behavior,
  hidden validation, or installed-version incompatibility;
- **medium**: substantial native-pattern inconsistency, missing navigation or
  feedback, fragile extension boundary, or recurring responsive defect; and
- **low**: bounded polish or consistency issue with a clear checklist basis.

Do not report subjective taste as a violation. Mark a plausible issue
**probable** until source, rendered behavior, or a test confirms it. Combine
findings with one shared root cause, but list every affected surface so the
fix-all scope is complete.

## Warn, summarize, and offer remediation

Present the audit before editing UI code. The report must contain:

1. audited Wagtail version, application scope, and runtime limits;
2. inventory totals by pass, violation, intentional exception, and unverified;
3. confirmed findings ordered by severity;
4. probable findings and the evidence needed to decide them;
5. the proposed fix-all scope, including shared roots, affected screens, likely
   files, migrations or compatibility risks, and validation; and
6. explicit exclusions such as intentional exceptions or unrelated dirty work.

End with a direct approval question, for example:

> I found 8 confirmed violations across 5 admin surfaces. Do you want me to fix
> all 8, or only selected finding IDs?

An audit request authorizes inspection and reporting, not remediation. Do not
change application UI, tests, or dependencies until the user approves fix-all
or named findings. Temporary read-only evidence artifacts may be created in the
repository's normal scratch location when allowed.

## Remediate an approved audit

After approval:

- recheck the worktree and preserve unrelated changes;
- fix shared view, template, or component roots before individual symptoms;
- use the shallowest native extension supported by the installed Wagtail
  version;
- keep each finding traceable through implementation and validation;
- add or update behavioral tests rather than wording-only assertions;
- capture fresh mobile and desktop proof for changed UI; and
- rerun the inventory and both audit passes at the final head.

Close with a finding ledger: **fixed**, **not reproduced**, **intentional
exception**, or **blocked**, plus evidence for every original finding. “Fix all”
is complete only when no approved confirmed finding is silently left unresolved.
