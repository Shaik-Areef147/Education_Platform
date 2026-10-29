# EduPro - Executive Summary
**Learner Demographics and Course Enrollment Behavior Analysis** (descriptive analytics, 01 Jan 2025 to 30 Dec 2025)

## Purpose
EduPro lacked clear answers about who its learners are and how they choose courses. This analysis joins the Users, Courses and Transactions sheets (3,000 learners, 60 courses, 10,000 enrollments; zero orphan records) to give a factual basis for course creation, marketing and inclusion decisions.

## Headline findings
- **Reach:** 3,000 learners made 10,000 enrollments - 3.33 per learner on average, but the median learner took only 1.
- **Age:** learners are aged 15-35. The **26-35** band is the most active (48.0% of enrollments). Learners aged 36+ are absent from the data.
- **Gender:** 50.7% female / 49.3% male - near-parity. Enrollments per learner: Female 3.34, Male 3.33.
- **Categories:** **Data Science** leads (9.2%); **Marketing** is lowest (8.1%). The spread is narrow - demand is broad across all 12 categories.
- **Levels:** Beginner 35.7%, Intermediate 29.5%, Advanced 34.8%. Free courses account for 64.0% of enrollments.
- **Preferences barely differ by segment:** association between age group and category is weak (Cramer's V = 0.030); gender vs category 0.030; age vs level 0.013.
- **Concentration:** the top 10% most active learners generate 42.3% of enrollments; 54.0% of learners enrolled in just one course.

## Recommendations
1. **Course creation:** grow catalogue depth in the highest-demand categories (Data Science, Finance, Web Development); review positioning of Marketing.
2. **Marketing:** prioritise the 26-35 segment; run acquisition tests for under-18s and attract 36+ learners (currently none).
3. **Inclusion:** participation is balanced - maintain it with gender-neutral content and messaging.
4. **Engagement:** most learners stop after one course. Introduce next-course recommendations and beginner-to-advanced learning paths.
5. **Retention:** protect and reward the small group of highly active learners who drive a large share of volume.

## Method and limits
Descriptive only (no prediction or monetization). Age bands: <18, 18-25, 26-35, 36-45, 45+. Findings reflect a single year of platform data. Live exploration with filters is available in the Streamlit dashboard.
