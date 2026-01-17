# CBT Assessment - Technical Debt & Improvements

**Last Updated:** 2026-01-17

**GitHub Project Board:** [CBT12 Project](https://github.com/timLP79/cbt12/projects/10)
**All issues below have been created in GitHub and added to the project board.**

## 🚀 Post-Deployment Tasks (January 6, 2026)

**1. Database Content Update (Issue #21)**
Assessments for Steps 2-12 have been added. Run the seed script on production:
```bash
# Connect via SSH first, load environment variables
python add_full_assessments.py
```

**2. Critical: Production Database Schema Update (Issue #9)**
The latest update adds a `UniqueConstraint` to the `responses` table. Since Alembic is not yet implemented, this must be applied manually to the AWS RDS instance after the code is deployed.

1. **Check for existing duplicates (Postgres):**
   ```sql
   SELECT attempt_id, question_id, COUNT(*)
   FROM responses
   GROUP BY attempt_id, question_id
   HAVING COUNT(*) > 1;
   ```

2. **Apply the constraint (Postgres):**
   ```sql
   ALTER TABLE responses
   ADD CONSTRAINT uq_attempt_question UNIQUE (attempt_id, question_id);
   ```

---

## ✅ Recently Completed

### Phase 8: UI Modernization - COMPLETE (2026-01-17)
- ✅ **UI Redesign** - Modern teal/cyan design with bold typography and animations (Issue #37)
- ✅ **Dark Mode** - Full dark theme with toggle button and localStorage persistence
- ✅ **CSS Variables** - Implemented theming system for easy customization
- ✅ **Design Options** - Created 4 design branches for testing (A, B, C, D)
- ✅ **Default Dark Mode** - Set dark mode as default for reduced eye strain

### Phase 7: Participant Features & Data Integrity - COMPLETE (2026-01-06)
- ✅ **Mobile Responsiveness** - Optimized layout for mobile devices (Issue #24)
- ✅ **CSS Consolidation** - Moved inline and internal styles to external style.css (Issue #20)
- ✅ **Null Checks** - Added defensive checks in templates for missing data (Issue #10)
- ✅ **Session Cleanup** - Implemented session.clear() on logout (Issue #8)
- ✅ **Content Expansion** - Added full assessments for Steps 2-12 (5 questions each) (Issue #21)
- ✅ **Participant Profile & History** - Added detailed admin view for user history and progress (Issue #22)
- ✅ **Resume Assessment** - Added logic to resume in-progress attempts and update saved answers (Issue #23)
- ✅ **Duplicate Response Prevention** - Added database-level UniqueConstraint to Response model (Issue #9)
- ✅ **UI/UX Polish** - Added "Save and Exit" and pre-filled responses in assessment flow
- ✅ **State ID Validation** - Enforced strict `[A-Z]{2}[0-9]{4,10}` format for State IDs (Issue #25)
- ✅ **Code Cleanup** - Fixed Limiter initialization syntax and typos

### Phase 6: Admin Dashboard Expansion & Polish - COMPLETE (2026-01-04)

**Feature Enhancements:**
- ✅ **User Management CRUD** - Full system to Create, Read, Update, and Deactivate participants (Issue #1, #2)
- ✅ **Admin Management CRUD** - Supervisor-only system to Create, Read, Update, and Deactivate admins
- ✅ **Blueprints Refactoring** - Reorganized application into modular blueprints (`main`, `admin`, `manage`)
- ✅ **Assessment History** - Added view for participants to see previous approved/reviewed attempts (Issue #3)
- ✅ **Approval Notifications** - System to notify participants of approved steps (`approval_viewed` flag)
- ✅ **Email Validation** - Implemented regex validation for Admin email addresses (Fixed Issue #4)
- ✅ **Custom Error Pages** - Added branded 404 and 403 error templates (Fixed Issue #5)
- ✅ **UI Fixes** - Fixed textarea cursor indentation in question forms (Issue #6)

**Code Structure:**
- Split `routes.py` into `routes/main.py`, `routes/admin.py`, and `routes/manage.py`
- Created `manage_users_list.html` and `manage_users_form.html`

### Phase 5: AWS Deployment with CI/CD - COMPLETE (2026-01-01)
- (See Issue #7)

---

## 🔴 CRITICAL PRIORITY - Security & Bug Fixes
**Status:** Issues created and tracked in GitHub (Issues #26-29)

### 1. Missing Active User Check (Security Vulnerability) - [Issue #26](https://github.com/timLP79/cbt12/issues/26)
**Issue:** Deactivated users can still log in - `is_active` flag not checked
**Location:**
- `app/routes/main.py:40` - Participant login
- `app/routes/admin.py:46` - Admin login
**Fix:** Add `user.is_active` check in authentication logic
**Impact:** HIGH - Security vulnerability allowing unauthorized access
**Labels:** `bug`, `critical`, `security`

### 2. Role Validation Bug (Prevents Supervisor Creation) - [Issue #27](https://github.com/timLP79/cbt12/issues/27)
**Issue:** Typo in role validation prevents creating supervisors
**Location:** `app/routes/manage.py:244`
**Current:** `if role not in ['role', 'clinician']:`
**Fix:** Should be `if role not in ['supervisor', 'clinician']:`
**Impact:** HIGH - Blocks critical admin functionality
**Labels:** `bug`, `critical`

### 3. Indentation Error in Assessment Logic - [Issue #28](https://github.com/timLP79/cbt12/issues/28)
**Issue:** Attempt creation code incorrectly indented outside else block
**Location:** `app/routes/main.py:175-191`
**Fix:** Move attempt creation inside the else block
**Impact:** HIGH - Causes runtime errors when resuming assessments
**Labels:** `bug`, `critical`

### 4. Deprecated datetime.utcnow() Usage - [Issue #29](https://github.com/timLP79/cbt12/issues/29)
**Issue:** Using deprecated `datetime.utcnow()` in Python 3.12
**Locations:**
- `app/models.py:18, 159`
- `app/routes/main.py:186, 301`
- `app/routes/admin.py:128`
**Fix:** Replace with `datetime.now(timezone.utc)`
**Impact:** MEDIUM - Will break in future Python versions
**Labels:** `bug`, `critical`
**Note:** Closed duplicate Issue #17

---

## 🟡 MEDIUM PRIORITY - Improve Code Quality
**Status:** Issues created and tracked in GitHub (Issues #30-36)

### 5. Missing Transaction Management in main.py - [Issue #30](https://github.com/timLP79/cbt12/issues/30)
**Issue:** No rollback handling in main.py routes (admin.py and manage.py have proper error handling)
**Location:** `app/routes/main.py` - All database operations
**Fix:** Add try/except blocks with `db.session.rollback()` for all database operations
**Impact:** Data corruption risk on errors
**Labels:** `bug`, `enhancement`

### 6. No Logging System - [Issue #31](https://github.com/timLP79/cbt12/issues/31)
**Issue:** Relies only on flash messages; no persistent logging
**Fix:** Implement Python's logging module for:
- Failed login attempts
- Database errors
- Validation failures
- Security events
**Impact:** Unable to debug production issues
**Labels:** `enhancement`

### 7. Session-Based Assessment State is Fragile - [Issue #32](https://github.com/timLP79/cbt12/issues/32)
**Issue:** Assessment progress stored in session (question_order, current_question_index)
**Location:** `app/routes/main.py:162-163, 194`
**Fix:** Consider storing state in database or make session more resilient
**Impact:** Users lose progress if session expires mid-assessment
**Labels:** `bug`, `enhancement`

### 8. N+1 Query Problem in Dashboard - [Issue #33](https://github.com/timLP79/cbt12/issues/33)
**Issue:** Dashboard loops through steps executing queries
**Location:** `app/routes/main.py:86-100`
**Fix:** Use eager loading or restructure query
**Impact:** Performance degradation with many steps
**Labels:** `bug`, `enhancement`

### 9. No Pagination in User/Admin Lists - [Issue #34](https://github.com/timLP79/cbt12/issues/34)
**Issue:** `list_users()` and `list_admins()` load ALL records
**Location:** `app/routes/manage.py:44, 195`
**Fix:** Implement pagination for large datasets
**Impact:** Performance issues with many users
**Labels:** `enhancement`

### 10. No Maximum Step Validation - [Issue #35](https://github.com/timLP79/cbt12/issues/35)
**Issue:** current_step could exceed 12
**Fix:** Add validation when advancing steps in approval logic
**Labels:** `bug`

### 11. Email Validation Using Regex - [Issue #36](https://github.com/timLP79/cbt12/issues/36)
**Issue:** Email regex is fragile and incomplete
**Location:** `app/models.py:104`
**Fix:** Use `email-validator` library instead
**Impact:** Invalid emails may pass validation
**Labels:** `enhancement`

---

## 🔵 LOW PRIORITY - Polish & Best Practices

### 12. XSS Protection Using Regex Blacklist
**Issue:** `validate_text_response()` uses regex blacklist (easy to bypass)
**Location:** `app/validators.py:67-77`
**Fix:** Rely on Jinja2 auto-escaping (already enabled by default)
**Note:** Current approach is redundant and gives false security

### 13. Optimize Question Ordering
**Issue:** Using Python sorted() instead of DB ORDER BY
**Fix:** Use database-level ordering

### 14. Configure Database Connection Pooling
**Issue:** No SQLAlchemy pool configuration for production
**Fix:** Add SQLALCHEMY_ENGINE_OPTIONS in ProductionConfig

### 15. Standardize Flash Message Categories
**Issue:** Some flash messages have categories, others don't
**Fix:** Standardize all flash() calls with categories

### 16. Replace Magic Strings with Constants (Duplicate of #4)
**Issue:** Status values hardcoded throughout
**Fix:** Create constants class with STATUS_IN_PROGRESS, STATUS_SUBMITTED, etc.

### 17. Add __repr__ Methods to Models
**Issue:** Models lack string representations
**Fix:** Add __repr__ to all models for better debugging

### 18. Missing Features for Production
**Issue:** No audit trail, password reset, email verification, rate limiting on sensitive ops
**Fix:** Consider implementing as Phase 8 features

---

## 🎯 Next Phase - Feature Expansion

**Immediate Tasks:**
- 👤 **Participant Profile & History** - COMPLETE (Issue #22)


**UI/UX Improvements:**
- Improve CSS styling and mobile responsiveness
- Better visual progress indicators
- Admin dashboard enhancements

**Backend Enhancements:**
- Logging and audit trail (track admin actions, login attempts)
- Database connection pooling for production
- Export functionality for assessment data

**Advanced Features:**
- Custom domain + HTTPS (AWS Certificate Manager + Route 53)
- Email notifications (admin for pending, participant for approvals)
- Analytics dashboard for treatment progress
- Multi-language support
- Offline capability for institutional tablets

**Infrastructure Optimization:**
- Consider AWS Auto Scaling for high traffic
- CloudWatch monitoring and alerts
- Automated database backups
- Staging environment for testing

---

## 📊 Project Management

### GitHub Integration
- **Repository:** [timLP79/cbt12](https://github.com/timLP79/cbt12)
- **Project Board:** [CBT12 Project](https://github.com/timLP79/cbt12/projects/10)
- **Total Issues:** 37
  - 🔴 Critical: 4 issues (#26-29)
  - 🟡 Medium: 7 issues (#30-36)
  - ✅ Completed: 1 issue (#37 - UI Redesign)
  - Other: 25 existing issues

### Labels Created (2026-01-17)
- `critical` - Critical priority issues requiring immediate attention
- `security` - Security vulnerabilities
- `ui` - User interface and design changes

### Recent Actions (2026-01-17)
- ✅ Created 11 new issues from comprehensive code review
- ✅ Added all issues to project board
- ✅ Assigned all issues to @timLP79
- ✅ Closed duplicate Issue #17 (consolidated into #29)
- ✅ Installed `jq` for enhanced JSON parsing
- ✅ Created Issue #37 for UI redesign
- ✅ Implemented modern UI with dark mode (merged Option D)
- ✅ Completed and closed Issue #37

---

## 📝 Notes

- This is a learning project focused on security best practices
- All critical security issues identified via comprehensive code review (2026-01-17)
- All issues tracked in GitHub with detailed implementation guidance
- Will implement fixes one-by-one in teaching style
- Each fix will be explained with understanding checks
- Testing after each major change
- Deployment only after all critical fixes complete
