---
name: wagtail-admin-ui
description: "Build, review, or align custom Wagtail administration interfaces so they look and behave like native Wagtail admin. Use for ModelViewSet, SnippetViewSet, custom admin views, reports, choosers, and templates, including repository-wide audits for inconsistent headers, breadcrumbs, buttons, responsive actions, listings, detail pages, forms, or sticky save actions. Do not use for public-facing site design or ordinary Django admin pages."
---

# Wagtail Admin UI

Make custom admin work feel like part of the installed Wagtail version. Prefer
Wagtail's viewsets, generic views, components, panels, tables, and interaction
patterns over copied markup or a parallel design system.

Read [references/admin-ui-checklist.md](references/admin-ui-checklist.md) before
implementing or reviewing a custom admin interface. For a repository-wide audit
or alignment request, also read
[references/audit-existing-repository.md](references/audit-existing-repository.md).

## Establish the local contract

Read the repository instructions and determine:

- the exact installed or locked Wagtail version;
- the project's supported browsers and accessibility requirements;
- existing custom-admin conventions, shared templates, tests, and asset
  pipeline; and
- the nearest built-in Wagtail screen with the same job.

Inspect the generic views, templates, Python components, and tests shipped by
that exact Wagtail version when an extension point is unclear. Treat current
official versioned documentation and source as authoritative. Wagtail's base
template HTML and CSS internals are not a stable API, so never copy an example
from another version without checking it locally.

## Audit an existing repository

When asked to check, align, standardize, or modernize an existing Wagtail admin,
inventory every custom admin surface and run the repository audit workflow.
Account for each discovered surface as compliant, a confirmed violation, an
intentional exception, or unverified. Findings must name the affected screen and
give concrete file, line, rendered, or test evidence.

Treat audit and remediation as separate phases. Warn the user about confirmed
violations before changing the UI. Present a fix-all scope with affected areas,
risks, and validation, then explicitly offer to fix every confirmed violation or
a selected subset. Make remediation changes only after the user approves them.

## Choose the shallowest native extension

Use the highest-level primitive that fits:

1. a registered snippet or `SnippetViewSet`;
2. `ModelViewSet` for model list/create/edit/delete/inspect workflows;
3. Wagtail generic view classes and `WagtailAdminTemplateMixin`;
4. a custom `ViewSet` grouping custom views; or
5. a plain registered Django admin view only when the earlier options do not
   express the workflow.

Configure viewset attributes and override view methods before replacing
templates. If a template override is necessary, extend the nearest generic
template and override the smallest documented block. Keep result fragments
separate from page furniture so search, filtering, and pagination updates do
not erase the header or controls.

## Compose the native interface

Build the page from Wagtail primitives:

- supply one page title, an icon from the registered icon set, and a meaningful
  root-to-current breadcrumb trail through the generic admin shell;
- put the single frequent action in the header and secondary or destructive
  actions in Wagtail's overflow mechanism;
- use `HeaderButton`, `Button`, `ListingButton`, `ButtonWithDropdown`, table
  components, and the `dropdown` template tags available in the installed
  version instead of hand-styled approximations;
- use Wagtail panels or `WagtailAdminModelForm` for model forms and preserve
  widget media;
- keep save and related submission actions in the native sticky form footer on
  every long editable page, including editable list or detail screens; and
- use Wagtail messages, confirmation pages, permission checks, and POST/CSRF
  semantics for state changes.

Do not add a save footer to a read-only detail screen or pure listing. Do not
create separate mobile-only action markup when Wagtail's header button and
overflow APIs can provide the responsive behavior.

## Verify behavior, not just resemblance

Test permissions, success and invalid-form paths, query-string preservation,
empty and populated states, and asynchronous result refreshes. Exercise the UI
with keyboard-only navigation and automated accessibility checks where the
project supports them.

Inspect current rendered pages at narrow mobile and wide desktop widths. Check
light and dark themes, zoom, forced-colors when practical, long and translated
labels, and RTL when the project supports it. Confirm that overflow menus remain
reachable and that sticky actions do not hide the last field or validation
message.

When UI changed, provide current visual proof for each materially different
state and viewport required by the repository's delivery rules.
