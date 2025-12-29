# CBT Assessment - Technical Debt & Improvements

**Last Updated:** 2025-12-28

## ✅ Recently Completed (2025-12-28)

### Phase 3: Admin Portal - COMPLETE
- **Admin authentication system** - Separate login portal for administrative staff
- **Admin dashboard** - Lists all pending assessments needing review
- **Review interface** - Displays participant responses with question context
- **Approval workflow** - Approve or request revision with feedback notes
- **Participant advancement** - Automatic step progression on approval
- **End-to-end testing** - Complete workflow verified (participant → submit → review → approve)

### Major Refactoring - COMPLETE (2025-12-28)
- **Renamed Clinician → Admin** - More general terminology for broader use
- **Renamed prison_id → state_id** - Removes prison-specific terminology
- **Updated all routes** - Changed 15+ route references and URLs
- **Updated all templates** - Modified 5 template files for new naming
- **Updated database scripts** - Modified init_db.py and create_test_data.py
- **Database recreation** - Fresh database with new schema
- **User-facing text** - Kept "clinician" in participant-facing messages for clarity
- **Test credentials updated** - ADMIN001/ADMIN002 instead of CLIN001/CLIN002

### Phase 2: Participant Flow - COMPLETE (2025-12-27)
- **Modified routes.py** - Create AssessmentAttempt on start, link responses to attempts
- **Removed auto-advancement** - Users stay on current step until approved
- **Updated dashboard.html** - Dynamic status display (Pending/Approved/Needs Revision)
- **Updated assessment_complete.html** - "Pending Review" messaging
- **End-to-end testing** - Verified attempt tracking and status flow

### Phase 1: Database & Core Models - COMPLETE
- Database schema with admin review workflow
- Instance folder creation fixed in init_db.py
- Test data script (create_test_data.py) for users and admins

---

## 🔴 CRITICAL - Security Issues (Phase 4)

**Note:** These issues were identified during comprehensive code review on 2025-12-28. Must fix before ANY production deployment.

### 1. Missing CSRF Protection
**Severity:** CRITICAL
**Impact:** All forms vulnerable to cross-site request forgery attacks
**Files:** All templates with forms
**Fix:**
```bash
pip install Flask-WTF
```
```python
# In app/__init__.py
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
csrf.init_app(app)

# In all templates with forms
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

### 2. Missing Authorization Checks on Admin Routes
**Severity:** CRITICAL
**Impact:** Participants could access admin review routes by manipulating URLs
**Files:** `app/routes.py` - admin_dashboard, review_attempt, submit_review
**Fix:** Create `@admin_required` decorator:
```python
from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Apply to all admin routes:
@main.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # ...
```

### 3. Weak Secret Key Handling
**Severity:** CRITICAL
**Impact:** Production could use weak default secret key
**File:** `config.py`
**Fix:**
```python
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")
```

### 4. Session Fixation Vulnerability
**Severity:** HIGH
**Impact:** Session ID not regenerated after login
**File:** `app/routes.py` - login routes
**Fix:**
```python
# After successful login, before redirect:
session.clear()
login_user(user)
session.regenerate()
session['user_type'] = 'participant'
```

### 5. Insecure Direct Object Reference (IDOR)
**Severity:** HIGH
**Impact:** Users could access other users' assessment attempts
**File:** `app/routes.py` - review_attempt
**Fix:** Add authorization check in review_attempt route

---

## 🟡 HIGH PRIORITY - Fix Before Deployment

### 6. No Input Validation
**Severity:** HIGH
**Impact:** User inputs not validated for length, format, or content
**Files:** All routes accepting form data
**Fix:** Add validation functions and use on all user inputs

### 7. No Rate Limiting
**Severity:** HIGH
**Impact:** No protection against brute force attacks on login
**Files:** Login routes
**Fix:**
```bash
pip install Flask-Limiter
```
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@main.route('/login')
@limiter.limit("5 per minute")
def login():
    # ...
```

### 8. Missing Database Indexes
**Severity:** HIGH
**Impact:** Poor query performance at scale
**File:** `app/models.py`
**Fix:** Add indexes on frequently queried columns:
```python
status = db.Column(db.String(20), default='in_progress', nullable=False, index=True)

__table_args__ = (
    db.Index('idx_state_assessment', 'state_id', 'assessment_id'),
    db.Index('idx_status_submitted', 'status', 'submitted_at'),
)
```

### 9. N+1 Query Problem
**Severity:** HIGH
**Impact:** Inefficient database queries in admin dashboard
**File:** `app/routes.py` - admin_dashboard
**Fix:** Use eager loading:
```python
from sqlalchemy.orm import joinedload

pending_attempts = AssessmentAttempt.query.filter_by(
    status='submitted'
).options(
    joinedload(AssessmentAttempt.user),
    joinedload(AssessmentAttempt.assessment).joinedload(Assessment.step)
).order_by(AssessmentAttempt.submitted_at.desc()).all()
```

### 10. Race Condition in Assessment Creation
**Severity:** HIGH
**Impact:** Could create duplicate attempt numbers
**File:** `app/routes.py` - start_assessment
**Fix:** Use database-level counting

---

## 🟢 MEDIUM PRIORITY - Improve Code Quality

### 11. Duplicate Response Prevention
**Issue:** No check to prevent multiple responses for same question
**Fix:** Add unique constraint in Response model

### 12. Incomplete Session Cleanup
**Issue:** Logout doesn't clear all session data
**Fix:** Use `session.clear()` in logout route

### 13. Missing Null Checks in Templates
**Issue:** Accessing `attempt.reviewer` without checking if exists
**Fix:** Add `{% if attempt.reviewer %}` checks

### 14. No Email Validation
**Issue:** Admin email field has no validation
**Fix:** Add email regex validation in Admin model

### 15. Missing Transaction Management
**Issue:** Multiple DB operations without rollback handling
**Fix:** Add try/except blocks with db.session.rollback()

### 16. No Maximum Step Validation
**Issue:** current_step could exceed 12
**Fix:** Add validation when advancing steps

### 17. No Logging/Audit Trail
**Issue:** No logging of security events
**Fix:** Add logging for logins, failed attempts, data changes

---

## 🔵 LOW PRIORITY - Polish & Best Practices

### 18. Inefficient Question Ordering
**Issue:** Using Python sorted() instead of DB ORDER BY
**Fix:** Use database-level ordering

### 19. No Error Templates
**Issue:** No custom 404, 403, 500 error pages
**Fix:** Create error handler functions and templates

### 20. No Database Connection Pooling
**Issue:** No SQLAlchemy pool configuration for production
**Fix:** Add SQLALCHEMY_ENGINE_OPTIONS in ProductionConfig

### 21. Inconsistent Flash Message Categories
**Issue:** Some flash messages have categories, others don't
**Fix:** Standardize all flash() calls with categories

### 22. Timezone Issues
**Issue:** Using datetime.utcnow() - deprecated
**Fix:** Use datetime.now(timezone.utc)

### 23. Magic Strings
**Issue:** Status values hardcoded throughout
**Fix:** Create constants class

### 24. Add __repr__ Methods
**Issue:** Models lack string representations
**Fix:** Add __repr__ to all models for better debugging

### 25. Consolidate CSS Styling
**Issue:** Mix of base.html styles and inline styles
**Fix:** Create app/static/css/style.css

---

## 📊 Security Review Summary

**Critical Security Issues:** 5 (MUST fix before deployment)
**High Priority Issues:** 5 (Should fix before deployment)
**Medium Priority Issues:** 7 (Improve as you go)
**Low Priority Issues:** 8 (Nice to have)

**Total Issues:** 25

---

## 🎯 Phase 4 Tasks (Next Session)

**Goal:** Security hardening before deployment

**Session 1: Critical Security Fixes (Teaching Mode)**
1. Add CSRF protection with Flask-WTF
2. Implement @admin_required decorator
3. Fix secret key handling
4. Regenerate sessions on login
5. Add authorization checks

**Session 2: Input Validation & Rate Limiting**
6. Add input validation throughout
7. Implement rate limiting on login
8. Add database indexes
9. Fix N+1 queries
10. Add transaction rollback handling

**Session 3: Testing & Deployment Prep**
11. Test all security fixes
12. Add error pages
13. Add logging
14. Prepare for Render.com deployment

**Estimated Time:** 3-4 hours total across multiple sessions

**After Phase 4:** Deploy to Render.com for testing

---

## 📝 Notes

- This is a learning project focused on security best practices
- All critical security issues identified via comprehensive code review
- Will implement fixes one-by-one in teaching style
- Each fix will be explained with understanding checks
- Testing after each major change
- Deployment only after all critical fixes complete
