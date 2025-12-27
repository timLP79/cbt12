# CBT Assessment - Technical Debt & Improvements

## 🔴 CRITICAL - Fix Before Next Session (5-10 minutes)

### 1. Login Manager Bug
**File:** `app/__init__.py:18`
**Issue:** Login redirect points to wrong blueprint
**Current:**
```python
login_manager.login_view = 'auth.login'  # Blueprint is 'main', not 'auth'
```
**Fix:**
```python
login_manager.login_view = 'main.login'
```

### 2. Move Scattered Imports to Top
**File:** `app/routes.py`
**Issue:** Imports inside functions (lines 70, 77, 89, 145)
**Fix:** Move these to top of file:
```python
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import random
```

### 3. Create Instance Folder Programmatically
**File:** `init_db.py` or `run.py`
**Issue:** App crashes on fresh install if `instance/` doesn't exist
**Fix:** Add before database operations:
```python
import os
os.makedirs('instance', exist_ok=True)
```

---

## 🟡 HIGH PRIORITY - Fix When Building Related Features

### 4. Add CSRF Protection
**Priority:** Before any deployment or multi-user testing
**Options:**
- Install Flask-WTF: `pip install flask-wtf`
- Or implement manual CSRF tokens
**Impact:** Security vulnerability without this

### 5. Replace Deprecated datetime.utcnow()
**Files:** `app/models.py:17, 88`
**Issue:** Deprecated in Python 3.12+
**Fix:**
```python
from datetime import datetime, timezone

# Change:
date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)
# To:
date_enrolled = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```

### 6. Add Error Handling to Database Operations
**File:** `app/routes.py`
**Issue:** No try/except blocks - users see raw 500 errors
**Fix:** Wrap commit operations:
```python
try:
    db.session.add(response)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    flash('An error occurred saving your response.')
    # Log the error
```

### 7. Prevent Duplicate Responses
**File:** `app/models.py` - Response class
**Issue:** User can submit same question multiple times
**Fix:** Add unique constraint:
```python
class Response(db.Model):
    __tablename__ = 'responses'
    # ... existing columns ...

    __table_args__ = (
        db.UniqueConstraint('prison_id', 'question_id',
                          name='unique_user_question_response'),
    )
```

---

## 🟢 MEDIUM PRIORITY - Improve Code Quality

### 8. Add __repr__ Methods to Models
**File:** `app/models.py`
**Benefit:** Better debugging experience
**Example:**
```python
class User(db.Model, UserMixin):
    # ... existing code ...

    def __repr__(self):
        return f'<User {self.prison_id}: {self.first_name} {self.last_name}>'
```
Add similar methods to all model classes.

### 9. Create Constants for Magic Strings
**Issue:** Question types hardcoded as strings throughout code
**Fix:** Create `app/constants.py`:
```python
class QuestionType:
    MULTIPLE_CHOICE = 'multiple_choice'
    WRITTEN = 'written'
```
Then use: `if question.question_type == QuestionType.MULTIPLE_CHOICE:`

### 10. Consolidate CSS Styling
**Files:** All templates
**Issue:** Mix of base.html styles and inline styles
**Options:**
- Move all styles to `base.html` `<style>` block
- Create `app/static/css/style.css`
- Use CSS framework (Bootstrap, Tailwind)

### 11. Add Cascade Delete Rules
**File:** `app/models.py`
**Issue:** Unclear behavior when deleting parent records
**Fix:**
```python
responses = db.relationship('Response', backref='user',
                           lazy=True, cascade='all, delete-orphan')
```

### 12. Fix Config Redundancy
**Files:** `run.py:6` and `config.py`
**Issue:** Debug mode set in two places
**Fix:** Remove `debug=True` from run.py, use config only:
```python
# run.py
if __name__ == '__main__':
    app.run()  # Remove debug=True
```

---

## 🔵 LOW PRIORITY - Polish & Best Practices

### 13. Add Database Indexes on Foreign Keys
**File:** `app/models.py`
**Benefit:** Better query performance (matters at scale)
**Example:**
```python
step_id = db.Column(db.Integer, db.ForeignKey('steps.step_id'),
                   nullable=False, index=True)
```

### 14. Standardize Relationship Comments
**File:** `app/models.py`
**Issue:** Inconsistent comment styles on relationships
**Fix:** Use consistent format or remove comments

### 15. Add Comprehensive Docstrings
**Files:** All model classes
**Current:** Only some functions have docstrings
**Fix:** Add class-level docstrings to all models

### 16. Move SECRET_KEY to Environment Variable
**File:** `config.py:8`
**Current:** Fallback secret in code
**Fix:**
- Create `.env` file (add to .gitignore)
- Use python-dotenv (already installed)
- Require SECRET_KEY in production

### 17. Add Rate Limiting
**Priority:** Only needed before production deployment
**Tool:** Flask-Limiter
**Target:** Login endpoint to prevent brute force attacks

### 18. Add Password Validation
**File:** `create_test_user.py` and future user creation
**Requirements:**
- Minimum length
- Complexity requirements
- Common password checking

---

## 📊 Code Review Summary

**Total Issues Found:** 18
**Critical (Fix Now):** 3
**High Priority:** 4
**Medium Priority:** 5
**Low Priority:** 6

**Estimated Time to Fix Critical Issues:** 5-10 minutes
**Estimated Time for High Priority:** 1-2 hours
**Estimated Time for Medium Priority:** 2-3 hours
**Estimated Time for Low Priority:** 2-4 hours

---

## 📝 Notes

- This is a learning project - perfection not required
- Fix critical bugs immediately
- Address other issues when working in related code
- Don't let technical debt block feature development
- Revisit this list before any production deployment
