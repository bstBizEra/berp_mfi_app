# 001B — 001A Invariant Traceability

Registry 15; companion to [001B](BERP-MFI-ARCH-001B.md) and its
[enforcement/test registry](BERP-MFI-ARCH-001B-enforcement.md).
Source: 001A at `3026077e3a9988c4e5baba1720091bb1b9203cd2`.
Status: DRAFT INVENTORY — source coverage awaits independent review; all tests NOT RUN.

## Inventory and counting rules

`INV-A-001` through `INV-A-090` are a clause-level inventory extracted from 001A.
Related predicates are grouped only where the same record/operation represents
them; each predicate must be exercised in test instances. Source sections are given
in every row. These identifiers do not alter the existing `A-G*-*` test identifiers.

The two table columns for record and constraints jointly specify concrete fields,
relationships and identity; E/K/S references resolve to the canonical registries.
Owner abbreviations: M=MFI, L=Lending, E=ERPNext, F=Frappe. Mixed ownership denotes
distinct identified source/control records, never duplicate balance ownership.
Authority abbreviations: CFG=independent policy reviewer; OP=authorized scoped
operator/service with original actor; REV=independent approver/reviewer;
AUD=authorized evidence reviewer. Each test reference defines both positive and
negative cases in registry 14, not only a nominal success test.

EN bindings are proposed. Their source-linked feasibility and unresolved coverage
are documented in B-BLK-01/02/03; referencing an EN does not close those blockers.

| Invariant / 001A source | Record, fields and relationship | Owner | Identity / constraint | Transition | Authority | Enforcement | Positive + negative test |
|---|---|---|---|---|---|---|---|
| INV-A-001 §1 Parent deposit/non-deposit scope retained | E01→E03 capability | M | K01/K03; explicit preset | S1 activate | CFG | EN13 | B-T17 |
| INV-A-002 §1 Draft does not authorize implementation or acceptance | E69 review outcome→gate | M | UUID; evidence references | S12 review | AUD/REV | EN09; acceptance registry | B-T20 |
| INV-A-003 §1 Compatibility/001B/001C evidence required | E69 release SHAs/schema/guard map | M | UUID; immutable manifest | S12 accept only with evidence | AUD/REV | EN09; B-BLK-01/02/03 | B-T20 |
| INV-A-004 §2 Resolved site and validated links | E01 company; E35/E28/E09 links | M/E/L/F | K01; exact I/company | S6 authorize | OP | EN01 | B-T01 |
| INV-A-005 §2 Server-issued durable event identity | E52 business_event_id | M | UUID/K09 | S6 received→posted | OP | EN04 | B-T02 |
| INV-A-006 §2 Stable source independent of transport | E52 source namespace/ID/action | M | K09, E54 many:1 event | S6 replay unchanged | OP | EN04 | B-T02 |
| INV-A-007 §2 Key/hash collision semantics | E54 key/hash→E52 | M | K23; mismatched body reject | S6 replay/conflict | OP | EN04 | B-T02 |
| INV-A-008 §2 Immutable executor/origin attribution | E52/E57 actor/originating_actor | M/F | UUID; no caller impersonation | S6 record | OP | EN04/EN09 | B-T15,B-T16 |
| INV-A-009 §2 Material revision and approval binding | E19 target revision/hash→E52 | M | K11; expected revision | S4 invalidated on edit | REV | EN02/EN13 | B-T07 |
| INV-A-010 §2 Decimal currency/date/period policy | E52 amount/currency/dates→E62 | M/E | K09/K24; explicit precision | S6 post | OP/REV | EN05/EN07 | B-T10,B-T11 |
| INV-A-011 §2 Versions are evidence, not identity | E04/E42 versions→E40 | M | K19 excludes versions | S9 post/adjust | REV | EN06 | B-T03,B-T04 |
| INV-A-012 §2 Durable result/reversal/recovery links | E52→E53/E47/E68 | M/L/E | K09/K22 | S6 posted/reversed | OP/REV | EN04/EN08 | B-T10,B-T11 |
| INV-A-013 §2 Canonical hash normalization | E54 normalized material payload hash | M | K23; decimal/date normalization | S6 claim | OP | EN04 | B-T02 |
| INV-A-014 §2 Identity retained for event life | E54→E52 retention policy | M | K23/K09 preserved | S6 historical replay | CFG/OP | EN04/EN12 | B-T02,B-T16 |
| INV-A-015 §2 Result retrieval remains authorized | E52 result→E35/E28 entitlement | M/L | K09; account/case permission | S6 read only | OP | EN01 | B-T01 |
| INV-A-016 §2 Financial GET prohibited | E52 operation type | M/F | K09; method check | S6 mutation denied on GET | OP | EN04 | B-T02 |
| INV-A-017 §2 Redacted denied audit survives rollback | E57 denied action, no financial link required | M | UUID/source request | S12 recorded after rollback | OP/AUD | EN09 | B-T15 |
| INV-A-018 §2 Success evidence/outbox shares commit | E57/E56→E52 | M | K09; atomic event references | S6 posted + S11 pending | OP | EN09 | B-T15 |
| INV-A-019 §3 Half-open economic interval/time basis | E39 basis; E40 start/end/component | M | K18/K19; start<end | S9 calculated→posted | OP | EN06 | B-T03 |
| INV-A-020 §3 Account currency immutable | E35 currency→E39 | M | K15; reject mutation | S7 active | CFG | EN05/EN13 | B-T18 |
| INV-A-021 §3 Segment/rule/rate/job not base key | E40 interval; E42 segments/versions | M | K19 excludes metadata | S9 original/adjustment | OP/REV | EN06 | B-T03 |
| INV-A-022 §3 Non-overlap requires stream serialization | E39 lock→E40 intervals | M | K18 lock + overlap predicate | S9 post | OP | EN06 | B-T03 |
| INV-A-023 §3 First stream creation is race-safe | E39 stable unique row | M | K18 creation conflict/retry | S9 stream creation | OP | EN06 | B-T03,B-T19 |
| INV-A-024 §3 Repartition after posting is adjustment | E42 segments→E41→E40 | M | K20/K19; original retained | S9 correction | REV | EN06 | B-T03,B-T04 |
| INV-A-025 §3 Complete immutable calculation evidence | E42 basis/rate/calendar/rounding/unrounded result | M | UUID/K09 evidence hash | S9 posted evidence | OP/REV | EN06/EN09 | B-T04,B-T18 |
| INV-A-026 §3 Net is base plus adjustments | E40 1:N E41 | M | K19/K20; derived net | S9 read recognized net | OP | EN06 | B-T04 |
| INV-A-027 §3 Locked correction computes delta | E41 prior_net/target/delta/expected_revision | M | K20; E39 chain lock | S9 adjustment post | REV | EN06 | B-T04 |
| INV-A-028 §3 Stale correction requires reauthorization | E41 expected chain revision→E19 | M | K11/K20; reject stale delta | S4 invalidated/reviewed | REV | EN06/EN02 | B-T04,B-T07 |
| INV-A-029 §3 Zero-delta emits evidence without posting | E41 NoChange/E42; batch absent | M | K20 still unique | S9 NoChange | REV | EN06 | B-T04 |
| INV-A-030 §3 Cancel/reversal preserves accrual chain | E41→original E40 | M | K20; original interval retained | S9 linked compensation | REV | EN06/EN08 | B-T04,B-T11 |
| INV-A-031 §3 Loan accrual remains upstream-owned | E68→Lending accrual; E40 deposits only | M/L | K09; no MFI loan accrual balance | U canonical lifecycle | OP | EN03/EN06; U06 pending | B-T09,B-T12 |
| INV-A-032 §4 Evaluate every applicable limit | E21 scopes→E24 allocations | M | K12/K13; all-scope set | S5 reserve | REV | EN02 | B-T05 |
| INV-A-033 §4 Typed scope prevents accidental partition | E21 type/owner/dimensions/window/currency | M | K12; global scope explicit | S5 resolve scopes | OP | EN02 | B-T05 |
| INV-A-034 §4 Rule change cannot reset exposure | E65/E04→stable E21 | M | K12 excludes rule version | S1 amendment preserves S5 | CFG | EN13/EN02 | B-T07 |
| INV-A-035 §4 Missing/conflicting rules deny commitments | E04/E65 applicability | M | K04; conflict predicate | S4/S5 deny | REV | EN13/EN02 | B-T07 |
| INV-A-036 §4 Group changes remap under locks | E64 membership→E21/E26 | M | K06/K12; no lost obligation | S1 amendment | CFG | EN13/EN02 | B-T07 |
| INV-A-037 §4 Policy states included exposure basis | E65 inclusion rule→E26 source obligation | M/L | K14; basis version evidence | S5 reserve/consume | CFG/REV | EN02 | B-T05,B-T12 |
| INV-A-038 §4 Reserved→booked never double counts | E24/E25/E26→E29 | M/L | K14, atomic paired deltas | S5 consumed | OP | EN02/EN03 | B-T06 |
| INV-A-039 §4 Obligation once per applicable scope | E26 obligation/scope/source event | M | K14; no duplicate membership count | S5 projection | OP | EN02 | B-T05,B-T07 |
| INV-A-040 §4 Approval/reservation all-or-none | E19/E20/E23/E24/E57 | M | K11–K14; all scopes locked | S4 approved + S5 reserved | REV | EN02 | B-T05 |
| INV-A-041 §4 Quorum/SoD/delegation uses people | E20 human principal→E66 | M/F | K11; distinct people, bounded delegation | S4 approve | REV | EN02/EN13 | B-T07 |
| INV-A-042 §4 Conservation through immutable events | E23/E24 totals + E26 signed changes | M | K13/K14; O=R+C+L | S5 transitions | OP/REV | EN02 | B-T06,B-T07 |
| INV-A-043 §4 Partial draw limited and atomic | E25/E29 + remaining E24/approval | M/L | K14; scope/reservation/loan locks | S5 partial/consumed | OP | EN03/EN02 | B-T06 |
| INV-A-044 §4 Single currency, no assumed revolving limits | E65 currency/budget semantics→E21 | M | K12; disabled FX | S1 capability/limit policy | CFG | EN13/EN02 | B-T07,B-T13 |
| INV-A-045 §4 Expiry releases only unconsumed amount | E23 expiry→E26 release | M | K14 release identity | S5 expired/released | OP job | EN02 | B-T06 |
| INV-A-046 §4 Repayment does not auto-replenish budgets | E65 budget type→E26/E30 | M/L | K14; rule-specific release | S5 booked decrease | OP | EN02/EN03 | B-T07 |
| INV-A-047 §4 Reversal releases only restored exposure once | E47/E52/E26 | M/L | K22/K14 | S6 reversed + S5 delta | REV | EN08/EN02 | B-T11 |
| INV-A-048 §4 Expiry race and unknown outcomes retain capacity | E23/E25/E52 | M | K13/K14; common locks | S5 consume OR release | OP | EN02 | B-T06,B-T10 |
| INV-A-049 §4 Limit reduction preserves obligations | E65 lower limit→E22/E26 | M | K12 unchanged; deny increase | S1 restricted/S5 retained | CFG | EN13/EN02 | B-T07 |
| INV-A-050 §4 Recheck concurrent policy changes | E01/E03 guard revision→E19 | M | K01/K03/K11; policy lock | S4 reauthorize | REV | EN13/EN02 | B-T07,B-T19 |
| INV-A-051 §5 Global lock order and event-first claim | E54/E03/E21/E23/E35/E39 | M/F/L | K23→policy→scope→reservation→account→stream | S6 transaction | OP | EN04/EN02/EN07; B-BLK-01 | B-T19 |
| INV-A-052 §5 Every writer participates | E38/E23/E39/E26 and scheduled operations | M/L | Same applicable locks | S5/S8/S9 mutation | OP service | EN02/EN05/EN06 | B-T08,B-T19 |
| INV-A-053 §5 Upstream lock conflict cannot be assumed safe | E69 lock graph→U01/U03 | M/F/L | Immutable snapshot evidence | S12 reject unproven | AUD/REV | B-BLK-01; EN12 | B-T19,B-T20 |
| INV-A-054 §5 Deadlock rollback and bounded stable retry | E52/E54 event/outcome | M/F | K09/K23; no new event | S6 retry same | OP | EN04/EN07 | B-T19 |
| INV-A-055 §5 No network/human wait while locked | E69 call graph; E56 deferred dispatch | M/L/F | K09; post-commit effects only | S6 commit→S11 dispatch | OP | EN07/EN09; B-BLK-03 | B-T19,B-T15 |
| INV-A-056 §5 No nested commit/DDL/irreversible local effect | E52/E53 transaction owner | M/L/E/F | One commit; no partial legs | S6 atomic post | OP | EN07/EN12; B-BLK-03 | B-T10,B-T19 |
| INV-A-057 §5 Outbox at-least-once and deduplication | E56 message key→E52 | M | K09; consumer identity | S11 retry/delivered | OP service | EN09 | B-T15 |
| INV-A-058 §5 Lost response reuses durable identity | E54→E52 committed result | M | K23/K09 | S6 read/replay | OP | EN04 | B-T02,B-T10 |
| INV-A-059 §6 All mutation routes converge or deny | E69 route manifest→EN rows | M/F/L/E | Versioned exact-path registry | S12 accept only covered | AUD/REV | EN01–EN13; B-BLK-02 | B-T09,B-T16 |
| INV-A-060 §6 Application/approval/limit guard | E16/E19/E21 | M/L | K10/K11/K12 | S3→S4→S5 | REV | EN02/EN03/EN13 | B-T07,B-T09 |
| INV-A-061 §6 Loan disbursement submit/cancel guard | E29/E25/E47 | L/M | K14/K22 | U submit/cancel | OP/REV | EN03/EN08 | B-T06,B-T09 |
| INV-A-062 §6 Repayment/refund/repost guard | E30/E52/E68 | L/M | K09; funding/date/reversal | U guarded action | OP/REV | EN03/EN07; U06 pending | B-T09,B-T10 |
| INV-A-063 §6 Restructure/write-off/waiver guard | E31/E32/E19/E68 | L/M | K09/K11 | U approved execution | REV | EN03; U06 pending | B-T07,B-T09 |
| INV-A-064 §6 Deposits deny generic raw balance writes | E35/E36/E37/E38 | M | K15–K17 account lock | S6 post | OP | EN05 | B-T08,B-T09 |
| INV-A-065 §6 Accrual/fee corrections guarded for jobs/imports | E39–E42/E52 | M/L | K18–K20 | S9 post/correct | OP/REV | EN06/EN12 | B-T03,B-T04,B-T09 |
| INV-A-066 §6 Native control-account GL guard | E67/E52/E53→E59/E60/E61 | M/E | K25/K09; source voucher role | U submit | OP/REV | EN11; U08 pending | B-T09,B-T10 |
| INV-A-067 §6 Policy/profile changes cannot grant arbitrary power | E07/E58/E65/E66→Role Profile | M/F | K06/K04; assignment allowlist | S1 approved activation | CFG | EN13 | B-T07,B-T17 |
| INV-A-068 §6 Pre-effect recheck; after-submit alone insufficient | E19 revision→U01/U02/U03 | M/L/F | K11 protected revision | U submit boundary | OP | EN03; B-BLK-01/02 | B-T09,B-T19 |
| INV-A-069 §6 Amendment reauthorizes; posted facts immutable | E19 new revision; E37/E40 original | M/L | K11/K19; no overwrite/delete | S4 new request/S9 adjustment | REV | EN03/EN06 | B-T04,B-T07,B-T18 |
| INV-A-070 §6 Raw DB/patch/bypass governed, not request switch | E69 trusted-code manifest/E57 | M/F | UUID approved maintenance source | S12 approval | AUD/CFG | EN12; U09 pending | B-T16 |
| INV-A-071 §6 Scoped jobs retain initiator and policy | E52 actor/origin, E07 scope | M/F | K06/K09; flags not authority | S6 execution | OP service | EN01/EN12 | B-T09,B-T16 |
| INV-A-072 §6 Root/framework trust explicitly outside business RBAC | E69 break-glass/evidence records | M/F | UUID; independent record retention | S12 reviewed | AUD | EN12 | B-T16,B-T20 |
| INV-A-073 §6 Read/file/report/field separate from mutation rights | E58/E13/E14/File→account | M/F | K06; purpose/account distinction | Read only | OP | EN01; U07 pending | B-T01,B-T14 |
| INV-A-074 §7 Model A only proposed, no automatic B fallback | E03 capability→E69 evidence | M | K03; disabled until proof | S1 deny activation | CFG/REV | EN13; B-BLK-03 | B-T17,B-T20 |
| INV-A-075 §7 Same site/company/currency and explicit target mandate | E12/E35→E28/E52 | M/L | K08/K15/K09; target authorization | S6 authorize funding | OP | EN05/EN07 | B-T13 |
| INV-A-076 §7 One balance owner per subledger/GL | E37/E30/E59/E53 | M/L/E respectively | K16/K09; correlation only | S6 post | OP | EN07/EN11 | B-T10,B-T12 |
| INV-A-077 §7 Matched C entries, no extra cash/Payment Entry | E53 voucher roles→E60/E30/E67 | M/L/E | K09/K25; X=X, C=0 | S6 post | OP | EN07/EN11; B-BLK-03 | B-T10 |
| INV-A-078 §7 Supported voucher API, never forced raw GL | E68 upstream voucher→E53 | M/L/E | K09; approved adapter mapping | U canonical post | OP | EN07/EN11/EN12 | B-T10,B-T16 |
| INV-A-079 §7 Unsupported fees/tax/overpay reject | E52 terms→E30 allocation | M/L | K09; approved X preserved | S6 reject incompatible | OP/REV | EN07 | B-T10,B-T13 |
| INV-A-080 §7 Locked canonical allocation and material-change approval | E30 allocation snapshot→E19/E42 | L/M | K11; locked loan basis | S4 reauthorize/S6 post | REV | EN07 | B-T13 |
| INV-A-081 §7 All legs/exposure/audit/batch in one commit | E36/E37/E30/E26/E53/E56/E57 | M/L/E | K09/K14/K16; atomic equality | S6 posted | OP | EN07/EN09; B-BLK-03 | B-T10,B-T15 |
| INV-A-082 §7 Request/lease not financial state | E54 receipt→E52 posted result | M | K23/K09; no partial committed financial state | S6 received/rejected/posted | OP | EN04/EN07 | B-T10 |
| INV-A-083 §7 Every crash/unknown/old-lease outcome resolves once | E52/E54/E56 outcome | M/F | K09/K23; query committed identity | S6 retry or original result | OP | EN04/EN07/EN09 | B-T10,B-T15 |
| INV-A-084 §7 Full reversal once with independent authority | E47→original E52→E30/E36 | M/L/E | K22; original-event/account locks | S4 approved→S6 reversed | REV | EN08 | B-T11 |
| INV-A-085 §7 Unsafe dependencies/closed periods refuse simple reversal | E47/E62/upstream dependency links | M/L/E | K22/K24; preserved originals | S4 deny or new reviewed plan | REV | EN08 | B-T11 |
| INV-A-086 §8 Event equality and zero residual | E53 allocation/source/voucher links | M/L/E | K09; deposit X=loan X; C=0 | S6 before commit | OP | EN07/EN10 | B-T10,B-T12 |
| INV-A-087 §8 Source/GL reconciliation by correct dimensions | E55→E37/E30/E59/E67 | M/L/E | K24/K25; I/company/currency/date | S10 reconcile | REV | EN10 | B-T12 |
| INV-A-088 §8 No netting/plug; opening events traceable | E55 exceptions; E52 opening source | M/E | K24/K09; unresolved blocks | S10 exception/closed | REV | EN10/EN12 | B-T12,B-T16 |
| INV-A-089 §8–9 Complete evidence and all 16 acceptance tests | E69 pins/schema/cases/inputs/results/reviewer | M | UUID immutable evidence manifest | S12 NOT RUN→review | AUD/REV | EN09; acceptance register | B-T20 plus all A-G tests |
| INV-A-090 §9–10 Independent review/001B/001C, no routing or code authority | E69 gate references and review identities | M | UUID; distinct reviewer, no empty pass | S12 blocked until evidence | AUD/REV | Acceptance registry; B-BLK-01/02/03 | B-T20 |

## Coverage disposition

Draft inventory: 90 identifiers; 90 structural mapping rows. Every row names records,
constraints, states, authority, EN references and positive/negative test families.
Ambiguous economic owners in the proposed ownership registry: zero identified.
Duplicate authoritative balances: zero proposed. These are design inspection counts,
not executable pass results, and the invariant extraction itself needs review.

Exact enforceability remains unresolved for the U06–U09 inventories and the
pre-effect/transaction concerns in B-BLK-01/02/03. Consequently no claim of zero
unmapped critical enforcement points is made. `90/90` structural rows do NOT satisfy
the Definition of Done or make 001B READY FOR ACCEPTANCE.

The final acceptance review must confirm the source inventory has no omitted 001A
clause, then resolve every affected EN boundary and test instance with 001C pins
and authorized compatibility evidence. If that work requires changing an invariant,
return the conflict to 001A; do not silently revise it in schema or code.
