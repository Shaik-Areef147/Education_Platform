"""Generate the executive summary and research paper (Markdown) from the data. Run: python scripts/generate_reports.py"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import analysis as A  # noqa: E402
from src import data as D  # noqa: E402

sheets = pd.read_excel(D.DATA_FILE, sheet_name=None)
enr, users, q = D.integrate(sheets)
K = A.kpis(enr, users)
PL = A.per_learner(enr)
ea = A.enrollments_by_age(enr)
ad = A.age_distribution(users)
g = A.gender_summary(enr)
cp = A.category_popularity(enr)
lv = A.level_distribution(enr)
ty = A.count_by(enr, "CourseType")
tp = A.top_pairs(enr, 5)
v_age_cat = A.cramers_v(A.crosstab(enr, "AgeGroup", "CourseCategory"))
v_gen_cat = A.cramers_v(A.crosstab(enr, "Gender", "CourseCategory"))
v_age_lvl = A.cramers_v(A.crosstab(enr, "AgeGroup", "CourseLevel"))
v_gen_lvl = A.cramers_v(A.crosstab(enr, "Gender", "CourseLevel"))
stage = A.learner_stage(PL).value_counts()
top10, top20 = A.share_of_top(PL, 10), A.share_of_top(PL, 20)
one = (PL["Courses"] == 1).mean() * 100


def md(df, fmt=None):
    fmt = fmt or {}
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt.get(c, "{}").format(r[c]) for c in cols) + " |")
    return "\n".join(out)


gl = A.crosstab(enr, "Gender", "CourseLevel", "row").round(1).reset_index()
al = A.crosstab(enr, "AgeGroup", "CourseLevel", "row").round(1).reset_index()
cat_age = A.crosstab(enr, "AgeGroup", "CourseCategory", "row").round(1).reset_index()
topc, botc = cp.iloc[0], cp.iloc[-1]
topa = ea.sort_values("Enrollments").iloc[-1]
dr = f"{q['date_min']:%d %b %Y} to {q['date_max']:%d %b %Y}"

summary = f"""# EduPro - Executive Summary
**Learner Demographics and Course Enrollment Behavior Analysis** (descriptive analytics, {dr})

## Purpose
EduPro lacked clear answers about who its learners are and how they choose courses. This analysis joins the Users, Courses and Transactions sheets ({q['users']:,} learners, {q['courses']} courses, {q['transactions']:,} enrollments; zero orphan records) to give a factual basis for course creation, marketing and inclusion decisions.

## Headline findings
- **Reach:** {K['active_learners']:,} learners made {K['total_enrollments']:,} enrollments - {K['avg_per_learner']:.2f} per learner on average, but the median learner took only {PL['Courses'].median():.0f}.
- **Age:** learners are aged {users['Age'].min()}-{users['Age'].max()}. The **{topa['AgeGroup']}** band is the most active ({topa['Share %']:.1f}% of enrollments). Learners aged 36+ are absent from the data.
- **Gender:** {K['female_pct']:.1f}% female / {K['male_pct']:.1f}% male - near-parity. Enrollments per learner: {', '.join(f"{a} {b:.2f}" for a, b in zip(g['Gender'], g['Enrollments per learner']))}.
- **Categories:** **{topc['CourseCategory']}** leads ({topc['Share %']:.1f}%); **{botc['CourseCategory']}** is lowest ({botc['Share %']:.1f}%). The spread is narrow - demand is broad across all {len(cp)} categories.
- **Levels:** {', '.join(f"{a} {b:.1f}%" for a, b in zip(lv['CourseLevel'], lv['Share %']))}. Free courses account for {K['free_pct']:.1f}% of enrollments.
- **Preferences barely differ by segment:** association between age group and category is weak (Cramer's V = {v_age_cat:.3f}); gender vs category {v_gen_cat:.3f}; age vs level {v_age_lvl:.3f}.
- **Concentration:** the top 10% most active learners generate {top10:.1f}% of enrollments; {one:.1f}% of learners enrolled in just one course.

## Recommendations
1. **Course creation:** grow catalogue depth in the highest-demand categories ({topc['CourseCategory']}, {cp.iloc[1]['CourseCategory']}, {cp.iloc[2]['CourseCategory']}); review positioning of {botc['CourseCategory']}.
2. **Marketing:** prioritise the {topa['AgeGroup']} segment; run acquisition tests for under-18s and attract 36+ learners (currently none).
3. **Inclusion:** participation is balanced - maintain it with gender-neutral content and messaging.
4. **Engagement:** most learners stop after one course. Introduce next-course recommendations and beginner-to-advanced learning paths.
5. **Retention:** protect and reward the small group of highly active learners who drive a large share of volume.

## Method and limits
Descriptive only (no prediction or monetization). Age bands: <18, 18-25, 26-35, 36-45, 45+. Findings reflect a single year of platform data. Live exploration with filters is available in the Streamlit dashboard.
"""

paper = f"""# Learner Demographics and Course Enrollment Behavior on EduPro: An Exploratory Data Analysis

## Abstract
This study describes who the learners on the EduPro online platform are and how they select courses. Using {q['transactions']:,} enrollments by {q['users']:,} learners across {q['courses']} courses ({dr}), we analyse age, gender, course category, type and level. Learners are young (ages {users['Age'].min()}-{users['Age'].max()}, mean {users['Age'].mean():.1f}), gender-balanced, and show broadly similar course preferences across segments. Engagement is highly concentrated: the top 10% of learners account for {top10:.1f}% of enrollments.

## 1. Introduction
Understanding learner demographics and enrollment behavior is foundational to course design, engagement, marketing and inclusivity. This project is deliberately descriptive: no prediction or monetization is attempted. Key questions: age distribution; enrollment by age; gender differences in course choice; most popular categories; and course type/level preferences.

## 2. Data and Methodology
**Data.** Workbook `EduPro_Online_Platform.xlsx` - Users (UserID, UserName, Age, Gender), Courses (CourseID, CourseName, CourseCategory, CourseType, CourseLevel) and Transactions (TransactionID, UserID, CourseID, TransactionDate).

**Integration and quality.** Transactions were inner-joined to Users on UserID and to Courses on CourseID. Checks: duplicate users {q['duplicate_users']}, duplicate courses {q['duplicate_courses']}, duplicate transactions {q['duplicate_transactions']}, orphan UserIDs {q['orphan_user_ids']}, orphan CourseIDs {q['orphan_course_ids']}, missing values {q['missing_values']}, rows lost in join {q['dropped_rows']}. Referential integrity holds fully.

**Segmentation.** Age bands: <18, 18-25, 26-35, 36-45, 45+ (the last two are empty in this dataset).

**Metrics.** Enrollment counts, enrollments per learner, share of total, Category Popularity Index (category share / equal share x 100), lift (segment share / platform share), Cramer's V for association strength, and a concentration curve of enrollments across learners.

## 3. Results
### 3.1 Learner demographics
{md(ad, {'Share %': '{:.1f}'})}

Gender (learners with at least one enrollment):

{md(g, {'Learner share %': '{:.1f}', 'Enrollments per learner': '{:.2f}'})}

### 3.2 Enrollment by age group
{md(ea, {'Share %': '{:.1f}', 'Enrollments per learner': '{:.2f}'})}

### 3.3 Enrollment distribution
Category popularity:

{md(cp, {'Share %': '{:.1f}', 'Popularity Index': '{:.0f}'})}

Course type:

{md(ty, {'Share %': '{:.1f}'})}

Course level:

{md(lv, {'Share %': '{:.1f}'})}

### 3.4 Demographics x preference
Category mix within each age group (% of the group's enrollments):

{md(cat_age)}

Course level mix by gender (%):

{md(gl)}

Course level mix by age group (%):

{md(al)}

Association strength (Cramer's V): age vs category {v_age_cat:.3f}; gender vs category {v_gen_cat:.3f}; age vs level {v_age_lvl:.3f}; gender vs level {v_gen_lvl:.3f}. All are close to zero: segment preferences are very similar. Largest segment over-indexes (lift):

{md(tp, {'Segment share %': '{:.1f}', 'Platform share %': '{:.1f}', 'Lift': '{:.2f}x'})}

### 3.5 Behavioral insights
- Mean courses per learner {PL['Courses'].mean():.2f}; median {PL['Courses'].median():.0f}; maximum {PL['Courses'].max()}.
- {one:.1f}% of learners took exactly one course; top 10% of learners generate {top10:.1f}% and top 20% generate {top20:.1f}% of enrollments.
- Learner stage by highest level taken: {', '.join(f'{k}: {v:,}' for k, v in stage.items())}.

## 4. Discussion
Demand is broad: no category dominates and the gap between the most ({topc['CourseCategory']}) and least ({botc['CourseCategory']}) popular is small. Because segment preferences are near-identical, differences between age/gender groups are better explained by group size than by taste. The more consequential pattern is behavioral - a small, highly active group and a large single-course majority.

## 5. Recommendations
1. Invest in depth of top-demand categories; test positioning of the lowest.
2. Market to the {topa['AgeGroup']} core while piloting outreach to under-18s and 36+ adults.
3. Keep gender-neutral design to preserve near-parity.
4. Build beginner-to-advanced paths and next-course recommendations to convert one-course learners.
5. Create loyalty mechanisms for highly active learners.

## 6. Limitations
Single year of data; no learner-outcome or satisfaction measures; ages limited to {users['Age'].min()}-{users['Age'].max()}; descriptive associations, not causal claims. Percent differences between segments should be treated cautiously where group sizes are small.

## 7. Conclusion
EduPro serves a young, balanced learner base with broad and uniform interests. Growth levers lie in engagement depth and in reaching age groups currently absent, rather than in tailoring content by gender or age band.
"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "Executive_Summary.md").write_text(summary, encoding="utf-8")
(ROOT / "docs" / "Research_Paper.md").write_text(paper, encoding="utf-8")
print(summary)
