## 📊 Project 2 Analysis
## Introduction

As a former job seeker, I’ve always been surprised by the lack of data exploring the most optimal jobs and skills in the data science market. I set out to understand what skills top employers request and how to land more pay.

## ❓ Questions to Analyze

To understand the data science job market, I asked the following:

- Do more skills get you better pay?
- What’s the salary for data jobs in different regions?
- What are the top skills of data professionals?
- What’s the pay for the top 10 skills?

## 🛠️ Excel Skills Used

The following Excel skills were utilized for analysis:

- 📊 Pivot Tables
- 📈 Pivot Charts
- 🧮 DAX (Data Analysis Expressions)
- 🔍 Power Query
- 💪 Power Pivot
- 📂 Data Jobs Dataset

The dataset used for this project contains real-world data science job information from 2023. The dataset is available via my Excel course, which provides a foundation for analyzing data using Excel.

It includes detailed information on:

- 👨‍💼 Job titles
- 💰 Salaries
- 📍 Locations
- 🛠️ Skills
- 🔎 Analysis

**1️⃣ Do more skills get you better pay?**

*🔍 Skill*: Power Query (ETL)

*📥 Extract*

- I first used Power Query to extract the original data (data_salary_all.xlsx) and create two queries:

- 🗃️ First one with all the data jobs information
🔧 The second listing the skills for each job ID

*🔄 Transform*

Then, I transformed each query by:

- Changing column types
Removing unnecessary columns
Cleaning text to eliminate specific words
Trimming excess whitespace

-- 📊 data_jobs

 ![data_jobs](/Project2_Analysis/Images/2_Project_Analysis_Screenshot1.png)

-- 🛠️ job_skills

![job_skills](/Project2_Analysis/Images/2_Project_Analysis_Screenshot2.png)

*🔗 Load*

- Finally, I loaded both transformed queries into the workbook, setting the foundation for my subsequent analysis.

-- 📊 data_jobs

![data_jobs](/Project2_Analysis/Images/2_Project_Analysis_Screenshot3.png)

-- 🛠️ job_skills

![jobs_skills](/Project2_Analysis/Images/2_Project_Analysis_Screenshot4.png)

**📊 Analysis**

*💡 Insights*

- There is a positive correlation between the number of skills requested in job postings and the median salary, particularly in roles like Senior Data Engineer and Data Scientist.
- Roles that require fewer skills, like Business Analyst, tend to offer lower salaries, suggesting that more specialized skill sets command higher market value.

![Alt_Text](/Project2_Analysis/Images/Screenshot5.png)

- This trend emphasizes the value of acquiring multiple relevant skills, particularly for individuals aiming for higher-paying roles.

**2️⃣ What’s the salary for data jobs in different regions?**

*🧮 Skills*: PivotTables & DAX

*📈 Pivot Table*

- I created a PivotTable using the Data Model created with Power Pivot
Moved job_title_short to rows
Moved salary_year_avg to values

*🧮 DAX*
```dax
=CALCULATE(
    MEDIAN(data_jobs_all[salary_year_avg]),
    data_jobs_all[job_country] = "United States"
)
```
- To calculate the median yearly salary:
```
Median Salary := MEDIAN(data_jobs_all[salary_year_avg])
```
*📊 Analysis*

*💡 Insights*

- Job roles like Senior Data Engineer and Data Scientist command higher median salaries both in the US and internationally
- The salary disparity between US and Non-US roles is particularly notable in high-tech jobs

![Alt_Text](/Project2_Analysis/Images/Screenshot%206.png)

- These salary insights are important for planning and salary negotiations, helping professionals and companies align their offers with market standards while considering geographical variations.

**3️⃣ What are the top skills of data professionals?**

*🔧 Skill*: Power Pivot

*💪 Power Pivot*

- Created a data model by integrating:
data_jobs_all
data_jobs_skills
- Power Pivot automatically created a relationship after cleaning

*🔗 Data Model*
- Relationship created using job_id

![Alt_Text](/Project2_Analysis/Images/2_Project_Analysis_Screenshot7.png)
*📃 Power Pivot Menu*

- Used to refine the data model and create measures

![Alt_Text](/Project2_Analysis/Images/2_Project_Analysis_Screenshot8.png)
*📊 Analysis*

*💡 Insights*

- SQL and Python dominate as top skills in data-related jobs
- Emerging technologies like AWS and Azure show significant presence

![Alt_Text](/Project2_Analysis/Images/Screenshot%209.png)

- Understanding prevalent skills helps professionals stay competitive and guides learning toward impactful technologies.

*4️⃣ What’s the pay of the top 10 skills?*

*📊 Skill*: Advanced Charts (Pivot Chart)

*📈 PivotChart*

- Created a combo PivotChart:

    - 🪙 Primary Axis → Median Salary (Clustered Column)
    - 👍 Secondary Axis → Skill Likelihood (%) (Line with Markers)

- Customizations:
Added title and axis labels
Removed unnecessary lines
Changed markers to diamonds

*📊 Analysis*

*💡 Insights*

- Higher median salaries are associated with:
Python
Oracle
SQL
Lower salaries and demand:
PowerPoint
Word

![Alt_Text](/Project2_Analysis/Images/Screenshot10.png)

- This highlights the importance of focusing on high-value technical skills to maximize earning potential.

## 🧠 Conclusion

As a data enthusiast and former job seeker, I embarked on this Excel-based project to uncover valuable insights about the data science job market.

Using real-world job postings data, I analyzed:

- Job titles
- Salaries
- Locations
- Skills

By leveraging Excel tools like Power Query, PivotTables, DAX, and charts, I discovered:

Strong correlation between multiple skills and higher salaries
High demand for Python, SQL, and cloud technologies