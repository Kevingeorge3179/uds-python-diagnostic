# Sprint 3 -- Regression Test Report

**Project:** Python UDS Diagnostics Simulation\
**Sprint:** 3 -- Negative Paths, State/Security Gates & Timeout Edge
Cases\
**Document status:** Regression specification and review record (revised 16 November 2026 after an execution review)\
**Date prepared:** 16 November 2026

## 1. Objective

This report consolidates the 16 regression cases reviewed during Sprint
3D. It checks diagnostic responses and internal ECU state for
session/security gates, invalid requests, S3 timeout behaviour, ECU
reset and DTC history.

A correct diagnostic response alone is not sufficient: the ECU's
internal state must also remain correct.

## 2. Scope and simulation assumptions

### 2.1 Session and security policy

  Service                                 Default (`0x01`)   Extended (`0x03`)   Security required
  ------------------------------------- ------------------ ------------------- -------------------
  `0x10` DiagnosticSessionControl                      Yes                 Yes                  No
  `0x11` ECUReset                                      Yes                 Yes                  No
  `0x22` ReadDataByIdentifier                          Yes                 Yes                  No
  `0x2E` WriteDataByIdentifier (F1A0)                   No                 Yes                 Yes
  `0x3E` TesterPresent                                 Yes                 Yes                  No
  `0x27` SecurityAccess                                 No                 Yes                  No
  `0x31` RoutineControl (FF00)                          No                 Yes                 Yes
  `0x19` ReadDTCInformation                            Yes                 Yes                  No
  `0x14` ClearDiagnosticInformation                    Yes                 Yes                  No

Gate order is session first, then security. Unknown SIDs are rejected by
dispatch lookup with NRC `0x11`; they do not reach the gate function.

Length and format validation happens inside each handler, after the gate.
A too-short request to a protected service while security is locked
therefore returns NRC `0x33`, not `0x13` (for example `2E F1 A0` returns
`7F 2E 33`, and `31 01 FF` returns `7F 31 33`). `0x13` is returned only
once the session and security gates have passed.

### 2.2 Timer and state assumptions

-   Simulated S3 timeout: **2 seconds**.
-   The ECU loop wakes periodically using a receive timeout and checks
    S3.
-   On S3 expiry, the ECU returns to Default Session and re-locks
    SecurityAccess.
-   TesterPresent (`3E 00`) refreshes S3 and returns `7E 00`.
-   `10 03` received while already in Extended Session does not re-lock
    security; only `10 01`, S3 expiry and ECU Reset re-lock it.
-   In this simulation, every received request refreshes
    `last_activity`, including invalid or gate-rejected requests, after
    the timeout check.
-   ECU Reset returns the ECU to Default Session, re-locks security,
    clears the seed, resets routine status and clears the simulated live
    fault state.
-   ECU Reset preserves F1A0 DID data and DTC history.
-   ClearDiagnosticInformation (`0x14`) clears stored DTC history but
    does not repair an active simulated fault. An active fault may be
    recorded again by the fault monitor.
-   `fault_active` represents the current live fault state; `dtc_store`
    represents diagnostic history.
-   DTC `12 34 56` is a simulation placeholder.
-   Status bit 0 (`testFailed`) follows the live fault state; bit 3
    (`confirmedDTC`) is retained in the stored DTC record. Therefore
    inactive-but-confirmed status is `0x08`; active-and-confirmed status
    is `0x09`.

### 2.3 NRC reference

  NRC      Meaning
  -------- ----------------------------------------
  `0x11`   ServiceNotSupported
  `0x12`   SubFunctionNotSupported
  `0x13`   IncorrectMessageLengthOrInvalidFormat
  `0x22`   ConditionsNotCorrect
  `0x24`   RequestSequenceError
  `0x31`   RequestOutOfRange
  `0x33`   SecurityAccessDenied
  `0x35`   InvalidKey
  `0x7E`   SubFunctionNotSupportedInActiveSession
  `0x7F`   ServiceNotSupportedInActiveSession

Negative response format: `7F <requested SID> <NRC>`.

`0x7E` and `0x22` are listed for reference only; the current
implementation does not return them.

## 3. Regression test cases

**Status definitions**

-   **Pass:** The case was executed on 16 Nov 2026 through the full
    ISO-TP bus path against `battery_ecu.py` using an ad-hoc review
    harness (not committed to the repo). Response bytes were compared,
    and internal state was checked with before/after snapshots of
    `did_data` and `dtc_store`, plus a handler-call counter for
    gate-rejected requests.
-   Earlier user-run observations are kept in each case's evidence line.
    The review harness is the source for the state and non-invocation
    checks, which the earlier observations did not cover.

### TC-3C-04 -- Late request after S3 expiry

-   **Preconditions:** Extended Session (`0x03`); wait longer than 2
    seconds without a request.
-   **Request:** `2E F1 A0 12 34`
-   **Expected response:** `7F 2E 7F`
-   **Expected state:** Default Session (`0x01`), security locked, seed
    cleared, F1A0 unchanged.
-   **Actual/evidence:** Shared output showed NRC `0x7F`, session
    `0x01`, security locked and seed `None`. F1A0 displayed `None`; a
    before/after dictionary snapshot was not shown.
-   **Execution review (16 Nov 2026):** Re-executed: response `7F 2E 7F`; session `0x01`, security locked, seed `None`; `did_data` identical before and after; write handler call count 0.
-   **Status:** **Pass**

### TC-3C-02 -- TesterPresent refreshes S3

-   **Preconditions:** Enter Extended Session; S3 timeout is 2 seconds.
-   **Request:** After approximately 1.5 seconds, send `3E 00`.
-   **Expected response:** `7E 00`.
-   **Expected state:** Remains Extended after TesterPresent; still
    Extended at approximately 2.5 seconds from initial entry; returns to
    Default after more than 2 seconds from TesterPresent.
-   **Actual/evidence:** Shared output showed `7E 00`, Extended at
    approximately 2.5 seconds and Default at approximately 3.7 seconds.
-   **Execution review (16 Nov 2026):** Re-executed: response `7E 00`; session still `0x03` about 2.5 s after entry; session `0x01` after a further 2.2 s.
-   **Status:** **Pass**

### TC-3C-03 -- Security re-lock on S3 expiry

-   **Preconditions:** Extended Session and SecurityAccess unlocked; no
    requests for longer than 2 seconds.
-   **Request:** No request during expiry.
-   **Expected response:** No UDS response is generated merely by idle
    expiry.
-   **Expected state:** Default Session (`0x01`),
    `security_unlocked == False`, `security_seed is None`.
-   **Actual/evidence:** Shared timeout output showed Default Session,
    security locked and seed `None`.
-   **Execution review (16 Nov 2026):** Re-executed with security actually unlocked beforehand (pre-check confirmed Extended and unlocked): after 2.2 s idle, session `0x01`, `security_unlocked == False`, seed `None`; a following `2E` returned `7F 2E 7F`. Note: `main_1.py` does not perform the unlock step, so it does not by itself demonstrate this case.
-   **Status:** **Pass**

### TC-3B-01 -- Protected service in Default Session

-   **Preconditions:** Default Session, security locked.
-   **Request:** `2E F1 A0 12 34`
-   **Expected response:** `7F 2E 7F`
-   **Expected state:** Remains Default and locked; write handler not
    called; F1A0 unchanged.
-   **Actual/evidence:** Shared gate regression sequence returned NRC
    `0x7F`. Handler non-invocation and data preservation were not
    independently instrumented.
-   **Execution review (16 Nov 2026):** Executed: response `7F 2E 7F`; write handler call count 0; `did_data` unchanged; session `0x01`.
-   **Status:** **Pass**

### TC-3B-02 -- Protected service in Extended Session while locked

-   **Preconditions:** Extended Session, security locked.
-   **Request:** `2E F1 A0 12 34`
-   **Expected response:** `7F 2E 33`
-   **Expected state:** Remains Extended and locked; F1A0 unchanged.
-   **Actual/evidence:** Shared gate sequence returned NRC `0x33`.
-   **Execution review (16 Nov 2026):** Executed: response `7F 2E 33`; write handler call count 0; `did_data` unchanged; session `0x03`, still locked.
-   **Status:** **Pass**

### TC-3B-03 -- Successful protected write

-   **Preconditions:** Extended Session, security unlocked.
-   **Request:** `2E F1 A0 12 34`
-   **Expected response:** `6E F1 A0`
-   **Expected state:** F1A0 stores bytes `12 34`; session remains
    Extended and security remains unlocked.
-   **Actual/evidence:** Shared gate sequence returned `6E F1 A0` after
    SecurityAccess unlock.
-   **Execution review (16 Nov 2026):** Executed: response `6E F1 A0`; F1A0 holds `12 34`; readback `22 F1 A0` returned `62 F1 A0 12 34`; session `0x03`, unlocked.
-   **Status:** **Pass**

### TC-3B-04 -- Unsupported SID

-   **Preconditions:** Any session.
-   **Request:** `99 01 02`
-   **Expected response:** `7F 99 11`
-   **Expected state:** Unknown SID is rejected by dispatch; no
    handler/gate policy or diagnostic data mutation.
-   **Actual/evidence:** Shared gate sequence returned NRC `0x11`.
-   **Execution review (16 Nov 2026):** Executed in Default and in Extended: response `7F 99 11` both times; `did_data` and `dtc_store` unchanged.
-   **Status:** **Pass**

### TC-3C-05 -- Invalid SecurityAccess key

-   **Preconditions:** Extended Session, security locked; request seed
    using `27 01`.
-   **Request:** `27 02` with an incorrect key.
-   **Expected response:** `7F 27 35`
-   **Expected state:** Security remains locked; seed invalidated
    (`None`).
-   **Actual/evidence:** Reviewed as a negative-path case; no separate
    execution output recorded.
-   **Execution review (16 Nov 2026):** Executed: response `7F 27 35`; `security_unlocked == False`; seed `None`.
-   **Status:** **Pass**

### TC-3C-06 -- Key requested without seed

-   **Preconditions:** Extended Session, security locked, no seed
    stored.
-   **Request:** `27 02`
-   **Expected response:** `7F 27 24`
-   **Expected state:** Security remains locked; seed remains `None`.
-   **Actual/evidence:** Sequence-error behaviour reviewed; no separate
    execution output recorded.
-   **Execution review (16 Nov 2026):** Executed: response `7F 27 24`; `security_unlocked == False`; seed `None`.
-   **Status:** **Pass**

### TC-3C-07 -- Unsupported DID

-   **Preconditions:** Extended Session, security unlocked.
-   **Request:** `2E F1 B0 12 34`
-   **Expected response:** `7F 2E 31`
-   **Expected state:** DID dictionary unchanged; F1B0 is not created.
-   **Actual/evidence:** Handler DID validation was reviewed; no
    before/after dictionary snapshot recorded.
-   **Execution review (16 Nov 2026):** Executed: response `7F 2E 31`; `did_data` unchanged; F1B0 not created.
-   **Status:** **Pass**

### TC-3C-08 -- RoutineControl with unsupported RID

-   **Preconditions:** Extended Session, security unlocked, routine
    status `COMPLETED`.
-   **Request:** `31 01 FF 01`
-   **Expected response:** `7F 31 31`
-   **Expected state:** Routine status and fault state unchanged.
-   **Actual/evidence:** Handler-level checks in
    `test_routine_control.py` (27 assertions across 9 cases); script
    completed without traceback.
-   **Execution review (16 Nov 2026):** Executed through the full path (unlock, `31 01 FF 00` returned `71 01 FF 00`, then `31 01 FF 01`): response `7F 31 31`; routine status `COMPLETED`; fault active. Separately, `test_routine_control.py` checks the handler directly: it calls `handle_routine_control` with `routine_status` and `fault_active` set by hand and does not set session or security, so it is a handler-level unit test, not a gated end-to-end case.
-   **Status:** **Pass**

### TC-3C-09 -- StartRoutine when already completed

-   **Preconditions:** Extended Session, security unlocked, RID FF00,
    routine status `COMPLETED`.
-   **Request:** `31 01 FF 00`
-   **Expected response:** `7F 31 24`
-   **Expected state:** Routine status remains `COMPLETED`; fault state
    unchanged.
-   **Actual/evidence:** Handler-level checks in
    `test_routine_control.py` (27 assertions across 9 cases); script
    completed without traceback.
-   **Execution review (16 Nov 2026):** Executed through the full path: response `7F 31 24`; routine status remains `COMPLETED`; fault active. Also covered at handler level by `test_routine_control.py` (see TC-3C-08 note).
-   **Status:** **Pass**

### TC-3A-01 -- Extended Session to Default Session

-   **Preconditions:** Extended Session (`0x03`), security unlocked.
-   **Request:** `10 01`
-   **Expected response:** `50 01 00 32 01 F4`
-   **Expected state:** `current_session = 0x01`;
    `security_unlocked = False`; `security_seed = None`.
-   **Actual/evidence:** Correct response and state transition were
    reasoned through; no separate execution output recorded.
-   **Execution review (16 Nov 2026):** Executed: response `50 01 00 32 01 F4`; session `0x01`; security locked; seed `None`.
-   **Status:** **Pass**

### TC-3A-02 -- ECU Reset while Extended and unlocked

-   **Preconditions:** Extended Session, security unlocked; F1A0 data
    and DTC history populated.
-   **Request:** `11 01`
-   **Expected response:** `51 01`
-   **Expected state:** Default Session; security locked; seed cleared;
    routine status `NOT_STARTED`; simulated `fault_active = False`. F1A0
    data and DTC history preserved.
-   **Actual/evidence:** Correct behaviour was recalled and explained;
    no separate execution output recorded.
-   **Execution review (16 Nov 2026):** Executed: response `51 01`; session `0x01`; security locked; seed `None`; routine `NOT_STARTED`; `fault_active == False`; F1A0 still `12 34`; DTC `12 34 56` preserved (one record).
-   **Status:** **Pass**

### TC-3C-10 -- Invalid WriteDataByIdentifier length

-   **Preconditions:** Extended Session, security unlocked, F1A0 already
    contains data.
-   **Request:** `2E F1 A0`
-   **Expected response:** `7F 2E 13`
-   **Expected state:** Session/security unchanged; existing F1A0 data
    unchanged.
-   **Actual/evidence:** User correctly traced dispatch, gates and
    handler length validation; no separate execution output recorded.
-   **Execution review (16 Nov 2026):** Executed: response `7F 2E 13`; F1A0 unchanged; session `0x03`, still unlocked.
-   **Status:** **Pass**

### TC-2C-01 -- DTC history after ECU Reset

-   **Preconditions:** Fault activated and DTC `12 34 56` recorded; ECU
    Reset then clears live fault state but preserves DTC history.
-   **Request:** `19 02 FF`
-   **Expected response:** `59 02 09 12 34 56 08` (positive response,
    sub-function `02`, availability mask `09`, then the single stored
    DTC `12 34 56` with status `08`).
-   **Expected state:** `fault_active = False`; DTC remains in
    `dtc_store`; status byte `0x08` (confirmed bit set, testFailed bit
    clear).
-   **Actual/evidence:** User correctly explained why the stored DTC
    remains reportable with status `0x08`, not `0x09`; no separate
    execution output recorded.
-   **Execution review (16 Nov 2026):** Executed after ECU Reset: response `59 02 09 12 34 56 08` (availability mask `09`, then DTC `12 34 56`, status `08`). Corrected from an earlier expected value that was written incorrectly.
-   **Status:** **Pass**

## 4. Execution summary

  Evidence category                          Cases
  ------------------------------------------ ------------------------------------------
  Executed 16 Nov 2026, full path,           All 16 cases: TC-3C-04, 3C-02, 3C-03,
  state-checked (all pass)                   3C-05, 3C-06, 3C-07, 3C-08, 3C-09, 3C-10,
                                             TC-3B-01, 3B-02, 3B-03, 3B-04, TC-3A-01,
                                             3A-02, TC-2C-01
  Reviewed only (no execution evidence)      None

The review harness used for this execution is not part of the repo.
Moving these cases into a committed, repeatable suite is Sprint 4 work.
Until then, "pass" in this report means executed once on 16 Nov 2026.

## 5. Known limitations and observations

1.  RoutineControl is synchronous: StartRoutine transitions immediately
    to `COMPLETED`, making a normal StopRoutine success path unreachable
    in the current design.
2.  Routine validation order is simulation-specific: message length,
    subfunction, RID, routine state, then execution. An unsupported RID
    therefore returns NRC `0x31` even if the routine is completed.
3.  SecurityAccess uses a simplified XOR seed/key algorithm for
    learning, not production security.
4.  DTC `12 34 56` is a placeholder, not a real vehicle DTC.
5.  Session/security restrictions are this project's chosen policy.
    Actual ECU permissions are defined by the OEM diagnostic
    specification.
6.  Timeout boundary behaviour depends on loop scheduling. The ECU
    checks expiry before processing a received request; a late request
    is evaluated after return to Default if expiry is detected on that
    receive-loop iteration.
7.  This report is not a claim of complete automated coverage. Automated
    regression, parameterized runs and pass/fail reporting belong to
    Sprint 4.
8.  Security is checked before message length, so a malformed request to
    a protected service returns `0x33` while locked and `0x13` only when
    unlocked. Some ECUs validate length earlier; this ordering is a
    deliberate simulation choice.
9.  `10 03` while already in Extended Session leaves security unlocked.
    Some ECUs re-lock on any session transition.
10. A service present in `dispatch_table` but missing from `gate_policy`
    raises `KeyError` inside the ECU loop and stops the ECU thread; the
    tester then receives no responses. There is no per-request exception
    handling. Keep the two tables in sync, or add a start-up consistency
    check.
11. `test_routine_control.py` calls handlers directly, so it bypasses
    dispatch and gates. It complements, and does not replace, the
    full-path cases.
12. The Sprint 3E runnable NRC matrix (a data-driven table with pass/fail
    output) was not built in Sprint 3 and is carried into Sprint 4.

## 6. Recommended next actions

1.  Sprint 4: build a data-driven runner (precondition steps, request,
    expected response, expected state) that reproduces these 16 cases
    with pass/fail output, then parameterize it.
2.  Add a raw-response helper to the tester so cases can assert on
    bytes. The per-service validator refactor is a separate Sprint 4
    item.
3.  Add a start-up check that `dispatch_table` and `gate_policy` have
    matching keys.
4.  Decide whether `10 03` should re-lock security, and whether length
    should be checked before security; update the policy table either
    way.

## 7. Sprint 3 conclusion

Sprint 3 established the negative-path, session/security-gate and
S3-timeout behaviour of the UDS simulation. All 16 regression cases were
executed on 16 Nov 2026 and pass, including state preservation and
handler non-invocation checks. Two simulation behaviours (security
before length; `10 03` not re-locking) are documented as deliberate
choices. The runnable test matrix planned as Sprint 3E moves to Sprint 4.

**Sprint 3D deliverable:** Regression test specification and review
record (all 16 cases executed).\
**Next roadmap item:** Sprint 4 -- runnable NRC test matrix (carried
from 3E), automated tests, pass/fail summary, parameterized runs and
tester refactoring.
