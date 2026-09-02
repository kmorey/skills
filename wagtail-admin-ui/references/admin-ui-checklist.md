# Native Wagtail admin checklist

Use this reference to plan, implement, or review a custom admin screen. APIs and
template blocks vary between Wagtail releases; verify every named primitive in
the project's installed version before relying on it.

## 1. Preflight

- Resolve the installed Wagtail version from the lockfile or runtime, not from
  memory.
- Locate the closest built-in list, inspect, create, edit, delete, history,
  report, or chooser screen in that version.
- Inspect its view class, template inheritance, context, component objects,
  tests, and responsive behavior.
- Search the application for an existing custom-admin base template or helper.
  Reuse it if it follows the current Wagtail shell.
- Write down the page's primary user goal, primary action, secondary actions,
  destructive actions, permissions, empty state, and error state.

## 2. Select the view architecture

Prefer configuration over custom rendering:

- Use `SnippetViewSet` when the content belongs in Wagtail snippets.
- Use `ModelViewSet` for conventional model management. Configure fields,
  panels, `list_display`, search, filters, ordering, pagination, inspect, copy,
  history, and permission behavior through the viewset where possible.
- Use generic Wagtail index/create/edit/delete/inspect views for a workflow that
  is close to model management but needs custom behavior.
- Use a base `ViewSet` to group related non-model admin views, URL names, menu
  metadata, and icons.
- Register standalone URLs with admin hooks only for genuinely standalone
  workflows. Ensure admin access and object-level permissions explicitly.

Override a view method or component factory before overriding a template.
Override a small template block before replacing a complete template. Avoid
depending on undocumented DOM structure.

## 3. Page shell and information hierarchy

Every full page should have:

- Wagtail's admin base or generic base for navigation, messages, theme, and
  responsive page furniture;
- a useful HTML title through the inherited title mechanism;
- exactly one page-level heading exposed to assistive technology;
- `page_title`, optional `page_subtitle`, and a registered `header_icon` or
  their version-equivalent context;
- standard content width and padding from the closest native analogue; and
- no duplicate legacy header below a slim breadcrumb header.

Use the generic template's shell instead of manually including the header when
possible. If a completely custom template is necessary, match the exact
installed version's documented base blocks. Remember that Wagtail explicitly
does not promise stable base-template HTML.

## 4. Breadcrumbs

- Render breadcrumbs inside Wagtail's current header pattern, not as a second
  strip in the content area.
- Build a short root-to-current trail: admin home or section, collection/list,
  object when applicable, then the current operation.
- Make ancestors links and the current item non-linking. Use concise labels;
  place object names in the label or sublabel according to the native analogue.
- Generate URLs with namespaced `reverse` calls. Preserve locale or relevant
  return state when the built-in view does.
- With `WagtailAdminTemplateMixin`, extend the inherited breadcrumb collection
  rather than mutating shared class data. Use `get_breadcrumbs_items()` when
  breadcrumbs depend on the object or request.
- Do not disable breadcrumbs merely to make a legacy header template easier to
  reuse. Current Wagtail generic listing templates expect breadcrumb context.

## 5. Header actions and responsive overflow

Give the header one obvious frequent action at most, such as **Add**, **Edit**,
or **Run report**. Represent it with the installed version's `HeaderButton` or
equivalent header component.

Place secondary, infrequent, and destructive actions in `header_more_buttons`
or the equivalent component collection. The generic admin mixin turns those
into the native dots overflow menu, including responsive behavior. Keep action
ordering stable and permission-aware.

For template-level menus, use Wagtail's `dropdown` or `dropdown_button` tags.
Their menu content must be interactive `a` or `button` elements. A dots-only
toggle needs an accessible label such as “Actions”; an item-specific row menu
needs a label such as “More options for ‘Quarterly report’”.

Do not:

- duplicate the same action in separate desktop and mobile markup;
- allow five header buttons to wrap or crowd the breadcrumb;
- hide the only way to perform the primary task in an unlabeled menu; or
- place a destructive action beside the primary action with equal emphasis.

## 6. Buttons and mutations

- Use Python button components (`HeaderButton`, `Button`, `ListingButton`, and
  `ButtonWithDropdown`, where available) and render them as components.
- Use a link for navigation and a real button for an in-page command or form
  submission. Never perform a mutation through GET.
- Use the native primary, secondary, warning, and destructive variants from the
  installed version. Do not recreate them with raw colors.
- Give icon-only controls a programmatic label and, where the native component
  supports it, a tooltip. Icons supplement clear text; they do not replace it
  without an accessible name.
- For slow submissions, follow the native long-running/progress-button pattern
  to prevent double submission and announce an active label.
- Keep button text task-oriented and consistent with Wagtail: “Add person”,
  “Save”, “Delete”, “Cancel”, rather than ambiguous “OK” or “Submit”.

Legacy listing-button CSS class recipes are version-sensitive. Newer Wagtail
versions require button component objects rather than removed listing styles.

## 7. Listing and report views

Use Wagtail's generic listing template and `Table`/column components when they
fit. In particular:

- use `TitleColumn` for the row's primary identity and link;
- use native date, boolean, status, user, locale, usage, and ordering columns
  instead of hand-formatting common values;
- give sortable columns an unambiguous accessible sort state and label;
- put row actions in the title/action column and collapse secondary row actions
  into an item-labelled dots menu;
- keep the most useful columns visible at small widths and avoid critical
  information that is only available by horizontal scrolling;
- add search and filters through generic view APIs, with applied state visible;
- preserve search, filters, ordering, and pagination across links and updates;
- report the match count after search/filter changes when the generic view does;
- show a helpful empty state that distinguishes “no objects exist” from “no
  objects match these filters”; and
- use built-in pagination and bulk-action semantics instead of custom checkbox
  behavior.

If bulk checkboxes are present, follow Wagtail table components' screen-reader
association between each checkbox and the row title.

## 8. Detail and inspect views

- Use the generic inspect view for a read-only object where possible.
- Lead with identity and status, then group values into scannable sections.
- Use definition-list or panel semantics from the native analogue; do not fake a
  form with disabled inputs.
- Put **Edit** in the header when it is the frequent next step. Put delete and
  other secondary operations in the labelled overflow menu.
- Format dates, numbers, booleans, relationships, statuses, and empty values
  with native components and localization.
- A read-only detail has no save bar. A detail page containing editable fields
  follows the form rules below and gets the native sticky footer.

## 9. Create, edit, and editable list/detail views

Use panels or a `WagtailAdminModelForm` so model fields receive Wagtail's native
date/time, page, document, image, and snippet widgets. Prefer panel definitions
for layout and field grouping. If rendering fields directly, use Wagtail's
formatted-field helper rather than bare `{{ field }}` output.

Follow the current generic form template's behavior:

- POST with CSRF protection and multipart encoding when required;
- render hidden fields, field help, required state, inline errors, and non-field
  errors accessibly;
- include form and panel media CSS/JS;
- warn before navigation with unsaved changes where supported;
- retain entered values and reveal/focus the error summary or first invalid
  field after a failed submission;
- keep the main **Save** action and related submission choices in Wagtail's
  sticky footer/action menu; and
- leave navigation and object-level commands in the header.

The sticky footer rule applies to any long custom page that submits editable
data, even when the page is called a list or detail view. Verify that the footer
does not cover the final field, inline panel controls, error text, browser zoom
content, or a mobile keyboard viewport. Pure listings and read-only details do
not receive a decorative save footer.

## 10. Delete and other destructive flows

- Require the correct permission and use POST with CSRF for the mutation.
- Use a dedicated confirmation screen or native dialog pattern.
- State the exact object and consequences, including references or protected
  usage when relevant.
- Use Wagtail's destructive button treatment for confirmation and a clear safe
  escape back to the object or listing.
- After success, redirect to a stable page and show a native success message.
  On failure, show a useful native error message without losing context.

## 11. Feedback, loading, and asynchronous fragments

- Use Wagtail's message system for durable success, warning, and error feedback.
  Do not rely on a color change or a toast that disappears before it can be
  read.
- Disable or show progress on the initiating control during slow work and avoid
  duplicate submissions.
- Keep headers, breadcrumbs, actions, search, and filters outside AJAX result
  fragments unless the generic view explicitly teleports or replaces them.
- Make the replaced results region identifiable, announce meaningful result
  changes, preserve focus where practical, and keep back/forward navigation
  coherent.
- Render identical action permissions and URLs in full-page and fragment
  responses.

## 12. Choosers and modal workflows

- Use `ChooserViewSet` and its current base chooser views for selecting model or
  non-model records instead of inventing a modal protocol.
- Reuse the native chooser title, tabs, search, result table, pagination,
  creation form, and selection response behavior that apply to the installed
  version.
- Keep result-only updates inside the chooser's results fragment. Do not return
  a complete admin page for a modal refresh.
- Make the chosen object's identity clear, label every choose/control action,
  and keep permissions consistent between browsing and creating.
- Preserve modal focus management, keyboard dismissal, loading state, and the
  originating field's value and label after selection.
- Use linked-field filtering through the chooser APIs where supported rather
  than coupling custom JavaScript to another widget's DOM.

## 13. Accessibility and responsive quality

Meet Wagtail's WCAG 2.1 AA target and the project's stricter requirements:

- valid semantic HTML and native controls before ARIA;
- logical heading order, landmarks, form labels, error associations, table
  headers, menu names, and unique IDs;
- visible keyboard focus, sensible tab order, Escape/arrow behavior supplied by
  native menu components, and no hover-only operation;
- accessible names for icons, dots menus, close controls, and row actions;
- touch targets and spacing that remain usable on phones;
- no clipped breadcrumbs, menus, dialogs, chooser content, or validation text;
- no meaning conveyed by color alone; and
- support for zoom and long or translated strings.

At minimum, inspect a narrow phone viewport and a wide desktop viewport. Also
check light/dark themes, forced-colors, RTL, and reduced motion when those states
are available. Use CSS logical properties so layouts mirror correctly.

## 14. CSS, icons, and JavaScript

- Reuse the design tokens, CSS variables, type scale, utility classes, component
  classes, and registered icons shipped by the installed Wagtail version.
- Do not assume a project's CSS build will compile arbitrary Wagtail Tailwind
  utilities. Verify a class exists in shipped CSS before using it.
- Scope unavoidable custom styles under an application-owned component class.
  Keep selectors shallow and use classes for styles, IDs for semantics, and
  `data-*` attributes for behavior.
- Avoid hard-coded brand colors, physical left/right spacing, copied SVGs, and
  magic offsets derived from one screenshot.
- Ensure boundaries remain visible in forced-colors mode; never disable forced
  color adjustment globally.
- Prefer Wagtail's existing components and Stimulus controllers. Add custom
  JavaScript only for domain behavior the native components do not provide.
- If custom JS is necessary, make it keyboard-safe, resilient to fragment
  replacement, and compatible with the project's lint/build pipeline.

## 15. Permissions, localization, and performance

- Enforce admin authentication, model/object permissions, and tenant/site or
  collection boundaries on the server. Hiding a button is not authorization.
- Build header, overflow, row, and bulk actions from the same permission rules
  used by their endpoints.
- Mark user-visible strings for translation and use locale-aware formatting.
- Avoid N+1 queries in table columns, permission checks, labels, and usage
  counts. Use `select_related`, `prefetch_related`, or annotations as warranted.
- Validate all mutation inputs and use Django/Wagtail URL helpers rather than
  concatenating admin URLs.

## 16. Completion checks

Automated checks should cover, in proportion to risk:

- unauthenticated, unauthorized, partially authorized, and authorized users;
- correct title, breadcrumbs, header actions, overflow actions, and row actions;
- GET rendering and POST success, invalid, protected, and conflict paths;
- CSRF and HTTP method behavior for mutations;
- search, filters, sorting, pagination, empty states, and query preservation;
- full-page and asynchronous fragment responses; and
- an automated accessibility scan when the project has browser tests.

Manual/visual checks should cover:

- populated, empty, filtered-empty, invalid, success, long-content, and
  permission-restricted states;
- mobile and desktop header layout and action overflow;
- keyboard use and visible focus;
- sticky footer reachability and content clearance;
- dark theme, zoom, and long labels; and
- current screenshots or other visual proof required by repository policy.

## Official sources to recheck

Use the documentation branch matching the project version:

- [Generic views](https://docs.wagtail.org/en/latest/extending/generic_views.html)
- [Creating admin views](https://docs.wagtail.org/en/latest/extending/admin_views.html)
- [Using forms in admin views](https://docs.wagtail.org/en/latest/extending/forms.html)
- [Template components](https://docs.wagtail.org/en/latest/extending/template_components.html)
- [UI components](https://docs.wagtail.org/en/latest/reference/ui/components.html)
- [Tables](https://docs.wagtail.org/en/latest/reference/ui/tables.html)
- [Icons](https://docs.wagtail.org/en/latest/advanced_topics/icons.html)
- [UI coding guidelines](https://docs.wagtail.org/en/latest/contributing/ui_guidelines.html)
- [Release notes and upgrade considerations](https://docs.wagtail.org/en/latest/releases/index.html)

When documentation and installed source disagree, follow the installed version
and record the version-specific choice in the change.
