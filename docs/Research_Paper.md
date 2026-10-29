# Learner Demographics and Course Enrollment Behavior on EduPro: An Exploratory Data Analysis

## Abstract
This study describes who the learners on the EduPro online platform are and how they select courses. Using 10,000 enrollments by 3,000 learners across 60 courses (01 Jan 2025 to 30 Dec 2025), we analyse age, gender, course category, type and level. Learners are young (ages 15-35, mean 25.0), gender-balanced, and show broadly similar course preferences across segments. Engagement is highly concentrated: the top 10% of learners account for 42.3% of enrollments.

## 1. Introduction
Understanding learner demographics and enrollment behavior is foundational to course design, engagement, marketing and inclusivity. This project is deliberately descriptive: no prediction or monetization is attempted. Key questions: age distribution; enrollment by age; gender differences in course choice; most popular categories; and course type/level preferences.

## 2. Data and Methodology
**Data.** Workbook `EduPro_Online_Platform.xlsx` - Users (UserID, UserName, Age, Gender), Courses (CourseID, CourseName, CourseCategory, CourseType, CourseLevel) and Transactions (TransactionID, UserID, CourseID, TransactionDate).

**Integration and quality.** Transactions were inner-joined to Users on UserID and to Courses on CourseID. Checks: duplicate users 0, duplicate courses 0, duplicate transactions 0, orphan UserIDs 0, orphan CourseIDs 0, missing values 0, rows lost in join 0. Referential integrity holds fully.

**Segmentation.** Age bands: <18, 18-25, 26-35, 36-45, 45+ (the last two are empty in this dataset).

**Metrics.** Enrollment counts, enrollments per learner, share of total, Category Popularity Index (category share / equal share x 100), lift (segment share / platform share), Cramer's V for association strength, and a concentration curve of enrollments across learners.

## 3. Results
### 3.1 Learner demographics
| AgeGroup | Learners | Share % |
|---|---|---|
| <18 | 433 | 14.4 |
| 18-25 | 1121 | 37.4 |
| 26-35 | 1446 | 48.2 |

Gender (learners with at least one enrollment):

| Gender | Enrollments | Learners | Enrollments per learner | Learner share % |
|---|---|---|---|---|
| Female | 5078 | 1520 | 3.34 | 50.7 |
| Male | 4922 | 1480 | 3.33 | 49.3 |

### 3.2 Enrollment by age group
| AgeGroup | Enrollments | Learners | Enrollments per learner | Share % |
|---|---|---|---|---|
| <18 | 1469 | 433 | 3.39 | 14.7 |
| 18-25 | 3732 | 1121 | 3.33 | 37.3 |
| 26-35 | 4799 | 1446 | 3.32 | 48.0 |

### 3.3 Enrollment distribution
Category popularity:

| CourseCategory | Enrollments | Share % | Popularity Index |
|---|---|---|---|
| Data Science | 916 | 9.2 | 110 |
| Finance | 864 | 8.6 | 104 |
| Web Development | 844 | 8.4 | 101 |
| Business | 833 | 8.3 | 100 |
| Project Management | 829 | 8.3 | 99 |
| Artificial Intelligence | 829 | 8.3 | 99 |
| Design | 827 | 8.3 | 99 |
| Cybersecurity | 819 | 8.2 | 98 |
| Machine Learning | 819 | 8.2 | 98 |
| Digital Marketing | 808 | 8.1 | 97 |
| Programming | 806 | 8.1 | 97 |
| Marketing | 806 | 8.1 | 97 |

Course type:

| CourseType | Enrollments | Share % |
|---|---|---|
| Free | 6403 | 64.0 |
| Paid | 3597 | 36.0 |

Course level:

| CourseLevel | Enrollments | Share % |
|---|---|---|
| Beginner | 3573 | 35.7 |
| Intermediate | 2952 | 29.5 |
| Advanced | 3475 | 34.8 |

### 3.4 Demographics x preference
Category mix within each age group (% of the group's enrollments):

| AgeGroup | Artificial Intelligence | Business | Cybersecurity | Data Science | Design | Digital Marketing | Finance | Machine Learning | Marketing | Programming | Project Management | Web Development |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <18 | 8.8 | 8.2 | 8.2 | 7.8 | 8.2 | 8.6 | 9.3 | 8.2 | 8.6 | 7.4 | 7.8 | 9.0 |
| 18-25 | 8.5 | 8.2 | 8.2 | 9.2 | 8.3 | 7.9 | 8.0 | 8.2 | 8.4 | 8.2 | 7.9 | 9.0 |
| 26-35 | 8.0 | 8.5 | 8.1 | 9.6 | 8.3 | 8.0 | 9.0 | 8.2 | 7.6 | 8.2 | 8.7 | 7.9 |

Course level mix by gender (%):

| Gender | Beginner | Intermediate | Advanced |
|---|---|---|---|
| Female | 35.7 | 29.7 | 34.6 |
| Male | 35.8 | 29.3 | 34.9 |

Course level mix by age group (%):

| AgeGroup | Beginner | Intermediate | Advanced |
|---|---|---|---|
| <18 | 34.1 | 29.5 | 36.4 |
| 18-25 | 36.0 | 29.1 | 34.8 |
| 26-35 | 36.0 | 29.8 | 34.2 |

Association strength (Cramer's V): age vs category 0.030; gender vs category 0.030; age vs level 0.013; gender vs level 0.004. All are close to zero: segment preferences are very similar. Largest segment over-indexes (lift):

| Segment | Category | Segment share % | Platform share % | Lift | Enrollments |
|---|---|---|---|---|---|
| <18 / Male | Finance | 10.7 | 8.6 | 1.24x | 85 |
| <18 / Male | Marketing | 9.5 | 8.1 | 1.18x | 75 |
| <18 / Male | Web Development | 9.9 | 8.4 | 1.17x | 78 |
| <18 / Female | Artificial Intelligence | 9.6 | 8.3 | 1.16x | 65 |
| 18-25 / Male | Web Development | 9.6 | 8.4 | 1.14x | 175 |

### 3.5 Behavioral insights
- Mean courses per learner 3.33; median 1; maximum 16.
- 54.0% of learners took exactly one course; top 10% of learners generate 42.3% and top 20% generate 66.5% of enrollments.
- Learner stage by highest level taken: Reached Advanced: 1,608, Reached Intermediate: 739, Beginner only: 653.

## 4. Discussion
Demand is broad: no category dominates and the gap between the most (Data Science) and least (Marketing) popular is small. Because segment preferences are near-identical, differences between age/gender groups are better explained by group size than by taste. The more consequential pattern is behavioral - a small, highly active group and a large single-course majority.

## 5. Recommendations
1. Invest in depth of top-demand categories; test positioning of the lowest.
2. Market to the 26-35 core while piloting outreach to under-18s and 36+ adults.
3. Keep gender-neutral design to preserve near-parity.
4. Build beginner-to-advanced paths and next-course recommendations to convert one-course learners.
5. Create loyalty mechanisms for highly active learners.

## 6. Limitations
Single year of data; no learner-outcome or satisfaction measures; ages limited to 15-35; descriptive associations, not causal claims. Percent differences between segments should be treated cautiously where group sizes are small.

## 7. Conclusion
EduPro serves a young, balanced learner base with broad and uniform interests. Growth levers lie in engagement depth and in reaching age groups currently absent, rather than in tailoring content by gender or age band.
