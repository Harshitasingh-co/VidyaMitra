# Internship Discovery Module - Test Documentation

## Overview

This document explains the testing strategy for the Internship Discovery & Verification Module, including property-based tests and unit tests.

## Test Files

### 1. `test_internship_models.py`
**Purpose**: Property-based tests for Pydantic models (data validation layer)

**What it tests**:
- Model serialization and deserialization
- Field validation (types, ranges, constraints)
- Enum validation
- Required vs optional fields

**Key Tests**:
- `test_profile_data_round_trip`: Validates that profile data can be serialized to dict and reconstructed without data loss (Property 1 - Model Layer)
- `test_semester_validation_property`: Validates semester range constraints (Property 2)
- Unit tests for boundary values, empty fields, and enum validation

**Dependencies**: None (runs without database)

**Run with**:
```bash
pytest tests/test_internship_models.py -v
```

### 2. `test_profile_round_trip.py`
**Purpose**: Property-based tests for database operations (service layer)

**What it tests**:
- Actual database INSERT and SELECT operations
- Data persistence and retrieval
- Service layer logic
- Database constraints and triggers

**Key Tests**:
- `test_profile_data_round_trip_database`: Validates that profile data stored in Supabase can be retrieved with all fields preserved (Property 1 - Database Layer)
- Unit tests for empty lists, all fields populated, partial updates, and not found cases

**Dependencies**: 
- Supabase credentials (SUPABASE_URL and SUPABASE_KEY)
- Database schema must be created (see migrations/001_internship_discovery_schema.sql)

**Run with**:
```bash
# Will skip if Supabase not configured
pytest tests/test_profile_round_trip.py -v
```

## Property-Based Testing

### What is Property-Based Testing?

Property-based testing validates universal properties that should hold for **all** valid inputs, not just specific examples. Instead of writing individual test cases, we define properties and let Hypothesis generate hundreds of random test cases.

### Configuration

- **Framework**: Hypothesis
- **Examples per test**: 100 (configurable in conftest.py)
- **Profile**: "default" (can switch to "ci" for more examples or "dev" for faster runs)

### Property 1: Profile Data Round-Trip

**Statement**: For any valid student profile data, storing the profile and then retrieving it should return equivalent data with all fields preserved.

**Validates**: Requirements 1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 1.9

**Two-Layer Testing**:
1. **Model Layer** (`test_internship_models.py`): Tests Pydantic serialization/deserialization
2. **Database Layer** (`test_profile_round_trip.py`): Tests actual database storage/retrieval

**Why both layers?**
- Model layer catches validation and serialization bugs (fast, no dependencies)
- Database layer catches persistence bugs, SQL constraints, and service logic issues (comprehensive, requires database)

### Property 2: Semester Validation

**Statement**: For any semester value, the system should accept values between 1 and 8 (inclusive) and reject all other values.

**Validates**: Requirement 1.2

**Implementation**: Tests all integers (positive, negative, zero) and verifies correct acceptance/rejection

## Running Tests

### Run all internship tests
```bash
pytest tests/test_internship_models.py tests/test_profile_round_trip.py -v
```

### Run only property tests
```bash
pytest -m property -v
```

### Run with Hypothesis statistics
```bash
pytest -m property --hypothesis-show-statistics
```

### Run with coverage
```bash
pytest tests/test_internship_models.py --cov=app.models.internship --cov-report=term-missing
```

## Test Data Generation

### Strategies Used

The tests use Hypothesis strategies to generate random but valid test data:

- **graduation_year**: 2024-2035
- **current_semester**: 1-8
- **degree**: B.Tech, M.Tech, BCA, MCA, B.Sc, M.Sc
- **branch**: Computer Science, IT, Electronics, Mechanical, Civil, Data Science
- **skills**: Python, Java, JavaScript, C++, SQL, React, Node.js, Django, Flask, AWS, Docker, Kubernetes, Git
- **roles**: Software Engineer, Data Analyst, Data Scientist, Frontend/Backend/Full Stack Developer, DevOps Engineer, ML Engineer
- **companies**: Google, Microsoft, Amazon, Apple, Meta, Netflix, Tesla, Adobe, Salesforce

### Why These Strategies?

1. **Realistic data**: Uses actual degree names, skills, and companies
2. **Edge cases**: Includes empty lists, None values, boundary values
3. **Comprehensive coverage**: Generates diverse combinations to catch bugs
4. **Reproducible**: Hypothesis caches failing examples for debugging

## Debugging Failed Tests

### If a property test fails:

1. **Check the counterexample**: Hypothesis will show the exact input that caused the failure
2. **Reproduce locally**: The failing example is cached in `.hypothesis/` directory
3. **Simplify**: Hypothesis automatically tries to find the simplest failing case
4. **Fix the bug**: Update the code or test based on the failure

### Example failure output:
```
Falsifying example: test_profile_data_round_trip(
    graduation_year=2024,
    current_semester=1,
    degree='B.Tech',
    branch='Computer Science',
    skills=[],
    preferred_roles=[],
    internship_type='Remote',
    compensation_preference='Paid',
    target_companies=[],
    resume_url=None
)
```

## Best Practices

1. **Keep tests independent**: Each test should clean up after itself
2. **Use fixtures**: Share common setup code via pytest fixtures
3. **Test at multiple layers**: Model validation + service logic + database operations
4. **Document properties**: Clearly state what property is being tested
5. **Link to requirements**: Reference specific requirements in test docstrings
6. **Run regularly**: Property tests should be part of CI/CD pipeline

## Future Enhancements

- Add property tests for verification service (Property 5-8)
- Add property tests for skill matching (Property 9-12)
- Add property tests for readiness scoring (Property 15-17)
- Add property tests for alert creation (Property 19-22)
- Add integration tests for complete user journeys
- Add performance tests for large datasets

## References

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing Guide](https://hypothesis.works/articles/what-is-property-based-testing/)
- Design Document: `.kiro/specs/internship-discovery/design.md`
- Requirements: `.kiro/specs/internship-discovery/requirements.md`
