WITH DailyOperatorMetrics AS (
    SELECT
        dd.FullDateAlternateKey AS Date,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.MonthNumberOfYear AS CalendarMonth,
        dd.EnglishDayNameOfWeek AS DayOfWeek,
        fcc.Shift,
        fcc.WageType,
        fcc.TotalOperators,
        fcc.LevelOneOperators,
        fcc.LevelTwoOperators,
        fcc.Calls,
        fcc.AutomaticResponses,
        fcc.Orders,
        fcc.IssuesRaised,
        fcc.AverageTimePerIssue,
        fcc.ServiceGrade,
        -- Calculate ratios
        ROUND(CAST(fcc.Calls AS FLOAT) / NULLIF(fcc.TotalOperators, 0), 2) AS CallsPerOperator,
        ROUND(CAST(fcc.Orders AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS ConversionRate,
        ROUND(CAST(fcc.LevelTwoOperators AS FLOAT) / NULLIF(fcc.TotalOperators, 0) * 100, 2) AS SeniorOperatorPct,
        ROUND(CAST(fcc.IssuesRaised AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS IssueRate
    FROM FactCallCenter fcc
    INNER JOIN DimDate dd ON fcc.DateKey = dd.DateKey
),
StaffingBuckets AS (
    SELECT
        *,
        CASE
            WHEN TotalOperators <= 5 THEN '1-5 Operators'
            WHEN TotalOperators <= 10 THEN '6-10 Operators'
            WHEN TotalOperators <= 15 THEN '11-15 Operators'
            WHEN TotalOperators <= 20 THEN '16-20 Operators'
            ELSE '21+ Operators'
        END AS StaffingLevel,
        CASE
            WHEN SeniorOperatorPct < 20 THEN 'Low Senior (<20%)'
            WHEN SeniorOperatorPct < 40 THEN 'Medium Senior (20-40%)'
            ELSE 'High Senior (40%+)'
        END AS SeniorMixLevel,
        CASE
            WHEN CallsPerOperator < 50 THEN 'Low Load (<50)'
            WHEN CallsPerOperator < 100 THEN 'Medium Load (50-100)'
            WHEN CallsPerOperator < 150 THEN 'High Load (100-150)'
            ELSE 'Very High Load (150+)'
        END AS WorkloadLevel
    FROM DailyOperatorMetrics
),
StaffingImpactAnalysis AS (
    SELECT
        StaffingLevel,
        SeniorMixLevel,
        WorkloadLevel,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(TotalOperators), 2) AS AvgTotalOperators,
        ROUND(AVG(SeniorOperatorPct), 2) AS AvgSeniorOperatorPct,
        ROUND(AVG(Calls), 2) AS AvgCalls,
        ROUND(AVG(CallsPerOperator), 2) AS AvgCallsPerOperator,
        ROUND(AVG(ConversionRate), 2) AS AvgConversionRate,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(AverageTimePerIssue), 2) AS AvgTimePerIssue,
        ROUND(AVG(Orders), 2) AS AvgOrders,
        -- Performance variability
        ROUND(STDDEV_SAMP(ConversionRate), 2) AS StdDevConversionRate,
        ROUND(STDDEV_SAMP(ServiceGrade), 4) AS StdDevServiceGrade,
        -- Min/Max for ranges
        ROUND(MIN(ConversionRate), 2) AS MinConversionRate,
        ROUND(MAX(ConversionRate), 2) AS MaxConversionRate,
        ROUND(MIN(ServiceGrade), 4) AS MinServiceGrade,
        ROUND(MAX(ServiceGrade), 4) AS MaxServiceGrade
    FROM StaffingBuckets
    GROUP BY StaffingLevel, SeniorMixLevel, WorkloadLevel
),
PerformanceScoring AS (
    SELECT
        *,
        -- Composite performance score (higher is better)
        ROUND((AvgConversionRate / 10) + (AvgServiceGrade * 100) - (AvgIssueRate / 2), 2) AS PerformanceScore,
        RANK() OVER (ORDER BY AvgConversionRate DESC, AvgServiceGrade DESC) AS OverallRank
    FROM StaffingImpactAnalysis
    WHERE ObservationCount >= 5  -- Filter out statistically insignificant groups
)
SELECT
    StaffingLevel,
    SeniorMixLevel,
    WorkloadLevel,
    ObservationCount,
    AvgTotalOperators,
    AvgSeniorOperatorPct,
    AvgCalls,
    AvgCallsPerOperator,
    AvgConversionRate,
    AvgServiceGrade,
    AvgIssueRate,
    AvgTimePerIssue,
    AvgOrders,
    StdDevConversionRate,
    StdDevServiceGrade,
    MinConversionRate,
    MaxConversionRate,
    MinServiceGrade,
    MaxServiceGrade,
    PerformanceScore,
    OverallRank,
    CASE
        WHEN OverallRank <= 3 THEN 'Optimal Configuration'
        WHEN OverallRank <= 10 THEN 'Good Configuration'
        WHEN OverallRank <= 20 THEN 'Acceptable Configuration'
        ELSE 'Suboptimal Configuration'
    END AS ConfigurationAssessment
FROM PerformanceScoring
ORDER BY PerformanceScore DESC;
