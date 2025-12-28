# CBT Assessment - Clinician Review Workflow Design

**Date Created:** 2025-12-26
**Last Updated:** 2025-12-27
**Status:** 🟢 In Progress - Phase 1 Complete
**Purpose:** Design and implement the assessment review and approval workflow

---

## Executive Summary

**Current Problem:** The application automatically advances users to the next step upon completing an assessment. This doesn't match the real-world requirement where assessments must be reviewed and approved by clinicians/psychologists before participants can progress.

**Impact:** This is a fundamental architectural change that affects:
- Database schema (new models needed)
- User flow (no auto-advancement)
- Application features (need clinician portal)

**Decision Point:** We need to understand the real-world workflow at the correctional facility before implementing the solution.

---

## Table of Contents

1. [Current vs. Required Flow](#current-vs-required-flow)
2. [Questions to Answer](#questions-to-answer)
3. [Workflow Options](#workflow-options)
4. [Database Changes Needed](#database-changes-needed)
5. [Implementation Phases](#implementation-phases)
6. [Decision Log](#decision-log)

---

## Current vs. Required Flow

### Current Implementation (Incorrect)
```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User logs in                                                 │
│ 2. Dashboard shows "Step 1"                                     │
│ 3. User clicks "Start Assessment"                               │
│ 4. User answers questions one-by-one                            │
│ 5. User completes final question                                │
│ 6. System shows "Assessment Complete"                           │
│ 7. ❌ System AUTOMATICALLY advances to Step 2                    │
│ 8. Dashboard now shows "Step 2"                                 │
└─────────────────────────────────────────────────────────────────┘

Problem: No clinician review, no approval gate
```

### Required Implementation
```
┌─────────────────────────────────────────────────────────────────┐
│ PARTICIPANT SIDE:                                               │
│ 1. User logs in                                                 │
│ 2. Dashboard shows "Step 1"                                     │
│ 3. User clicks "Start Assessment"                               │
│ 4. User answers questions one-by-one                            │
│ 5. User completes final question                                │
│ 6. System shows "Assessment Complete - Pending Review"          │
│ 7. ⏸️  User CANNOT start Step 2 yet                             │
│ 8. Dashboard shows "Step 1 - Awaiting Clinician Review"         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ CLINICIAN SIDE:                                                 │
│ 1. Clinician logs into separate portal                          │
│ 2. Sees list of "Pending Assessments"                           │
│ 3. Clicks on participant's assessment                           │
│ 4. Reviews all responses                                        │
│ 5. Makes decision: Approve / Request Revision / Reject          │
│ 6. (Optional) Adds notes/feedback                               │
│ 7. Submits review                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ BACK TO PARTICIPANT:                                            │
│ - If APPROVED: Dashboard now shows "Step 2 Available"           │
│ - If NEEDS REVISION: Shows feedback, allows re-submission       │
│ - If REJECTED: [Decision needed - see below]                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Questions to Answer

### 🔴 Critical Questions (Must answer before coding)

#### Q1: What happens when an assessment is rejected/failed?
**Options:**
- [ ] **A.** Participant retakes the entire assessment (all responses deleted)
- [ ] **B.** Participant can revise their answers (responses preserved, editable)
- [ ] **C.** Participant must complete additional education/counseling first, then retake
- [ ] **D.** Other: _______________

**Decision:** _[To be filled in]_

**Notes:** _[Add context from conversation with ex-colleague]_

---

#### Q2: Is there a scoring/grading system?
**Options:**
- [ ] **A.** Simple Pass/Fail (binary decision)
- [ ] **B.** Numeric score (e.g., 0-100 or 1-5 rating)
- [ ] **C.** Rubric-based (different criteria weighted)
- [ ] **D.** Subjective evaluation (clinician judgment, no formal score)

**Decision:** _[To be filled in]_

**Notes:** _[Add details about scoring criteria]_

---

#### Q3: Do clinicians provide written feedback to participants?
**Options:**
- [ ] **A.** Yes, detailed feedback on each answer
- [ ] **B.** Yes, general comments on overall assessment
- [ ] **C.** No written feedback, discussed in person
- [ ] **D.** Only feedback when revision needed

**Decision:** _[To be filled in]_

**Notes:** _[How is feedback delivered?]_

---

#### Q4: Are participants assigned to specific clinicians?
**Options:**
- [ ] **A.** Yes, each participant has one assigned clinician
- [ ] **B.** No, any clinician can review any assessment (shared queue)
- [ ] **C.** Hybrid (assigned, but others can help with backlog)

**Decision:** _[To be filled in]_

**Implications:**
- Option A requires assignment logic in database
- Option B simpler, but less personal
- Option C requires permission/override system

---

#### Q5: Can participants retake assessments? How many times?
**Options:**
- [ ] **A.** Unlimited retakes until approved
- [ ] **B.** Limited retakes (e.g., 3 attempts max)
- [ ] **C.** Only one retake allowed
- [ ] **D.** No retakes - must wait for remedial program

**Decision:** _[To be filled in]_

**Notes:** _[What happens after max attempts?]_

---

### 🟡 Important Questions (Affects features, not core flow)

#### Q6: How quickly do assessments need review?
- [ ] Same day (clinician on-site daily)
- [ ] Within 48 hours
- [ ] Within one week
- [ ] No specific timeline

**Decision:** _[To be filled in]_

**Impact:** Affects whether we need notification system

---

#### Q7: Who needs access to this system?
- [ ] Participants/Inmates (already built)
- [ ] Clinicians/Counselors (need to build)
- [ ] Supervisors/Program Directors (need to build)
- [ ] Administrators (need to build)
- [ ] Other: _______________

**Decision:** _[To be filled in]_

---

#### Q8: Is there an in-person component to the review?
**Context:**
- [ ] Clinician reviews responses alone, makes decision
- [ ] Clinician reviews, then discusses with participant in person
- [ ] Review happens during scheduled counseling session
- [ ] Other: _______________

**Decision:** _[To be filled in]_

**Impact:** If in-person, app might just be record-keeping tool

---

#### Q9: Privacy and audit requirements
**Need to track:**
- [ ] Who viewed which participant's responses (audit log)
- [ ] When responses were viewed
- [ ] Who approved/rejected assessments
- [ ] HIPAA or similar protections required

**Decision:** _[To be filled in]_

---

#### Q10: Notification preferences
- [ ] **A.** No notifications (users check dashboard)
- [ ] **B.** Email notifications (when assessment approved/rejected)
- [ ] **C.** In-app notifications (bell icon with alerts)

**Decision:** _[To be filled in]_

**Note:** In correctional settings, email might not be available

---

## Workflow Options

Based on common correctional treatment programs, here are three potential workflows:

### Option A: Simple Binary Approval

**Process:**
1. Participant completes assessment → Status: "Pending Review"
2. Clinician views responses in dashboard
3. Clinician clicks one button: "Approve" or "Needs Retake"
4. If approved → Participant can start next step
5. If rejected → All responses deleted, participant starts over

**Pros:**
- Simplest to implement
- Clear, unambiguous outcomes
- Minimal database changes

**Cons:**
- No granular feedback
- Participant loses all work if rejected
- No opportunity for learning/revision

**Best for:** Programs with straightforward pass/fail criteria

---

### Option B: Review with Revision Capability

**Process:**
1. Participant completes assessment → Status: "Pending Review"
2. Clinician reviews each response
3. Clinician can:
   - Mark specific answers as "needs revision"
   - Add comments/feedback per question
   - Or approve entire assessment
4. If needs revision:
   - Participant sees feedback
   - Can edit flagged answers only
   - Resubmits for review
5. Clinician reviews revisions → Approves
6. Participant advances to next step

**Pros:**
- Educational - participant learns from feedback
- Doesn't waste good answers
- More granular control
- Better aligns with CBT principles (reflection & growth)

**Cons:**
- More complex UI needed
- More database fields
- Potential for many revision cycles

**Best for:** Treatment programs focused on personal growth

---

### Option C: Scored Evaluation with Threshold

**Process:**
1. Participant completes assessment
2. System auto-scores multiple choice questions (if applicable)
3. Status: "Pending Review"
4. Clinician reviews written responses
5. Clinician assigns score or rating (e.g., 1-5 scale)
6. Total score calculated
7. If score ≥ threshold (e.g., 70%) → Auto-approved
8. If score < threshold → Needs retake or revision
9. Scores tracked over time for progress reports

**Pros:**
- Quantifiable progress
- Can generate reports/analytics
- Clear success criteria
- Supervisor can spot-check borderline cases

**Cons:**
- Requires defining scoring rubrics
- May not capture qualitative progress
- More complex calculations

**Best for:** Programs with structured evaluation criteria

---

### Option D: Hybrid Approach (Recommended)

**Process:**
1. Participant completes assessment → Status: "Submitted"
2. Clinician reviews in dashboard
3. Clinician chooses outcome:
   - **Approve** → Participant advances to next step
   - **Needs Revision** → Adds feedback, participant can edit & resubmit
   - **Refer to Supervisor** → Escalates complex cases
4. (Optional) Clinician can assign informal rating for tracking
5. All decisions logged with timestamp and clinician ID

**Pros:**
- Flexible for different situations
- Supports learning without being punitive
- Audit trail for accountability
- Room for growth as program evolves

**Cons:**
- Slightly more complex than Option A
- Requires good UX design

**Best for:** Real-world programs with diverse participant needs

---

## Database Changes Needed

### New Models Required

#### 1. AssessmentAttempt
**Purpose:** Track each time a participant attempts an assessment (not just completion)

```python
class AssessmentAttempt(db.Model):
    """Tracks assessment attempts and review status"""
    __tablename__ = 'assessment_attempts'

    attempt_id = db.Column(db.Integer, primary_key=True)
    prison_id = db.Column(db.String(50), db.ForeignKey('users.prison_id'))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.assessment_id'))

    # Attempt tracking
    attempt_number = db.Column(db.Integer, default=1)  # 1st attempt, 2nd, etc.
    started_at = db.Column(db.DateTime)
    submitted_at = db.Column(db.DateTime)

    # Review status
    status = db.Column(db.String(20))
    # Values: 'in_progress', 'submitted', 'under_review',
    #         'approved', 'needs_revision', 'rejected'

    # Clinician review
    reviewed_by = db.Column(db.String(50), db.ForeignKey('clinicians.clinician_id'))
    reviewed_at = db.Column(db.DateTime)
    clinician_notes = db.Column(db.Text)

    # Optional scoring
    score = db.Column(db.Integer)  # 0-100 or null if not scored

    # Relationships
    responses = db.relationship('Response', backref='attempt', lazy=True)
```

**Why we need this:**
- Tracks multiple attempts if participant retakes
- Separates "in progress" from "submitted for review"
- Links all responses to a specific attempt
- Stores review outcome and feedback

---

#### 2. Clinician
**Purpose:** Separate user accounts for clinical staff

```python
class Clinician(db.Model, UserMixin):
    """Clinical staff who review assessments"""
    __tablename__ = 'clinicians'

    clinician_id = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True)
    password_hash = db.Column(db.String(200), nullable=False)

    # Role-based access
    role = db.Column(db.String(20), default='clinician')
    # Values: 'clinician', 'supervisor', 'admin'

    # Optional: Assignment tracking
    is_active = db.Column(db.Boolean, default=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reviewed_attempts = db.relationship('AssessmentAttempt',
                                       backref='reviewer', lazy=True)
    assigned_participants = db.relationship('User',
                                           backref='assigned_clinician',
                                           lazy=True)
```

**Why we need this:**
- Separate login from participants
- Track who reviewed what (accountability)
- Support multiple clinicians
- Role-based permissions (clinician vs supervisor vs admin)

---

#### 3. Modified: Response Model
**Change:** Link responses to an attempt, not just a question

```python
class Response(db.Model):
    """User responses to questions"""
    __tablename__ = 'responses'

    response_id = db.Column(db.Integer, primary_key=True)

    # NEW: Link to attempt instead of just user
    attempt_id = db.Column(db.Integer,
                          db.ForeignKey('assessment_attempts.attempt_id'))

    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'))

    # Response data
    response_text = db.Column(db.Text)
    selected_option_id = db.Column(db.Integer,
                                  db.ForeignKey('multiple_choice_options.option_id'))

    # NEW: Clinician feedback on individual responses (optional)
    clinician_comment = db.Column(db.Text)
    needs_revision = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

**Why this change:**
- Can track multiple attempts with different answers
- Supports revision workflow
- Clinician can comment on specific answers
- Clear history of what was answered when

---

#### 4. Modified: User Model
**Change:** Add clinician assignment

```python
class User(db.Model, UserMixin):
    """Participant taking assessment"""
    __tablename__ = 'users'

    prison_id = db.Column(db.String(50), primary_key=True)
    # ... existing fields ...

    # NEW: Optional assigned clinician
    assigned_clinician_id = db.Column(db.String(50),
                                     db.ForeignKey('clinicians.clinician_id'))

    # Relationships
    attempts = db.relationship('AssessmentAttempt', backref='user', lazy=True)
```

---

### Database Migration Considerations

**Important:** This is a breaking change to the schema.

**Options:**
1. **Start fresh** - Drop existing database, recreate with new schema
2. **Migration script** - Write script to convert existing data
3. **Parallel tables** - Keep old, add new, migrate gradually

**Recommendation:** Since you're in early development with test data only, **Option 1 (start fresh)** is simplest.

**Action items:**
- [ ] Back up existing database (if any real data)
- [ ] Create new migration script
- [ ] Update `init_db.py` to create new tables
- [ ] Create script to seed test clinician accounts

---

## Implementation Phases

### Phase 1: Database & Core Models ✅ COMPLETE
**Goal:** Get the data structure right

**Tasks:**
- [x] Create new models (AssessmentAttempt, Clinician)
- [x] Modify existing models (Response, User)
- [x] Write migration/fresh db script
- [x] Create test data script (participants + clinicians)
- [x] Test relationships work correctly

**Deliverable:** Database schema that supports review workflow

**Completed:** 2025-12-27
**Notes:** All models created and tested. Database includes 8 tables with proper relationships. Test data script creates 2 participants and 2 clinicians.

---

### Phase 2: Modified Participant Flow (Week 1-2)
**Goal:** Stop auto-advancement, add status tracking

**Tasks:**
- [ ] Modify `assessment_complete()` route - remove auto-advancement
- [ ] Create AssessmentAttempt when user starts assessment
- [ ] Link responses to attempt_id
- [ ] Update dashboard to show attempt status
- [ ] Add "Pending Review" / "Approved" / "Needs Revision" states
- [ ] Prevent starting next step if current not approved

**Deliverable:** Participants can complete but not auto-advance

---

### Phase 3: Clinician Login & Authentication (Week 2)
**Goal:** Separate login for clinical staff

**Tasks:**
- [ ] Create clinician login page (separate from participant)
- [ ] Add user_loader for clinician accounts
- [ ] Create clinician registration/management (admin only)
- [ ] Add role-based access control
- [ ] Test clinician can log in separately

**Deliverable:** Clinicians can log into separate portal

---

### Phase 4: Clinician Review Dashboard (Week 2-3)
**Goal:** Let clinicians see and review assessments

**Tasks:**
- [ ] Create clinician dashboard page
- [ ] List all pending assessments (table view)
- [ ] Filter by status, date, participant
- [ ] Click to view assessment details
- [ ] Show all responses for one assessment
- [ ] Display participant info safely (privacy)

**Deliverable:** Clinicians can view pending work

---

### Phase 5: Review & Approval Actions (Week 3)
**Goal:** Let clinicians approve/reject assessments

**Tasks:**
- [ ] Add "Approve" button on review page
- [ ] Add "Request Revision" with comment field
- [ ] (Optional) Add "Reject" option
- [ ] Update AssessmentAttempt status in database
- [ ] Log reviewer, timestamp, notes
- [ ] Test approval unlocks next step for participant

**Deliverable:** Basic review workflow complete

---

### Phase 6: Revision Workflow (Week 3-4)
**Goal:** Let participants revise based on feedback

**Tasks:**
- [ ] Show clinician notes to participant
- [ ] Allow editing responses (if revision workflow chosen)
- [ ] Track revision as same attempt vs new attempt
- [ ] Resubmit for review
- [ ] Clinician sees "revised" status

**Deliverable:** Full revision loop working

---

### Phase 7: Polish & Features (Week 4+)
**Goal:** Make it production-ready

**Tasks:**
- [ ] Add scoring system (if decided)
- [ ] Add notifications (if decided)
- [ ] Add audit logs
- [ ] Add clinician assignment
- [ ] Add reporting/analytics
- [ ] Add supervisor oversight features
- [ ] Security hardening
- [ ] User testing with ex-colleague

**Deliverable:** Production-ready system

---

## Decision Log

**Instructions:** Fill this out as decisions are made. Date each decision.

### Workflow Choice
**Date:** 2025-12-27
**Decision:** Option D (Hybrid Approach)
**Rationale:**
- Most flexible for different situations
- Supports learning without being punitive (revision capability)
- Audit trail for accountability
- Room for program to evolve based on real-world needs

**Implementation Details:**
- Clinician can Approve, Request Revision, or Refer to Supervisor
- Optional informal rating/scoring for progress tracking
- All decisions logged with timestamp and clinician ID


---

### Retake Policy
**Date:** __________
**Decision:**


**Max attempts allowed:**


**What happens after max attempts:**


---

### Scoring System
**Date:** __________
**Will use scoring:** Yes / No
**If yes, scoring method:**


**Passing threshold:**


---

### Clinician Assignment
**Date:** __________
**Assignment method:**


**Can be reassigned:** Yes / No


---

### Notification Method
**Date:** __________
**Notification type:**


**Implementation priority:** High / Medium / Low


---

### Additional Decisions
**Date:** __________
**Topic:**


**Decision:**


**Impact:**


---

## Next Steps

### ✅ Completed (2025-12-27)
- [x] Chose Option D (Hybrid Approach) for workflow
- [x] Designed complete database schema
- [x] Implemented Phase 1 (Database & Core Models)
- [x] Created AssessmentAttempt and Clinician models
- [x] Modified Response and User models
- [x] Built test data creation scripts

### For Next Session (Phase 2: Modified Participant Flow)

**Tasks:**
1. Modify `app/routes.py` to create AssessmentAttempt when user starts assessment
2. Remove auto-advancement code from assessment completion
3. Update dashboard template to show attempt status (Pending/Approved/Needs Revision)
4. Prevent users from starting next step until current is approved
5. Test participant flow with new workflow

**Goal:** Participants can complete assessments but cannot auto-advance. Status tracking in place.

**Estimated Time:** 30-45 minutes of guided implementation

---

## References

**Related Files:**
- `TODO.md` - Technical debt and bug fixes
- `README.md` - Current project documentation
- `app/models.py` - Current database schema
- `app/routes.py` - Current workflow (needs changes)

**External Resources:**
- 12-Step Program Standards
- Correctional Treatment Program Guidelines
- CBT Assessment Best Practices

---

## Questions or Notes

Use this section to jot down anything that comes up:

**Questions:**
1.
2.
3.

**Concerns:**
1.
2.

**Ideas:**
1.
2.

---

**Document Status:** Draft
**Last Updated:** 2025-12-26
**Next Review:** [Tomorrow's session]
