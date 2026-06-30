**SYDECO LIGHTML**

**CONTRACT RISK ANALYZER**

**Design System & UI/UX Product Guide**

**Version 1.0**

Prepared for UI/UX design, product, legal review, and engineering handoff

**Design intent**

A sober, evidence-first legal technology interface that makes risk understandable without pretending to replace legal judgment.

DOCUMENT CONTROL

# How to use this design system

This file is the source of truth for the Contract Risk Analyzer interface. It translates the product requirements into visual rules, interaction patterns, screen specifications, component behavior, content standards, and handoff criteria.

| **Field**             | **Value**                                            |
| --------------------- | ---------------------------------------------------- |
| Product               | Sydeco LightML Contract Risk Analyzer                |
| Design-system version | 1.0                                                  |
| Status                | Baseline for pilot design and development            |
| Primary owners        | Product owner, lead UI/UX designer, frontend lead    |
| Mandatory reviewers   | Security lead and legal-review representative        |
| Target platforms      | Responsive web application and accessible PDF report |
| Default theme         | Light; dark theme deferred                           |
| Accessibility target  | WCAG 2.2 AA                                          |

## Authority and precedence

- Security, tenant isolation, legal-source status, and retention requirements override visual convenience.
- Structured analysis data is the single source for portal views and PDF reports.
- Risk score and confidence must remain visually and semantically distinct.
- Only verified citations may be presented as authoritative legal sources.
- Components should be reused before a new component or page-specific pattern is created.

## Contents

1\. Product experience principles

2\. Users, roles, and information architecture

3\. Brand foundation

4\. Color system

5\. Typography, iconography, and imagery

6\. Spacing, grid, radius, and elevation

7\. Responsive layouts and navigation

8\. Core components

9\. Product-specific components

10\. Screen templates and page specifications

11\. Data visualization

12\. Content design and legal language

13\. Accessibility

14\. Secure and trustworthy UX

15\. Motion, loading, and feedback

16\. Figma organization and governance

17\. Engineering handoff and QA

Appendices: tokens, flows, and checklists

SECTION 01

# Product experience principles

The product should feel rigorous, local, understandable, and controlled-not conversational, magical, or overconfident.

| **Principle**                               | **Design implication**                                                                                                                 |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Evidence before assertion                   | Every material finding must lead to a clause excerpt, rule source, and-when applicable-a verified citation.                            |
| Human judgment stays visible                | The interface supports screening and review. It never implies that an automated score is a legal conclusion.                           |
| Progressive disclosure                      | Executives see a clear summary first; analysts and lawyers can drill into evidence, rules, and metadata.                               |
| Local-first trust                           | Confidentiality, encryption, retention, tenant context, and download expiry are visible at the moments that matter.                    |
| Deterministic core, explainable enhancement | Rules and approved datasets own findings and scores. ML confidence and LLM explanations are supporting layers.                         |
| Calm severity                               | Use strong hierarchy and precise labels, not alarmist graphics. Critical findings are serious without making the entire interface red. |
| Designed for review                         | Findings must be assignable, commentable, approvable, and reproducible in the report.                                                  |
| Multilingual by structure                   | The layout must tolerate longer French and Indonesian strings, mixed legal citations, and language-specific evidence.                  |

**Core product promise**

Upload a contract, understand its main risks, verify the evidence, and produce an auditable report-without exposing the document to an uncontrolled external AI service.

## Experience success criteria

- A first-time analyst can upload and understand the result without training.
- A lawyer can verify how each material finding was produced within two interactions.
- A manager can distinguish risk severity from detection confidence immediately.
- A user always knows the active organization, document, jurisdiction status, and report status.
- No screen suggests that a low score means "legally safe" or that a high score proves illegality.

SECTION 02

# Users, roles, and information architecture

Role-aware navigation prevents overexposure while keeping the primary analysis workflow simple.

## Role model

| **Role**             | **Primary goals**                                  | **Default access**                                        | **Primary navigation**                                |
| -------------------- | -------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------- |
| System administrator | Operate the platform and manage organizations      | Platform settings, organizations, global citations, audit | Organizations, Users, Citation library, Audit, System |
| Organization manager | Manage team and portfolio                          | All cases in own organization, team, usage, retention     | Dashboard, Cases, Reports, Team, Settings             |
| Analyst              | Screen contracts and prepare cases                 | Own or assigned cases; no global citation approval        | Dashboard, New analysis, Cases                        |
| Legal reviewer       | Validate findings and approve professional reports | Assigned cases and legal-review workspace                 | Review queue, Cases, Citation proposals               |
| Viewer / client      | Read finalized outputs                             | Approved reports only                                     | Reports, Shared items                                 |

## Primary information architecture

| **Level**      | **Area**              | **Contents**                                          |
| -------------- | --------------------- | ----------------------------------------------------- |
| Global         | Organization switcher | Current organization, tenant identity, user menu      |
| Primary        | Dashboard             | Work queue, recent cases, portfolio summary, usage    |
| Primary        | New analysis          | Upload, metadata, configuration, processing           |
| Primary        | Cases                 | Search, filter, status, assignment, retention         |
| Primary        | Reports               | Approved reports, expiring downloads, versions        |
| Role-specific  | Review queue          | Findings requiring legal validation or approval       |
| Role-specific  | Citation library      | Draft, verified, rejected, superseded citations       |
| Administration | Team / Organizations  | Users, roles, MFA, status, retention                  |
| Administration | Audit / System        | Security events, configuration status, service health |

## Navigation rules

- Use a persistent left navigation at desktop widths and a compact top bar plus drawer below 1024 px.
- Show no more than seven top-level items for any single role.
- Never rely on hidden hover navigation for required actions.
- Display the current organization and user role in the global header.
- Case pages use tabs for Summary, Findings, Clauses, Sources, Review, Report, and Activity; hide tabs the role cannot access.

SECTION 03

# Brand foundation

A professional legal-tech identity: precise, restrained, modern, and visibly sovereign.

## Brand attributes

| **Attribute** | **Express through**                                                 | **Avoid**                                                           |
| ------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Trustworthy   | Clear evidence, stable layouts, precise labels, visible controls    | Futuristic glow, unsupported claims, anthropomorphic AI             |
| Sovereign     | Local-processing status, Indonesian relevance, controlled model use | Flags as decoration, nationalism clichés, external-service logos    |
| Professional  | Strong typography, calm spacing, consistent tables                  | Consumer-app playfulness, excessive gradients, novelty interactions |
| Intelligent   | Progressive disclosure, useful summaries, structured comparison     | Chat-first experience, unexplained scores, black-box animation      |
| Decisive      | Clear primary actions, explicit review status, strong empty states  | Ambiguous buttons, passive alerts, hidden next steps                |

## Product naming

| **Context**                   | **Preferred name**                                | **Rule**                                                             |
| ----------------------------- | ------------------------------------------------- | -------------------------------------------------------------------- |
| Formal cover and legal report | Sydeco LightML Contract Risk Analyzer             | Use full name on first reference                                     |
| Application navigation        | Contract Risk Analyzer                            | Use where space permits                                              |
| Compact UI                    | CRA                                               | Use only after full-name introduction or in admin/technical contexts |
| Feature labels                | Analysis, Finding, Clause, Source, Review, Report | Use concrete nouns; avoid "AI answer"                                |

## Logo and lockup guidance

Use the approved Sydeco corporate mark when available. The product name should sit beside or below it, never merged into a new unapproved logo. Maintain clear space equal to the cap height of "SYDECO." Minimum digital width: 120 px for the corporate mark and 220 px for the full product lockup.

**Do not invent an AI mascot**

The product's trust comes from evidence, governance, and controlled processing. Avoid robots, brains, gavels, and glowing neural-network imagery.

SECTION 04

# Color system

Color communicates hierarchy and state, but every status also requires a text label and/or icon.

## Core palette

| **Token**            | **Swatch** | **Hex** | **Primary use**                                 | **Rules**                                 |
| -------------------- | ---------- | ------- | ----------------------------------------------- | ----------------------------------------- |
| color.brand.navy.900 |            | #14213D | Primary navigation, report cover, dark surfaces | Use with white text.                      |
| color.brand.blue.600 |            | #2F6BFF | Primary action, active navigation, links        | Use blue 700 for small text links.        |
| color.brand.blue.50  |            | #EFF4FF | Selected rows, informational backgrounds        | Never use as the only selected-state cue. |
| color.brand.teal.600 |            | #0E9384 | Verified, local processing, secondary emphasis  | Do not use as the general success color.  |
| color.ink.950        |            | #101828 | Primary text                                    | Default on white and gray 50.             |
| color.ink.600        |            | #475467 | Secondary text                                  | Minimum for 14 px body text.              |
| color.gray.200       |            | #EAECF0 | Borders, dividers                               | Avoid heavy table grids.                  |
| color.gray.50        |            | #F9FAFB | Application background                          | Cards remain white.                       |

## Semantic palette

| **Token**       | **Swatch** | **Hex** | **Primary use**                      | **Rules**                                                                 |
| --------------- | ---------- | ------- | ------------------------------------ | ------------------------------------------------------------------------- |
| status.critical |            | #7A271A | Critical risk                        | Always pair with "Critical" and alert icon.                               |
| status.high     |            | #D92D20 | High risk / destructive action       | Do not use for ordinary validation errors if the whole page is high-risk. |
| status.medium   |            | #DC6803 | Medium risk / warning                | Use dark amber text on pale background.                                   |
| status.low      |            | #039855 | Low risk / success                   | "Low risk" is not "safe."                                                 |
| status.info     |            | #1570EF | Information and in-progress state    | Use for neutral system guidance.                                          |
| status.verified |            | #0E9384 | Verified legal citation              | Reserved for verification, not general success.                           |
| status.draft    |            | #6941C6 | Draft or internal-only legal content | Never show as authoritative in client report.                             |
| status.neutral  |            | #667085 | Unknown, not run, not applicable     | Use dashed or neutral icon where useful.                                  |

## Risk severity mapping

| **Level**     | **Foreground** | **Background** | **Icon**           | **Required wording** |
| ------------- | -------------- | -------------- | ------------------ | -------------------- |
| Critical      | #7A271A        | #FEF3F2        | Octagon / alert    | Critical             |
| High          | #B42318        | #FEF3F2        | Triangle / alert   | High                 |
| Medium        | #B54708        | #FFFAEB        | Triangle / warning | Medium               |
| Low           | #027A48        | #ECFDF3        | Circle / check     | Low                  |
| Informational | #175CD3        | #EFF8FF        | Circle / info      | Information          |

**Never map confidence to risk colors**

Use a separate confidence treatment-high, medium, low, unavailable-so users cannot confuse "high confidence" with "high risk."

SECTION 05

# Typography, iconography, and imagery

Legibility and legal verification are more important than visual novelty.

## Typography families

| **Use**                 | **Family**     | **Fallback**                       | **Notes**                                                 |
| ----------------------- | -------------- | ---------------------------------- | --------------------------------------------------------- |
| Interface and reports   | Inter          | Arial, Liberation Sans, sans-serif | Primary family; use tabular numerals for scores and dates |
| Legal evidence excerpts | Source Serif 4 | Georgia, Liberation Serif, serif   | Optional; only for quoted clause text and report excerpts |
| Code, IDs, hashes       | JetBrains Mono | DejaVu Sans Mono, monospace        | Use sparingly; never for long body text                   |

## Type scale

| **Token**  | **Size / line** | **Weight** | **Use**                                                        |
| ---------- | --------------- | ---------- | -------------------------------------------------------------- |
| display.lg | 48 / 56         | 700        | Marketing or report cover only                                 |
| heading.1  | 36 / 44         | 700        | Page title                                                     |
| heading.2  | 30 / 38         | 700        | Major section                                                  |
| heading.3  | 24 / 32         | 600        | Card group / report section                                    |
| heading.4  | 20 / 28         | 600        | Card title                                                     |
| body.lg    | 18 / 28         | 400        | Lead text                                                      |
| body.md    | 16 / 24         | 400        | Default UI body                                                |
| body.sm    | 14 / 20         | 400 or 500 | Tables, metadata, controls                                     |
| caption    | 12 / 18         | 500        | Labels, helper text; never essential dense content below 12 px |

## Typography rules

- Use sentence case for page titles, buttons, tabs, table headers, and form labels.
- Use tabular numerals for risk scores, percentages, dates, usage counts, and monetary values.
- Do not center long text. Centering is limited to empty states, report cover, and compact metrics.
- Limit normal reading lines to 60-85 characters.
- Underline links on hover and keyboard focus; never use color alone to distinguish links in prose.

## Iconography

| **Rule**      | **Specification**                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------------- |
| Library       | Use one outline icon family with 2 px stroke at 24 px base size.                                                  |
| Sizes         | 16 px inline, 20 px controls, 24 px navigation, 32-48 px empty states.                                            |
| Meaning       | Use familiar symbols: upload, file, search, filter, check, warning, shield, lock, clock, download.                |
| Accessibility | Decorative icons are hidden from screen readers; meaningful icons have accessible names or adjacent text.         |
| Restrictions  | Do not use scales of justice, gavels, robots, brains, magic wands, or sparkle icons as primary product metaphors. |

## Imagery

Prefer product screenshots, abstract document/evidence compositions, and restrained diagrams. Photography should show professional review and collaboration, not staged courtrooms. Data illustrations must use the same color and icon tokens as the product.

SECTION 06

# Spacing, grid, radius, and elevation

A disciplined 4 px system supports dense legal information without making the interface feel cramped.

## Spacing scale

| **Token** | **Value** | **Typical use**                   |
| --------- | --------- | --------------------------------- |
| space.0   | 0         | Reset                             |
| space.1   | 4 px      | Icon gaps, compact metadata       |
| space.2   | 8 px      | Control internals, chip gaps      |
| space.3   | 12 px     | Dense card padding, field groups  |
| space.4   | 16 px     | Default card padding, form rhythm |
| space.6   | 24 px     | Section gaps                      |
| space.8   | 32 px     | Page section spacing              |
| space.12  | 48 px     | Large page transitions            |
| space.16  | 64 px     | Report/marketing separation       |

## Layout grid

| **Viewport** | **Columns** | **Margin** | **Gutter** | **Behavior**                                   |
| ------------ | ----------- | ---------- | ---------- | ---------------------------------------------- |
| 360-767 px   | 4           | 16 px      | 16 px      | Single-column; bottom or drawer navigation     |
| 768-1023 px  | 8           | 24 px      | 20 px      | Two-column where content allows                |
| 1024-1439 px | 12          | 32 px      | 24 px      | Persistent left navigation                     |
| 1440 px+     | 12          | 48 px      | 24 px      | Content max-width; avoid excessive line length |

## Application shell dimensions

| **Element**                | **Desktop**                       | **Tablet**         | **Mobile**               |
| -------------------------- | --------------------------------- | ------------------ | ------------------------ |
| Left navigation            | 248 px expanded / 72 px collapsed | Drawer             | Drawer                   |
| Top bar                    | 64 px                             | 64 px              | 56 px                    |
| Main content max width     | 1280 px                           | 100% minus margins | 100% minus 16 px margins |
| Detail side panel          | 400-480 px                        | Overlay drawer     | Full-screen sheet        |
| Minimum interactive target | 44 × 44 px                        | 44 × 44 px         | 44 × 44 px               |

## Radius and elevation

| **Token**   | **Value**     | **Use**                             |
| ----------- | ------------- | ----------------------------------- |
| radius.sm   | 4 px          | Inputs, compact tags                |
| radius.md   | 8 px          | Buttons, cards, menus               |
| radius.lg   | 12 px         | Modals, upload zones, major cards   |
| radius.xl   | 16 px         | Hero summary panels only            |
| radius.pill | 999 px        | Status chips and segmented controls |
| shadow.1    | 0 1 2 / 6%    | Inputs and subtle raised cards      |
| shadow.2    | 0 4 12 / 10%  | Dropdowns and popovers              |
| shadow.3    | 0 16 32 / 14% | Modals and drawers                  |

SECTION 07

# Responsive layouts and navigation

Design each workflow for constrained width first; legal evidence must remain usable without horizontal page scrolling.

## Desktop shell

| **Region**      | **Required content**                                                                                      |
| --------------- | --------------------------------------------------------------------------------------------------------- |
| Global header   | Organization switcher, search, encryption/system status when relevant, notifications, user menu           |
| Left navigation | Role-filtered primary sections with text labels; collapsible only after onboarding                        |
| Page header     | Breadcrumb, page title, status, primary action, optional secondary actions                                |
| Main canvas     | 12-column responsive layout; cards align to grid                                                          |
| Context panel   | Evidence, metadata, filters, or review activity; never required for completing the primary task on mobile |

## Mobile behavior

- Replace large data tables with sortable cards or a horizontal scroll region with a visible cue.
- Keep risk summary, status, and primary next action above the first scroll.
- Open finding evidence in a full-screen sheet with a persistent close/back action.
- Use sticky bottom actions only for a single clear action such as "Submit for review."
- Do not compress score breakdowns into unreadable charts; show ordered lists instead.

## Navigation patterns

| **Pattern**    | **Use**                       | **Do not use**                          |
| -------------- | ----------------------------- | --------------------------------------- |
| Breadcrumbs    | Case and admin hierarchy      | As the only back-navigation mechanism   |
| Tabs           | Sibling views of one case     | For sequential upload steps             |
| Stepper        | Upload and configuration flow | For non-linear case review              |
| Side panel     | Evidence, filters, activity   | For long multi-step forms               |
| Modal          | Confirmation or focused edit  | For complete pages or complex review    |
| Command search | Find cases, reports, users    | As a replacement for visible navigation |

SECTION 08

# Core components

Every component must define anatomy, variants, states, accessibility behavior, and content limits.

## Buttons

| **Variant** | **Use**                            | **Height**                      | **Content rule**                              |
| ----------- | ---------------------------------- | ------------------------------- | --------------------------------------------- |
| Primary     | One dominant page or modal action  | 40 px default / 48 px prominent | Verb + object: "Analyze contract"             |
| Secondary   | Alternative or supporting action   | 40 px                           | Do not compete visually with primary          |
| Tertiary    | Low-emphasis action in dense UI    | 36-40 px                        | Text or icon + text                           |
| Destructive | Delete, revoke, reject permanently | 40 px                           | Require confirmation for irreversible actions |
| Link        | Navigation or inline action        | Auto                            | Never use for form submission                 |
| Icon-only   | Recognizable repeated utility      | 40-44 px                        | Tooltip and accessible name required          |

States: default, hover, pressed, focus-visible, disabled, loading. Loading buttons retain their width and replace the leading icon with a spinner while keeping the label or a clear progress label.

## Form fields

| **Element**  | **Specification**                                                                       |
| ------------ | --------------------------------------------------------------------------------------- |
| Label        | Above control; persistent; required indicator uses text or "\*" plus helper explanation |
| Input height | 40 px default, 48 px for primary onboarding forms                                       |
| Helper text  | 14 px; explains format or consequence before an error occurs                            |
| Error        | Inline below field with error icon; focus moves to first invalid field on submit        |
| Success      | Use only when meaningful, such as a verified email or valid key                         |
| Read-only    | Distinct from disabled; selectable and readable                                         |
| Sensitive    | Mask by default; provide explicit reveal and copy actions with audit where necessary    |

## Selection controls

| **Control**       | **Use**                                                          |
| ----------------- | ---------------------------------------------------------------- |
| Checkbox          | Independent multi-select or agreement                            |
| Radio             | One choice from a small visible set                              |
| Switch            | Immediate binary setting; not for form submission requiring Save |
| Combobox          | Searchable selection, e.g., organization or jurisdiction         |
| Segmented control | Two to four compact modes with immediate change                  |
| Date picker       | Retention, expiry, and report date; allow keyboard entry         |

## Feedback components

| **Component**      | **Purpose**                                     | **Persistence**                                         |
| ------------------ | ----------------------------------------------- | ------------------------------------------------------- |
| Inline validation  | Field-specific correction                       | Until corrected                                         |
| Banner             | Page-level system or legal status               | Persistent until resolved or dismissed if non-critical  |
| Toast              | Confirmation of completed action                | 4-8 seconds; never the only record of a critical action |
| Alert dialog       | Irreversible or security-sensitive confirmation | Requires explicit choice                                |
| Progress indicator | Known or unknown operation duration             | Persistent while operation runs                         |
| Skeleton           | Initial layout loading                          | Replace when content arrives; avoid for errors          |

## Cards, tables, and lists

- Cards group one concept; do not nest more than one card level.
- Tables are for comparison and scanning. Use sticky headers, row focus, sorting labels, and accessible pagination.
- Use a kebab menu only for secondary row actions. Primary actions remain visible.
- Every empty table requires an explanation and a relevant next action.
- Selected rows use background, border or checkmark-not color alone.

SECTION 09

# Product-specific components

These components make the CRA recognizable and trustworthy. They should be documented as reusable Figma components, not redrawn per screen.

## Risk score summary

| **Anatomy** | **Requirement**                                                            |
| ----------- | -------------------------------------------------------------------------- |
| Score       | 0-100 in tabular numerals; no decimal in normal UI                         |
| Label       | Critical, High, Medium, Low, or Not scored                                 |
| Calibration | Show "Provisional" when the policy is not legally calibrated               |
| Breakdown   | Direct link to score contributors and policy version                       |
| Disclaimer  | "Decision support; not legal advice" in report and result context          |
| Visual      | Use a horizontal scale or compact ring only when the label is also printed |

**Forbidden pattern**

Do not show a large green "Safe" badge. A low score means fewer detected risks under the current rules-not guaranteed validity or enforceability.

## Confidence indicator

| **State**   | **Label**         | **Display**                                 |
| ----------- | ----------------- | ------------------------------------------- |
| ≥ 0.85      | High confidence   | Teal text + 3 filled bars                   |
| 0.65-0.84   | Medium confidence | Blue-gray text + 2 filled bars              |
| < 0.65      | Low confidence    | Amber text + 1 filled bar and review prompt |
| Unavailable | Not available     | Neutral icon and explanation                |

## Finding card

| **Zone**     | **Contents**                                                             |
| ------------ | ------------------------------------------------------------------------ |
| Header       | Severity label, finding title, category, review status                   |
| Evidence     | Exact clause excerpt with paragraph/page reference                       |
| Explanation  | Plain-language consequence; no invented legal conclusion                 |
| Source row   | Detection source: rule, keyword database, semantic recovery, or reviewer |
| Legal source | Verified citation or internal draft status                               |
| Actions      | Open evidence, assign, comment, confirm, reject, propose correction      |
| Metadata     | Finding ID, rule version, confidence when applicable                     |

## Clause coverage matrix

| **Status**             | **Meaning**                                 | **Display**                                |
| ---------------------- | ------------------------------------------- | ------------------------------------------ |
| Present                | Detected and accepted                       | Check icon, source, evidence link          |
| Semantically recovered | NLI recovered clause missed by rule         | Check icon + "Semantic match" + confidence |
| Missing                | Mandatory clause not detected               | Severity, rationale, recommendation        |
| Not required           | Not mandatory for selected contract profile | Neutral "Not required"                     |
| Needs review           | Ambiguous presence or low confidence        | Amber review state                         |

## Citation component

| **Status**  | **Customer visibility** | **Designer treatment**                                                         |
| ----------- | ----------------------- | ------------------------------------------------------------------------------ |
| Verified    | Yes                     | Teal verified chip; source title, article, jurisdiction, verification date     |
| Draft       | Internal only           | Purple draft chip; hidden from client PDF unless explicitly marked as research |
| Rejected    | No                      | Muted strike-through in reviewer history only                                  |
| Superseded  | No as current authority | Show replacement link in history                                               |
| Unavailable | Yes as limitation       | Neutral "No verified citation available"                                       |

## Evidence viewer

- Preserve the original clause text and highlight only the matched phrase.
- Show page and paragraph location; support previous/next match.
- Display surrounding context by default, with the full document available to authorized users.
- Never silently translate evidence; show original and translated text as separate labeled views.
- Maintain text selection and copy where policy permits; copying sensitive content may be audited.

## Review decision bar

| **Action**          | **Meaning**                            | **Required behavior**                              |
| ------------------- | -------------------------------------- | -------------------------------------------------- |
| Confirm             | Finding is accepted for report         | Record reviewer and timestamp                      |
| Reject              | Finding is not applicable or incorrect | Reason required                                    |
| Edit recommendation | Change business-language guidance      | Preserve original and version history              |
| Escalate            | Senior legal review required           | Assign and notify                                  |
| Approve report      | Freeze reviewed report version         | Require legal-reviewer permission and confirmation |

SECTION 10

# Screen templates and page specifications

Each page has one primary job, a defined information hierarchy, and mandatory states.

## A. Authentication and access

| **Screen**      | **Primary goal**           | **Mandatory elements**                                           | **Critical states**                               |
| --------------- | -------------------------- | ---------------------------------------------------------------- | ------------------------------------------------- |
| Sign in         | Securely authenticate      | Email, password, organization context if needed, forgot password | Invalid credentials, locked account, rate-limited |
| MFA challenge   | Complete TOTP verification | 6-digit code, recovery code option, trusted-device policy text   | Expired code, too many attempts, recovery flow    |
| Session expired | Protect sensitive work     | Reason, sign-in action, unsaved-work explanation                 | Re-authentication                                 |

## B. Dashboard

| **Zone**          | **Contents**                                                      |
| ----------------- | ----------------------------------------------------------------- |
| Header            | Welcome, organization, "New analysis" primary action              |
| Work queue        | Processing, needs review, ready for approval, failed              |
| Recent cases      | Contract name, type, score, status, owner, last activity          |
| Portfolio metrics | Cases by risk level, pending review, usage allowance              |
| Trust status      | Encryption, local model availability, verified jurisdiction packs |
| Empty state       | Explain the workflow and provide first upload action              |

## C. New analysis flow

| **Step**           | **Purpose**              | **Required inputs**                                                   | **UX rules**                                                  |
| ------------------ | ------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1 Upload           | Choose file              | DOCX, TXT, text-based PDF; file size and confidentiality notice       | Drag/drop and browse; validate before upload                  |
| 2 Document details | Confirm context          | Display name, contract type, jurisdiction, language, client/reference | Allow auto-detected values later; explain why context matters |
| 3 Analysis options | Set scope                | Package/report depth, explanation layer, reviewer                     | Advanced options collapsed by default                         |
| 4 Confirmation     | Review before processing | Retention date, encryption status, consent/authority confirmation     | Block if production encryption is unavailable                 |
| 5 Processing       | Track status             | Stage names and elapsed time                                          | Allow safe navigation away and notify on completion           |

## D. Processing page

| **Stage label**   | **Example status copy**                               |
| ----------------- | ----------------------------------------------------- |
| Uploading         | Securely uploading document                           |
| Extracting        | Reading document structure and text                   |
| Classifying       | Identifying language, document type, and jurisdiction |
| Analyzing clauses | Checking mandatory and risky clauses                  |
| Scoring           | Calculating the reproducible risk breakdown           |
| Preparing report  | Building the structured result and preview            |

If processing exceeds the expected time, show a neutral message and continue in the background. Never display fake percentages unless the backend provides meaningful progress.

## E. Result overview

| **Priority** | **Module**        | **Contents**                                                                    |
| ------------ | ----------------- | ------------------------------------------------------------------------------- |
| 1            | Case header       | Document name, type, jurisdiction, language, status, owner                      |
| 2            | Risk summary      | Score, label, provisional/calibrated status, confidence shown separately        |
| 3            | Top findings      | Three to five most material findings with evidence links                        |
| 4            | Mandatory clauses | Present, missing, needs review                                                  |
| 5            | Next actions      | Submit for review, assign, generate first-test report, compare version          |
| 6            | Limitations       | Unsupported jurisdiction, translation, OCR, missing citation, model unavailable |

## F. Findings view

- Provide filters for severity, category, status, source, and reviewer.
- Default sort: Critical/High first, then score impact, then document order.
- Opening a finding preserves filter and scroll position.
- Bulk actions are limited to assignment or export; legal confirmation remains deliberate.
- Show a zero-findings state that explains the limits of automated screening.

## G. Professional legal-review workspace

| **Region**    | **Desktop behavior**                                |
| ------------- | --------------------------------------------------- |
| Left pane     | Ordered finding list and filters                    |
| Center pane   | Evidence excerpt and surrounding document context   |
| Right pane    | Explanation, citation, comments, decision controls  |
| Sticky footer | Previous/next finding, save decision, submit review |
| Header        | Review progress, assignee, deadline, report version |

## H. Report preview and generation

- Preview uses the same structured result as the portal.
- Allow inclusion/exclusion only where policy permits; every change is recorded.
- Show report status: Draft, Under review, Approved, Superseded.
- Generate an expiring download link after approval.
- Display included language, jurisdiction pack, scoring policy version, and citation status.

## I. Cases and portfolio

| **Feature** | **Requirement**                                                                |
| ----------- | ------------------------------------------------------------------------------ |
| Search      | Filename, client/reference, case ID, owner                                     |
| Filters     | Status, score level, contract type, jurisdiction, assignee, date               |
| Saved views | Role-specific views such as "My reviews" or "High-risk this month"             |
| Bulk action | Assign, archive, export metadata; no bulk delete without elevated confirmation |
| Retention   | Show expiry date and upcoming deletion warning                                 |
| Comparison  | Link versions of the same contract and show changed findings                   |

## J. Administration

| **Screen**       | **Required capabilities**                                                 |
| ---------------- | ------------------------------------------------------------------------- |
| Team             | Create/suspend users, assign roles, MFA reset, session revoke             |
| Organizations    | Create org, set retention, usage limits, status                           |
| Citation library | Review draft citations, verify/reject/supersede, view history             |
| Audit log        | Filter action, user, org, resource, date; export within permissions       |
| System status    | Encryption configured, models available, rate-limit backend, backup state |

SECTION 11

# Data visualization

Charts summarize patterns; they never replace the finding list or score breakdown.

## Approved chart types

| **Use case**         | **Preferred chart**                    | **Rules**                                                  |
| -------------------- | -------------------------------------- | ---------------------------------------------------------- |
| Risk distribution    | Horizontal stacked bar                 | Always label counts and totals; fixed severity order       |
| Cases over time      | Line chart                             | Show interval and missing data; avoid decorative smoothing |
| Findings by category | Sorted horizontal bars                 | Top categories plus "Other" if needed                      |
| Review progress      | Progress bar or stage counts           | Show numerator and denominator                             |
| Score contribution   | Waterfall or ordered contribution list | Must reconcile exactly to final score                      |
| Contract comparison  | Side-by-side bars or change table      | Highlight added, removed, and changed findings             |

## Visualization rules

- Never use a gauge as the only display of risk score.
- Avoid 3D charts, gradients, and unlabeled pie charts.
- Use severity order: Critical, High, Medium, Low, Information.
- Provide data table alternatives for complex charts.
- Use patterns, labels, or icons in addition to color.
- Portfolio charts must respect filters and organization scope visibly.

## Score breakdown pattern

| **Column**           | **Example**                                     |
| -------------------- | ----------------------------------------------- |
| Contributor          | Missing limitation-of-liability clause          |
| Category             | Mandatory clause                                |
| Impact               | +15 risk points                                 |
| Evidence / rationale | Required for selected service agreement profile |
| Policy source        | Scoring policy 2026.06.1                        |
| Review status        | Unreviewed / confirmed / rejected               |

SECTION 12

# Content design and legal language

The interface must be understandable to business users while remaining precise enough for legal review.

## Voice and tone

| **Situation**    | **Tone**                        | **Example**                                                                                                                      |
| ---------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Routine guidance | Direct and calm                 | Upload a contract to begin the analysis.                                                                                         |
| High-risk result | Serious, specific, non-alarmist | This clause may create a significant unilateral obligation. Review the evidence and legal source.                                |
| Uncertainty      | Transparent                     | The jurisdiction could not be determined with sufficient confidence. Select it manually before generating a professional report. |
| Security issue   | Explicit and action-oriented    | Encryption is not configured. Production uploads are disabled.                                                                   |
| Error            | Plain language with recovery    | We could not extract readable text from this PDF. Upload a text-based PDF or DOCX.                                               |
| Success          | Factual                         | Report approved and download link created.                                                                                       |

## Terminology

| **Use**                      | **Avoid**                       | **Reason**                                   |
| ---------------------------- | ------------------------------- | -------------------------------------------- |
| Risk score                   | Legality score                  | The score is not a legal conclusion          |
| Potential issue / finding    | Violation                       | A generic rule may not establish a violation |
| Verified legal source        | AI citation                     | Citations are lawyer-verified data           |
| Analysis complete            | AI has decided                  | Human review remains necessary               |
| Low risk under current rules | Safe contract                   | No guarantee of validity                     |
| Needs review                 | Uncertain / maybe wrong         | Action-oriented and professional             |
| Document type                | Contract category guessed by AI | Use product terminology                      |

## Standard status labels

| **Object**    | **Allowed statuses**                                                   |
| ------------- | ---------------------------------------------------------------------- |
| Analysis      | Draft, Uploading, Processing, Completed, Needs review, Failed, Deleted |
| Finding       | Unreviewed, Confirmed, Rejected, Escalated                             |
| Report        | Draft, Under review, Approved, Superseded                              |
| Citation      | Draft, Verified, Rejected, Superseded                                  |
| User          | Invited, Active, Suspended, Locked                                     |
| Download link | Active, Expired, Revoked, Used                                         |

## Disclaimers

**Standard result disclaimer**

This analysis is decision support based on the selected contract profile, configured rules, and available legal sources. It is not legal advice and does not guarantee validity, enforceability, or litigation outcome.

**Unsupported jurisdiction**

No production-verified legal pack is available for the selected jurisdiction. Findings may still identify contractual patterns, but jurisdiction-specific legal conclusions and authoritative citations are not provided.

SECTION 13

# Accessibility

Accessibility is a release requirement, not a post-launch enhancement.

## Baseline requirements

| **Area**      | **Requirement**                                                                     |
| ------------- | ----------------------------------------------------------------------------------- |
| Standard      | WCAG 2.2 AA for the web application; accessible tagged PDF target for reports       |
| Contrast      | 4.5:1 normal text; 3:1 large text and essential UI boundaries                       |
| Keyboard      | All functions operable by keyboard; visible focus; logical order                    |
| Touch targets | Minimum 44 × 44 px                                                                  |
| Zoom          | Usable at 200% browser zoom without loss of content or functionality                |
| Motion        | Respect prefers-reduced-motion; no essential information conveyed only by animation |
| Language      | Set page and excerpt language; identify translated content                          |
| Tables        | Programmatic headers, captions where needed, keyboard-accessible sorting            |
| Errors        | Summary plus inline errors; focus first invalid field                               |
| Charts        | Text summary and data-table alternative                                             |

## Keyboard pattern

- Tab moves through actionable elements in visual order.
- Arrow keys navigate tabs, segmented controls, menus, and radio groups according to platform conventions.
- Escape closes menus, popovers, drawers, and modals without losing committed work.
- Enter activates primary focused actions; Space toggles checkboxes and buttons.
- Focus returns to the triggering element when an overlay closes.

## Screen reader guidance

- Announce processing state changes through a polite live region.
- Risk summaries include score, label, calibration status, and confidence as separate phrases.
- Finding cards use headings and landmarks; severity is text, not only an icon.
- Evidence highlights do not break the reading order of the original clause.
- Do not announce decorative icons or repeated visual dividers.

SECTION 14

# Secure and trustworthy UX

Security controls must be understandable, visible, and difficult to bypass accidentally.

## Tenant and identity context

- Show the active organization in the header on every authenticated page.
- Require explicit confirmation before moving or sharing a case across organization boundaries; by default, this is not permitted.
- Display the user role in account settings and permission-related errors.
- Do not reveal whether an email belongs to another organization during login or password recovery.

## Encryption and local processing

| **State**                             | **UI behavior**                                                                          |
| ------------------------------------- | ---------------------------------------------------------------------------------------- |
| Encryption enabled                    | Subtle verified status in upload confirmation and system status                          |
| Encryption unavailable in development | Persistent warning; uploads allowed only in explicitly marked non-production mode        |
| Encryption unavailable in production  | Block upload and provide administrator action                                            |
| Local models ready                    | Show local-processing status in system details, not as marketing clutter on every screen |
| Model missing                         | Explain degraded behavior and which features are unavailable                             |

## Downloads and sharing

- Generate time-limited download links only after an authorization check.
- Show expiry time, recipient context if applicable, and a revoke action.
- Default professional-report links to 15 minutes unless the product owner approves another policy.
- Audit generation, revocation, and successful download.
- Never display signing tokens or security secrets in the interface.

## Deletion and retention

| **Action**       | **Pattern**                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------- |
| Retention notice | Show scheduled deletion date on case metadata                                            |
| Delete now       | Explain what is deleted, what remains in audit records, and backup-retention limitations |
| Bulk delete      | Require typed confirmation and elevated permission                                       |
| Legal hold       | Show clear hold status and reason; prevent deletion                                      |
| Expired case     | Replace content with deletion record where policy requires                               |

## Audit and sensitive actions

User, role, organization, retention, citation status, report approval, deletion, and download-link actions must show confirmation and generate durable audit events. The interface may confirm "Action recorded" but must not expose internal audit identifiers to ordinary users.

SECTION 15

# Motion, loading, and feedback

Motion clarifies change and progress. It must never simulate intelligence or hide uncertainty.

| **Token**   | **Duration** | **Use**                             |
| ----------- | ------------ | ----------------------------------- |
| motion.fast | 100 ms       | Hover, pressed, small color changes |
| motion.base | 180 ms       | Menus, tooltips, compact expansions |
| motion.slow | 240 ms       | Drawers, panels, modal entrance     |
| motion.max  | 320 ms       | Large page transitions only         |

## Easing

| **Token**     | **Value**                  | **Use**           |
| ------------- | -------------------------- | ----------------- |
| ease.standard | cubic-bezier(0.2, 0, 0, 1) | Most transitions  |
| ease.enter    | cubic-bezier(0, 0, 0, 1)   | Entering elements |
| ease.exit     | cubic-bezier(0.3, 0, 1, 1) | Exiting elements  |

## Progress and loading rules

- Use determinate progress only when the backend provides meaningful completion data.
- For long analysis, show named stages, elapsed time, background-processing behavior, and safe navigation.
- Use skeletons for predictable content layouts; use spinners for local compact actions.
- Never animate a score counting upward as if the system is "thinking."
- Failure states preserve the case and provide retry or support information.

SECTION 16

# Figma organization and governance

The Figma file should function as a maintained system, not a collection of disconnected screens.

## Recommended Figma pages

| **Page**                 | **Contents**                                               |
| ------------------------ | ---------------------------------------------------------- |
| 00 Cover & release notes | Version, owners, changelog, status                         |
| 01 Foundations           | Color variables, typography, spacing, grid, iconography    |
| 02 Components            | Core components with variants and documentation            |
| 03 Product components    | Risk, finding, citation, clause, evidence, review patterns |
| 04 Patterns              | Forms, tables, navigation, empty/error/loading states      |
| 05 Templates             | Application shell and responsive page templates            |
| 06 Product flows         | Upload, analysis, legal review, report, admin              |
| 07 Prototype             | Current approved clickable prototype                       |
| 08 Archive               | Deprecated components and previous releases                |

## Component naming

| **Pattern**       | **Example**                          |
| ----------------- | ------------------------------------ |
| Core component    | C/Button                             |
| Variant property  | Type=Primary, Size=MD, State=Default |
| Product component | P/Finding card                       |
| Pattern           | PT/Filter bar                        |
| Template          | T/Case detail/Desktop                |
| Icon              | I/Upload/24                          |

## Variable collections

| **Collection** | **Examples**                                                   |
| -------------- | -------------------------------------------------------------- |
| Color / Light  | brand, neutral, semantic, risk, confidence, border, background |
| Typography     | family, size, line-height, weight, letter-spacing              |
| Spacing        | 0, 1, 2, 3, 4, 6, 8, 12, 16                                    |
| Radius         | sm, md, lg, xl, pill                                           |
| Elevation      | shadow 1-3                                                     |
| Motion         | duration and easing                                            |
| Layout         | breakpoints, nav width, content max width                      |

## Governance

- A new component requires a documented unmet need, anatomy, variants, states, accessibility notes, and developer mapping.
- Changes to risk, citation, review, or security components require product and legal/security review.
- Deprecated components remain in Archive for one release and are clearly marked.
- Every design-system release includes a changelog and migration notes.
- Only approved components may be used in production-ready screens.

SECTION 17

# Engineering handoff and quality assurance

Design is complete only when behavior, data, accessibility, and edge cases are specified.

## Handoff package for every screen

| **Item**             | **Required detail**                                                           |
| -------------------- | ----------------------------------------------------------------------------- |
| Responsive frames    | Desktop 1440, tablet 768, mobile 390; additional widths when behavior changes |
| Component references | Exact design-system components and variants                                   |
| Data contract        | Fields, null states, enum values, permissions, formatting                     |
| Interaction notes    | Focus, keyboard, hover, loading, errors, confirmation, undo                   |
| Content              | Final labels, helper text, validation copy, disclaimers                       |
| Accessibility        | Heading order, labels, announcements, alternative content                     |
| Security             | Role access, tenant context, audit event, sensitive data handling             |
| Acceptance criteria  | Observable pass/fail behavior                                                 |

## Definition of done for a UI feature

- Uses approved tokens and components.
- Works at defined breakpoints and at 200% zoom.
- Includes loading, empty, error, disabled, permission-denied, and partial-data states.
- Passes keyboard and screen-reader smoke tests.
- Does not expose draft citations, cross-tenant data, secrets, or unauthorized actions.
- Matches backend status and enum values exactly.
- Produces the same structured meaning in the portal and report where applicable.
- Has product-owner acceptance and required legal/security sign-off.

## UI QA checklist

| **Category**  | **Checks**                                                                        |
| ------------- | --------------------------------------------------------------------------------- |
| Visual        | Grid, spacing, type scale, contrast, truncation, multilingual expansion           |
| Behavior      | All states, retries, navigation preservation, overlay focus                       |
| Data          | Long names, empty arrays, null confidence, unsupported jurisdiction, deleted file |
| Permissions   | Role matrix, hidden vs disabled actions, direct URL access                        |
| Security      | Session expiry, MFA, signed links, encryption block, retention                    |
| Accessibility | Keyboard, focus, labels, landmarks, live regions, table headers                   |
| Reporting     | Portal/PDF consistency, verified citations only, score reconstruction             |

APPENDIX A

# Design token reference

Use these names in Figma variables, CSS custom properties, and component documentation. The companion JSON file contains the same baseline values.

## Color tokens

| **Token**                   | **Value** | **Use**                   |
| --------------------------- | --------- | ------------------------- |
| \--cra-color-brand-navy-900 | #14213D   | Primary dark brand        |
| \--cra-color-brand-blue-600 | #2F6BFF   | Primary action            |
| \--cra-color-brand-blue-700 | #2355D8   | Accessible link/pressed   |
| \--cra-color-brand-teal-600 | #0E9384   | Verified/local processing |
| \--cra-color-text-primary   | #101828   | Primary text              |
| \--cra-color-text-secondary | #475467   | Secondary text            |
| \--cra-color-border         | #D0D5DD   | Control border            |
| \--cra-color-surface        | #FFFFFF   | Cards                     |
| \--cra-color-canvas         | #F9FAFB   | App background            |
| \--cra-color-critical       | #7A271A   | Critical risk             |
| \--cra-color-high           | #D92D20   | High risk/destructive     |
| \--cra-color-medium         | #DC6803   | Medium risk/warning       |
| \--cra-color-low            | #039855   | Low risk/success          |
| \--cra-color-info           | #1570EF   | Info/progress             |
| \--cra-color-draft          | #6941C6   | Draft legal content       |

## Core dimension tokens

| **Category**   | **Tokens**                                     |
| -------------- | ---------------------------------------------- |
| Spacing        | 4, 8, 12, 16, 24, 32, 48, 64 px                |
| Radius         | 4, 8, 12, 16, 999 px                           |
| Control height | 32 compact, 40 default, 48 prominent           |
| Icon           | 16, 20, 24, 32, 48 px                          |
| Content width  | 1280 px maximum application content            |
| Navigation     | 248 px expanded, 72 px collapsed, 64 px header |
| Touch target   | 44 × 44 px minimum                             |

APPENDIX B

# Component inventory

| **Group**      | **Components**                                                           |
| -------------- | ------------------------------------------------------------------------ |
| Foundations    | Color, type, spacing, grid, radius, elevation, motion                    |
| Navigation     | App shell, side nav, top bar, breadcrumb, tabs, pagination               |
| Actions        | Button, icon button, link, split button, overflow menu                   |
| Inputs         | Text, textarea, search, password, number, date, select, combobox         |
| Selection      | Checkbox, radio, switch, segmented control                               |
| Feedback       | Inline error, banner, toast, alert dialog, progress, skeleton            |
| Containers     | Card, panel, accordion, modal, drawer, popover, tooltip                  |
| Data           | Table, list, metric, badge, chip, avatar, timeline                       |
| Upload         | Dropzone, file row, extraction warning, processing stage                 |
| CRA            | Risk score, confidence, finding card, evidence viewer, clause matrix     |
| Legal review   | Citation, decision bar, comment thread, review progress, approval status |
| Reporting      | Report cover, finding section, score breakdown, source note, footer      |
| Administration | Role matrix, user status, audit row, system-health status                |

**Component completion rule**

A component is not complete until it includes default, hover, focus, pressed, disabled, loading, error, empty or unavailable states as applicable, plus responsive and accessibility behavior.

APPENDIX C

# Key user flows

## Flow 1: First contract test

- Sign in and select organization.
- Choose New analysis and upload a supported document.
- Confirm document type, language, and jurisdiction.
- Review encryption and retention information.
- Start analysis and leave the page safely if needed.
- Open completed result and review top findings and missing clauses.
- Generate the limited first-test report or submit for professional review.

## Flow 2: Professional report

- Analyst prepares a completed case.
- Analyst assigns a legal reviewer and submits the review.
- Reviewer works through findings, evidence, and citations.
- Reviewer confirms, rejects, edits recommendations, or escalates.
- Reviewer approves the report version.
- System creates an expiring download link and audit event.
- Manager or client viewer accesses the approved report.

## Flow 3: Monthly portfolio management

- Manager opens the organization dashboard.
- Filters cases by risk, type, status, or team member.
- Assigns pending analyses and reviews.
- Monitors usage allowance and upcoming retention expiry.
- Downloads approved reports or portfolio metadata.
- Reviews trends without losing access to the underlying findings.

## Flow 4: Citation verification

- Legal reviewer opens the draft citation queue.
- Reviews jurisdiction, article, official source, finding mapping, and notes.
- Verifies, rejects, or supersedes the citation with a reason.
- System records reviewer, timestamp, and version.
- Verified status becomes available to customer-facing reports; draft content remains internal.

APPENDIX D

# Screen acceptance checklist

| **Screen**     | **Must pass**                                                                         |
| -------------- | ------------------------------------------------------------------------------------- |
| Login / MFA    | No account enumeration; keyboard complete; rate-limit message; recovery path          |
| Dashboard      | Correct role scope; organization visible; empty and loading states; metrics reconcile |
| Upload         | Supported formats; size/type errors; encryption block; retention and consent          |
| Processing     | Named stages; background behavior; failure retry; no fake progress                    |
| Result         | Risk/confidence distinct; limitations visible; top findings lead to evidence          |
| Finding detail | Exact excerpt; source and rule version; review history; accessible actions            |
| Clause matrix  | Present/missing/not required/needs review states; evidence links                      |
| Citation       | Verified/draft/rejected/superseded behavior; no draft authority leakage               |
| Legal review   | Assignment, comments, decisions, version history, approval permission                 |
| Report         | Portal parity; accessible structure; verified sources; score policy version           |
| Cases          | Search/filter/sort; role scope; retention; deleted/expired state                      |
| Administration | MFA reset audit; role limits; no final-admin removal; retention confirmation          |
| Audit          | Filters, pagination, immutable presentation, permission enforcement                   |
| Mobile         | No hidden required actions; readable evidence; full-screen detail sheet               |

END NOTE

# Design direction in one sentence

**Make the reasoning visible.**

The Contract Risk Analyzer should always help the user move from summary → finding → evidence → source → human decision, while preserving confidentiality and clearly communicating limitations.

## Next design deliverables

- Build the Figma variable collections and core component library from the token appendix.
- Design the application shell and responsive navigation.
- Prototype the New analysis, Result overview, Finding detail, and Legal review workflows first.
- Run a usability review with one analyst, one legal reviewer, and one manager before visual polish.
- Validate accessibility and multilingual expansion before developer handoff.