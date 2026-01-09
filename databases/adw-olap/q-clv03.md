# Customer Lifecycle Stage Analysis - KPI Documentation

This document provides a comprehensive analysis of all Key Performance Indicators (KPIs) calculated in the customer lifecycle stage SQL query. The query tracks customer progression through lifecycle stages and identifies stage transition opportunities.

---

# KPI 1: GrossProfit (per transaction)

## Definition
**GrossProfit** calculates the gross profit for each individual transaction by subtracting the total product cost from the sales amount. This measures the margin contribution of each sale.

**SQL Expression:**
```sql
fis.SalesAmount - fis.TotalProductCost AS GrossProfit
```

**Mathematical Formula:**
$$\text{GrossProfit} = \text{SalesAmount} - \text{TotalProductCost}$$

**Business Purpose:** Provides transaction-level profitability for margin analysis and customer value assessment.

## Examples
- Transaction A: $500 sales, $300 costs → $200 gross profit (40% margin)
- Transaction B: $1,000 sales, $950 costs → $50 gross profit (5% margin, low-margin sale)
- Transaction C: $200 sales, $80 costs → $120 gross profit (60% margin, high-margin sale)

---

# KPI 2: PurchaseSequence

## Definition
**PurchaseSequence** assigns a sequential order number to each transaction within a customer's purchase history, starting from 1 for their first purchase. This enables analysis of customer behavior evolution over time.

**SQL Expression:**
```sql
ROW_NUMBER() OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS PurchaseSequence
```

**Mathematical Formula:**
$$\text{PurchaseSequence}_i = i \text{ where } i \text{ is the rank of transaction by OrderDate within customer}$$

For customer $c$, if transactions are ordered by date as $t_1, t_2, ..., t_n$, then:
$$\text{PurchaseSequence}(t_i) = i$$

**Business Purpose:** Enables cohort analysis, first-order vs. repeat-order comparisons, and tracking of customer journey progression.

## Examples
For Customer A's purchases:
- 2023-01-15: PurchaseSequence = 1 (first purchase)
- 2023-03-20: PurchaseSequence = 2 (second purchase)
- 2023-06-10: PurchaseSequence = 3 (third purchase)
- 2023-12-05: PurchaseSequence = 4 (fourth purchase)

**Analysis Applications:**
- Compare average order value for PurchaseSequence = 1 vs. > 1
- Analyze product preferences by purchase sequence
- Identify drop-off patterns (e.g., many customers with sequence = 1 only)

---

# KPI 3: CumulativeOrders

## Definition
**CumulativeOrders** counts the running total of distinct orders a customer has placed up to and including each transaction date. This shows the customer's order count at each point in their history.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.SalesOrderNumber) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS CumulativeOrders
```

**Mathematical Formula:**
$$\text{CumulativeOrders}(t_i) = |\{o : o \in \text{orders}, \text{OrderDate}(o) \leq \text{OrderDate}(t_i)\}|$$

where $|\cdot|$ denotes count of distinct orders up to transaction $t_i$.

**Business Purpose:** Tracks customer engagement progression and identifies when customers cross engagement thresholds (e.g., 5 orders, 10 orders).

## Examples
Customer B's timeline:
- Order 1 (2023-01-15, 3 line items): CumulativeOrders = 1, 1, 1 for each line
- Order 2 (2023-02-10, 2 line items): CumulativeOrders = 2, 2 for each line
- Order 3 (2023-04-20, 1 line item): CumulativeOrders = 3

**Note:** Multiple line items in same order have same CumulativeOrders value.

---

# KPI 4: CumulativeRevenue

## Definition
**CumulativeRevenue** calculates the running total of sales amount for a customer up to and including each transaction, showing their lifetime value progression over time.

**SQL Expression:**
```sql
SUM(fis.SalesAmount) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS CumulativeRevenue
```

**Mathematical Formula:**
$$\text{CumulativeRevenue}(t_i) = \sum_{j=1}^{i} \text{SalesAmount}(t_j)$$

where transactions are ordered by date: $t_1, t_2, ..., t_i$.

**Business Purpose:** Tracks customer value accumulation, identifies high-value moments, and supports lifetime value projection models.

## Examples
Customer C's revenue progression:
- Transaction 1 (2023-01-01): $100 → CumulativeRevenue = $100
- Transaction 2 (2023-02-01): $150 → CumulativeRevenue = $250
- Transaction 3 (2023-03-01): $200 → CumulativeRevenue = $450
- Transaction 4 (2023-04-01): $175 → CumulativeRevenue = $625

**Analysis:**
- Identify when customers cross $1,000 threshold
- Calculate time-to-$X-revenue metrics
- Detect accelerating vs. decelerating value patterns

---

# KPI 5: PreviousOrderDate

## Definition
**PreviousOrderDate** retrieves the date of the customer's immediately preceding purchase, enabling calculation of inter-purchase intervals.

**SQL Expression:**
```sql
LAG(fis.OrderDate) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS PreviousOrderDate
```

**Mathematical Formula:**
$$\text{PreviousOrderDate}(t_i) = \begin{cases}
\text{OrderDate}(t_{i-1}) & \text{if } i > 1 \\
\text{NULL} & \text{if } i = 1
\end{cases}$$

**Business Purpose:** Foundation for calculating time between purchases, detecting changes in purchase frequency, and identifying purchase cycle patterns.

## Examples
Customer D's purchase dates:
- Purchase 1 (2023-01-15): PreviousOrderDate = NULL (first purchase)
- Purchase 2 (2023-02-20): PreviousOrderDate = 2023-01-15
- Purchase 3 (2023-05-10): PreviousOrderDate = 2023-02-20
- Purchase 4 (2023-12-01): PreviousOrderDate = 2023-05-10

---

# KPI 6: DaysSincePreviousOrder

## Definition
**DaysSincePreviousOrder** calculates the number of days between consecutive purchases for the same customer, measuring inter-purchase interval.

**SQL Expression:**
```sql
(fis.OrderDate::DATE - (LAG(fis.OrderDate) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate))::DATE) AS DaysSincePreviousOrder
```

**Mathematical Formula:**
$$\text{DaysSincePreviousOrder}(t_i) = \begin{cases}
\text{OrderDate}(t_i) - \text{OrderDate}(t_{i-1}) & \text{if } i > 1 \\
\text{NULL} & \text{if } i = 1
\end{cases}$$

**Business Purpose:** Identifies natural purchase cycles, detects anomalies (unusually long/short intervals), and predicts next purchase timing.

## Examples
Customer E's inter-purchase intervals:
- Purchase 1 (2023-01-01): DaysSincePreviousOrder = NULL
- Purchase 2 (2023-01-31): DaysSincePreviousOrder = 30 days (monthly pattern)
- Purchase 3 (2023-03-02): DaysSincePreviousOrder = 30 days (consistent monthly)
- Purchase 4 (2023-06-15): DaysSincePreviousOrder = 105 days (deviation, potential issue)

**Alert Trigger:** If typical interval is 30 days but current is 90 days, trigger re-engagement campaign.

---

# KPI 7: FirstPurchaseDate

## Definition
**FirstPurchaseDate** identifies the date of the customer's very first purchase, establishing the customer relationship start date.

**SQL Expression:**
```sql
MIN(cpt.OrderDate) AS FirstPurchaseDate
```

**Mathematical Formula:**
$$\text{FirstPurchaseDate} = \min_{i}(\text{OrderDate}_i)$$

**Business Purpose:** Defines customer cohort membership, enables age-based analysis, and serves as baseline for tenure calculations.

## Examples
- Customer A: FirstPurchaseDate = 2020-06-15 → June 2020 cohort
- Customer B: FirstPurchaseDate = 2023-11-20 → November 2023 cohort
- Customer C: FirstPurchaseDate = 2019-01-03 → January 2019 cohort (oldest)

---

# KPI 8: LastPurchaseDate

## Definition
**LastPurchaseDate** identifies the date of the customer's most recent purchase, critical for recency analysis.

**SQL Expression:**
```sql
MAX(cpt.OrderDate) AS LastPurchaseDate
```

**Mathematical Formula:**
$$\text{LastPurchaseDate} = \max_{i}(\text{OrderDate}_i)$$

**Business Purpose:** Determines current activity status and is used to calculate days since last purchase for churn prediction.

## Examples
- Customer A: LastPurchaseDate = 2024-12-15 (recent, active)
- Customer B: LastPurchaseDate = 2023-06-20 (18 months ago, at risk)
- Customer C: LastPurchaseDate = 2021-08-10 (churned)

---

# KPI 9: CustomerAgeDays

## Definition
**CustomerAgeDays** calculates the total number of days since the customer's first purchase to the current date, representing the customer's age/tenure with the business.

**SQL Expression:**
```sql
(CURRENT_DATE - MIN(cpt.OrderDate)::DATE) AS CustomerAgeDays
```

**Mathematical Formula:**
$$\text{CustomerAgeDays} = \text{CURRENT\_DATE} - \text{FirstPurchaseDate}$$

**Business Purpose:** Differentiates new vs. longstanding customers, enables cohort-based comparisons, and supports lifecycle stage classification.

## Examples
- Customer A: First purchase 2023-12-10, analyzed 2024-01-10 → 31 days (new)
- Customer B: First purchase 2023-01-15, analyzed 2024-01-10 → 360 days (~1 year)
- Customer C: First purchase 2019-06-01, analyzed 2024-01-10 → 1,684 days (~4.6 years)

**Stage Thresholds:**
- 0-90 days: New customer phase
- 91-365 days: Developing phase
- 365+ days: Established customer

---

# KPI 10: DaysSinceLastPurchase

## Definition
**DaysSinceLastPurchase** calculates the number of days from the customer's last purchase to the current date, the primary recency metric.

**SQL Expression:**
```sql
(CURRENT_DATE - MAX(cpt.OrderDate)::DATE) AS DaysSinceLastPurchase
```

**Mathematical Formula:**
$$\text{DaysSinceLastPurchase} = \text{CURRENT\_DATE} - \text{LastPurchaseDate}$$

**Business Purpose:** Primary indicator of churn risk. Used to trigger retention campaigns and classify lifecycle stages.

## Examples
- Customer A: 15 days since last purchase → active
- Customer B: 200 days since last purchase → at risk
- Customer C: 400 days since last purchase → likely churned

**Critical Thresholds:**
- 0-180 days: Active engagement
- 181-365 days: At-risk zone
- 365+ days: Churned

---

# KPI 11: ActiveLifespanDays

## Definition
**ActiveLifespanDays** measures the time span between a customer's first and last purchase, representing the duration of their active purchasing period (distinct from CustomerAgeDays which measures from first purchase to today).

**SQL Expression:**
```sql
(MAX(cpt.OrderDate)::DATE - MIN(cpt.OrderDate)::DATE) AS ActiveLifespanDays
```

**Mathematical Formula:**
$$\text{ActiveLifespanDays} = \text{LastPurchaseDate} - \text{FirstPurchaseDate}$$

**Relationship:**
$$\text{CustomerAgeDays} = \text{ActiveLifespanDays} + \text{DaysSinceLastPurchase}$$

**Business Purpose:** Measures actual engagement duration. A customer with 1000 CustomerAgeDays but 100 ActiveLifespanDays was only active for 100 days then churned.

## Examples
- Customer A: First 2023-01-01, Last 2024-01-01 → ActiveLifespanDays = 365
  - If today is 2024-06-01, CustomerAgeDays = 517, DaysSinceLastPurchase = 152
- Customer B: First 2023-01-01, Last 2023-01-15 → ActiveLifespanDays = 14 (one-time buyer)
  - If today is 2024-01-01, CustomerAgeDays = 365, DaysSinceLastPurchase = 351

**Interpretation:**
- High ActiveLifespanDays: Long engagement period (loyal)
- Low ActiveLifespanDays: Short engagement burst (may be one-time or seasonal)

---

# KPI 12: TotalOrders

## Definition
**TotalOrders** counts the total number of distinct orders a customer has placed over their lifetime.

**SQL Expression:**
```sql
COUNT(DISTINCT cpt.SalesOrderNumber) AS TotalOrders
```

**Mathematical Formula:**
$$\text{TotalOrders} = |\{\text{SalesOrderNumber}_i : i \in \text{all transactions}\}|$$

**Business Purpose:** Primary frequency metric. Used to classify customers into engagement tiers and lifecycle stages.

## Examples
- Customer A: 25 orders → highly engaged
- Customer B: 3 orders → moderate engagement
- Customer C: 1 order → one-time buyer

**Stage Classification Thresholds:**
- 1-2 orders: New
- 3-4 orders: Developing
- 5-10 orders: Growing
- 11+ orders: Mature

---

# KPI 13: MaxOrders

## Definition
**MaxOrders** retrieves the maximum value of CumulativeOrders, which should equal TotalOrders. This is a verification metric to ensure window function calculations are correct.

**SQL Expression:**
```sql
MAX(cpt.CumulativeOrders) AS MaxOrders
```

**Mathematical Formula:**
$$\text{MaxOrders} = \max_{i}(\text{CumulativeOrders}_i) = \text{TotalOrders}$$

**Business Purpose:** Quality assurance check. MaxOrders should always equal TotalOrders.

## Examples
- If TotalOrders = 10 and MaxOrders = 10 → Correct
- If TotalOrders = 10 and MaxOrders = 9 → Data quality issue

---

# KPI 14: TotalRevenue

## Definition
**TotalRevenue** sums all sales amounts across all customer transactions, representing lifetime monetary contribution.

**SQL Expression:**
```sql
ROUND(SUM(cpt.SalesAmount), 2) AS TotalRevenue
```

**Mathematical Formula:**
$$\text{TotalRevenue} = \sum_{i=1}^{n} \text{SalesAmount}_i$$

**Business Purpose:** Primary customer value metric. Used for ranking, segmentation, and ROI analysis.

## Examples
- Customer A: $50,000 total revenue → high-value
- Customer B: $2,500 total revenue → moderate-value
- Customer C: $150 total revenue → low-value

---

# KPI 15: TotalGrossProfit

## Definition
**TotalGrossProfit** sums the gross profit across all customer transactions, representing lifetime margin contribution.

**SQL Expression:**
```sql
ROUND(SUM(cpt.GrossProfit), 2) AS TotalGrossProfit
```

**Mathematical Formula:**
$$\text{TotalGrossProfit} = \sum_{i=1}^{n} \text{GrossProfit}_i = \sum_{i=1}^{n} (\text{SalesAmount}_i - \text{TotalProductCost}_i)$$

**Business Purpose:** More accurate value metric than revenue, accounting for cost structure and margin differences.

## Examples
- Customer A: $50,000 revenue, $20,000 profit → 40% lifetime margin
- Customer B: $10,000 revenue, $8,000 profit → 80% lifetime margin (high-margin buyer)
- Customer C: $100,000 revenue, $5,000 profit → 5% lifetime margin (low-margin buyer)

**Insight:** Customer B is more valuable per dollar than Customer C despite lower revenue.

---

# KPI 16: AvgTransactionValue

## Definition
**AvgTransactionValue** calculates the mean sales amount per line item across all customer purchases.

**SQL Expression:**
```sql
ROUND(AVG(cpt.SalesAmount), 2) AS AvgTransactionValue
```

**Mathematical Formula:**
$$\text{AvgTransactionValue} = \frac{1}{n}\sum_{i=1}^{n} \text{SalesAmount}_i$$

where $n$ is the total number of line items.

**Business Purpose:** Indicates typical basket size and price point preference.

## Examples
- Customer A: $250 average → premium buyer
- Customer B: $50 average → mid-market buyer
- Customer C: $15 average → value/discount buyer

---

# KPI 17: AvgDaysBetweenOrders (calculated from timeline)

## Definition
**AvgDaysBetweenOrders** calculates the mean number of days between consecutive purchases, indicating the customer's natural purchase cycle.

**SQL Expression:**
```sql
ROUND(AVG(cpt.DaysSincePreviousOrder), 2) AS AvgDaysBetweenOrders
```

**Mathematical Formula:**
$$\text{AvgDaysBetweenOrders} = \frac{1}{n-1}\sum_{i=2}^{n} \text{DaysSincePreviousOrder}_i$$

where $n$ is the total number of orders.

**Business Purpose:** Identifies natural replenishment cycle. Used for timing re-engagement campaigns and predicting next purchase.

## Examples
- Customer A: 30 days average → monthly buyer
- Customer B: 90 days average → quarterly buyer
- Customer C: 7 days average → weekly buyer (possible business/reseller)

**Application:** If customer typically orders every 30 days but hasn't ordered in 60 days, trigger campaign.

---

# KPI 18: AvgPurchaseCycleDays

## Definition
**AvgPurchaseCycleDays** calculates an alternative measure of inter-purchase interval by dividing the total active lifespan by the number of purchase intervals. This provides a different perspective than AvgDaysBetweenOrders.

**SQL Expression:**
```sql
ROUND(CAST((MAX(cpt.OrderDate)::DATE - MIN(cpt.OrderDate)::DATE) AS DOUBLE) / NULLIF(COUNT(DISTINCT cpt.SalesOrderNumber) - 1, 0), 2) AS AvgPurchaseCycleDays
```

**Mathematical Formula:**
$$\text{AvgPurchaseCycleDays} = \frac{\text{ActiveLifespanDays}}{\text{TotalOrders} - 1} = \frac{\text{LastPurchaseDate} - \text{FirstPurchaseDate}}{\text{TotalOrders} - 1}$$

**Relationship:**
$$\text{AvgPurchaseCycleDays} \approx \text{AvgDaysBetweenOrders}$$

These should be similar but may differ slightly due to calculation method.

**Business Purpose:** Alternative measure of purchase frequency that's less sensitive to individual transaction variations.

## Examples
- Customer A: First 2023-01-01, Last 2023-12-31, 13 orders
  - AvgPurchaseCycleDays = 365 / (13-1) = 30.4 days
- Customer B: First 2023-01-01, Last 2023-07-01, 7 orders
  - AvgPurchaseCycleDays = 182 / (7-1) = 30.3 days

**Note:** For single-order customers, this is NULL (division by zero protection).

---

# KPI 19: CustomerAgeYears

## Definition
**CustomerAgeYears** converts CustomerAgeDays into years for more intuitive understanding of customer tenure.

**SQL Expression:**
```sql
ROUND(ccs.CustomerAgeDays / 365.25, 2) AS CustomerAgeYears
```

**Mathematical Formula:**
$$\text{CustomerAgeYears} = \frac{\text{CustomerAgeDays}}{365.25}$$

**Business Purpose:** Human-readable tenure metric for reporting and segmentation.

## Examples
- 30 days → 0.08 years (~1 month)
- 365 days → 1.00 years
- 1095 days → 3.00 years
- 1825 days → 5.00 years

---

# KPI 20: LifecycleStage

## Definition
**LifecycleStage** classifies customers into one of seven strategic lifecycle stages based on their age, engagement level, and recency. This is the core classification metric that drives all lifecycle-based strategies.

**SQL Expression:**
```sql
CASE
    WHEN ccs.DaysSinceLastPurchase > 365 THEN 'Churned'
    WHEN ccs.DaysSinceLastPurchase > 180 AND ccs.TotalOrders >= 3 THEN 'At-Risk'
    WHEN ccs.CustomerAgeDays <= 90 AND ccs.TotalOrders <= 2 THEN 'New'
    WHEN (ccs.CustomerAgeDays BETWEEN 91 AND 180) OR (ccs.TotalOrders BETWEEN 2 AND 4) THEN 'Developing'
    WHEN (ccs.CustomerAgeDays BETWEEN 181 AND 365) OR (ccs.TotalOrders BETWEEN 5 AND 10) THEN 'Growing'
    WHEN ccs.CustomerAgeDays > 365 AND ccs.TotalOrders >= 11 AND ccs.DaysSinceLastPurchase <= 180 THEN 'Mature'
    ELSE 'Inactive'
END AS LifecycleStage
```

**Stage Definitions:**

### 1. Churned
**Criteria:** $\text{DaysSinceLastPurchase} > 365$

**Profile:** No purchase in over 1 year, regardless of prior engagement.

**Characteristics:**
- Disengaged from brand
- Low recovery probability
- May have switched to competitor

**Example:** Customer last purchased Jan 2023, analyzed Jan 2025 → Churned

### 2. At-Risk
**Criteria:** $\text{DaysSinceLastPurchase} > 180$ AND $\text{TotalOrders} \geq 3$

**Profile:** Was previously engaged (3+ orders) but hasn't purchased in 6-12 months.

**Characteristics:**
- High historical engagement
- Recent disengagement
- High-value recovery target
- Urgent intervention needed

**Example:** Customer with 15 orders, last purchase 250 days ago → At-Risk

### 3. New
**Criteria:** $\text{CustomerAgeDays} \leq 90$ AND $\text{TotalOrders} \leq 2$

**Profile:** Recent first-time or second-time buyers, still in onboarding phase.

**Characteristics:**
- Fresh relationship (< 3 months)
- 1-2 orders only
- High potential for development
- Critical period for habit formation

**Example:** Customer joined 60 days ago, made 1 purchase → New

### 4. Developing
**Criteria:** ($\text{CustomerAgeDays}$ BETWEEN 91 AND 180) OR ($\text{TotalOrders}$ BETWEEN 2 AND 4)

**Profile:** Transitioning from new to regular customer, building engagement.

**Characteristics:**
- 3-6 months old OR 2-4 orders
- Establishing purchase patterns
- Not yet fully loyal
- Needs nurturing

**Example:**
- Customer A: 120 days old, 3 orders → Developing
- Customer B: 45 days old, 3 orders → Developing (age OR orders condition)

### 5. Growing
**Criteria:** ($\text{CustomerAgeDays}$ BETWEEN 181 AND 365) OR ($\text{TotalOrders}$ BETWEEN 5 AND 10)

**Profile:** Regular customers with established patterns, actively growing engagement.

**Characteristics:**
- 6-12 months old OR 5-10 orders
- Regular purchase patterns
- Expanding product usage
- High conversion to Mature stage potential

**Example:**
- Customer A: 250 days old, 7 orders → Growing
- Customer B: 90 days old, 8 orders → Growing (high velocity)

### 6. Mature
**Criteria:** $\text{CustomerAgeDays} > 365$ AND $\text{TotalOrders} \geq 11$ AND $\text{DaysSinceLastPurchase} \leq 180$

**Profile:** Long-term, highly engaged customers who are actively purchasing.

**Characteristics:**
- Over 1 year old
- 11+ lifetime orders
- Recent purchase (< 6 months)
- Highest loyalty
- Most valuable segment

**Example:** Customer joined 3 years ago, 45 orders, last purchase 60 days ago → Mature

### 7. Inactive
**Fallback:** Doesn't fit any other category

**Profile:** Low engagement customers who don't meet criteria for other stages.

**Characteristics:**
- Various patterns not captured above
- Generally low engagement
- Mixed age and order counts
- May include edge cases

**Example:** Customer 200 days old, 2 orders, last purchase 100 days ago → Inactive

**Business Purpose:** Provides clear, actionable segmentation for lifecycle marketing strategies. Each stage has distinct needs and optimal interventions.

## Examples

**Lifecycle Progression Examples:**

**Customer Journey 1 (Successful):**
1. Day 1: First purchase → New
2. Day 45: Second purchase → New (still < 90 days, ≤ 2 orders)
3. Day 95: Third purchase → Developing (passed 90 days)
4. Day 150: Fifth purchase → Growing (5 orders)
5. Day 400: Twelfth purchase → Mature (>365 days, 11+ orders, recent)

**Customer Journey 2 (At Risk):**
1. Day 1-300: Accumulate 10 orders → Growing
2. Day 400: 11th purchase → Would be Mature if purchased recently
3. Day 600: No purchases for 200 days → At-Risk (>180 days, had 11 orders)
4. Day 900: No purchases for 500 days → Churned (>365 days)

**Customer Journey 3 (Quick Churn):**
1. Day 1: First purchase → New
2. Day 450: Still only 1 purchase → Churned (>365 days since last = only purchase)

---

# KPI 21: CustomerCount (by Stage)

## Definition
**CustomerCount** aggregates the number of customers in each lifecycle stage, showing stage distribution.

**SQL Expression:**
```sql
COUNT(*) AS CustomerCount
```

**Mathematical Formula:**
$$\text{CustomerCount}_s = |\{c : \text{LifecycleStage}(c) = s\}|$$

for each stage $s$.

**Business Purpose:** Reveals customer base health and identifies which stages need attention.

## Examples
Distribution across 10,000 customers:
- New: 1,500 (15%) - healthy acquisition
- Developing: 2,000 (20%)
- Growing: 1,800 (18%)
- Mature: 1,200 (12%) - solid loyal base
- At-Risk: 800 (8%) - needs attention
- Churned: 2,500 (25%) - high churn rate
- Inactive: 200 (2%)

**Health Indicators:**
- High % in New: Good acquisition
- High % in Mature: Strong loyalty
- High % in At-Risk/Churned: Retention problem

---

# KPI 22: StagePct

## Definition
**StagePct** calculates what percentage of total customers each lifecycle stage represents.

**SQL Expression:**
```sql
ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM LifecycleStageAssignment), 2) AS StagePct
```

**Mathematical Formula:**
$$\text{StagePct}_s = \frac{\text{CustomerCount}_s}{\sum_{s'} \text{CustomerCount}_{s'}} \times 100$$

**Range:** 0% to 100%, sum = 100%

**Business Purpose:** Enables proportional comparison and benchmark tracking over time.

## Examples
- New: 15% (good if stable or growing)
- Mature: 12% (target: 15-25%)
- At-Risk: 8% (red flag if > 10%)
- Churned: 25% (concerning, target < 20%)

---

# KPI 23: AvgCustomerAgeYears (by Stage)

## Definition
**AvgCustomerAgeYears** calculates the mean customer age in years within each lifecycle stage, validating stage definitions.

**SQL Expression:**
```sql
ROUND(AVG(lsa.CustomerAgeYears), 2) AS AvgCustomerAgeYears
```

**Mathematical Formula:**
$$\text{AvgCustomerAgeYears}_s = \frac{1}{n_s}\sum_{c \in s} \text{CustomerAgeYears}(c)$$

**Business Purpose:** Quality check for stage classification. Verifies age-based stage logic is working correctly.

## Examples
Expected averages by stage:
- New: 0.15 years (~2 months)
- Developing: 0.40 years (~5 months)
- Growing: 0.75 years (~9 months)
- Mature: 2.50 years
- At-Risk: 1.80 years
- Churned: 3.00 years (older customers who left)

---

# KPI 24: AvgDaysSinceLastPurchase (by Stage)

## Definition
**AvgDaysSinceLastPurchase** calculates the mean days since last purchase for customers in each stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.DaysSinceLastPurchase), 0) AS AvgDaysSinceLastPurchase
```

**Mathematical Formula:**
$$\text{AvgDaysSinceLastPurchase}_s = \frac{1}{n_s}\sum_{c \in s} \text{DaysSinceLastPurchase}(c)$$

**Business Purpose:** Validates recency-based stage logic and sets campaign timing.

## Examples
Expected averages by stage:
- New: 25 days (recent)
- Developing: 40 days
- Growing: 50 days
- Mature: 60 days (still recent despite older age)
- At-Risk: 250 days (by definition 180-365)
- Churned: 550 days (over 1 year)

---

# KPI 25: AvgTotalOrders (by Stage)

## Definition
**AvgTotalOrders** calculates the mean lifetime order count for customers in each stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.TotalOrders), 2) AS AvgTotalOrders
```

**Mathematical Formula:**
$$\text{AvgTotalOrders}_s = \frac{1}{n_s}\sum_{c \in s} \text{TotalOrders}(c)$$

**Business Purpose:** Validates engagement-based stage logic and characterizes stage behavior.

## Examples
Expected averages by stage:
- New: 1.5 orders (1-2 by definition)
- Developing: 3.2 orders (2-4 range)
- Growing: 7.5 orders (5-10 range)
- Mature: 25 orders (11+ orders)
- At-Risk: 12 orders (historically engaged)
- Churned: 4 orders (mixed engagement)

---

# KPI 26: AvgLifetimeRevenue (by Stage)

## Definition
**AvgLifetimeRevenue** calculates the mean total revenue per customer within each lifecycle stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.TotalRevenue), 2) AS AvgLifetimeRevenue
```

**Mathematical Formula:**
$$\text{AvgLifetimeRevenue}_s = \frac{1}{n_s}\sum_{c \in s} \text{TotalRevenue}(c)$$

**Business Purpose:** Quantifies average value by stage, informing investment levels and prioritization.

## Examples
Expected averages by stage:
- New: $500 (early stage)
- Developing: $1,500
- Growing: $4,000
- Mature: $20,000 (highest value)
- At-Risk: $8,000 (high value at risk!)
- Churned: $2,000

**Strategic Insight:** At-Risk customers with $8,000 average justify high retention investment.

---

# KPI 27: AvgLifetimeProfit (by Stage)

## Definition
**AvgLifetimeProfit** calculates the mean gross profit per customer within each lifecycle stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.TotalGrossProfit), 2) AS AvgLifetimeProfit
```

**Mathematical Formula:**
$$\text{AvgLifetimeProfit}_s = \frac{1}{n_s}\sum_{c \in s} \text{TotalGrossProfit}(c)$$

**Business Purpose:** More accurate value metric than revenue for determining intervention budgets.

## Examples
Expected averages by stage:
- New: $200 (40% margin on $500)
- Developing: $600
- Growing: $1,600
- Mature: $8,000
- At-Risk: $3,200 (justifies up to ~$1,000 retention spend)

---

# KPI 28: AvgTransactionValue (by Stage)

## Definition
**AvgTransactionValue** calculates the mean transaction size for customers in each lifecycle stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.AvgTransactionValue), 2) AS AvgTransactionValue
```

**Mathematical Formula:**
$$\text{AvgTransactionValue}_s = \frac{1}{n_s}\sum_{c \in s} \text{AvgTransactionValue}(c)$$

This is the average of averages across customers in the stage.

**Business Purpose:** Identifies whether basket size changes across lifecycle stages.

## Examples
- New: $120 (learning, small baskets)
- Developing: $150 (growing confidence)
- Growing: $180 (expanding purchases)
- Mature: $200 (confident, larger baskets)

**Insight:** If Mature customers have higher average transaction value, upselling is working.

---

# KPI 29: AvgDaysBetweenOrders (by Stage)

## Definition
**AvgDaysBetweenOrders** calculates the mean inter-purchase interval for customers in each lifecycle stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.AvgDaysBetweenOrders), 0) AS AvgDaysBetweenOrders
```

**Mathematical Formula:**
$$\text{AvgDaysBetweenOrders}_s = \frac{1}{n_s}\sum_{c \in s} \text{AvgDaysBetweenOrders}(c)$$

**Business Purpose:** Identifies typical purchase frequency by stage for campaign timing.

## Examples
Expected averages by stage:
- New: N/A or 60 days (limited data)
- Developing: 45 days
- Growing: 35 days (accelerating)
- Mature: 30 days (regular pattern)

---

# KPI 30: TotalStageRevenue

## Definition
**TotalStageRevenue** sums the total revenue generated by all customers within a lifecycle stage.

**SQL Expression:**
```sql
ROUND(SUM(lsa.TotalRevenue), 2) AS TotalStageRevenue
```

**Mathematical Formula:**
$$\text{TotalStageRevenue}_s = \sum_{c \in s} \text{TotalRevenue}(c)$$

**Business Purpose:** Identifies which stages drive total business value, often revealing concentration in Mature stage.

## Examples
With $50M total revenue:
- Mature (12% of customers): $30M (60% of revenue)
- Growing (18% of customers): $12M (24%)
- At-Risk (8% of customers): $5M (10%)
- All others: $3M (6%)

**Insight:** Mature stage drives disproportionate value despite smaller customer count.

---

# KPI 31: RevenueSharePct (by Stage)

## Definition
**RevenueSharePct** calculates what percentage of total company revenue each lifecycle stage generates.

**SQL Expression:**
```sql
ROUND(100.0 * SUM(lsa.TotalRevenue) / (SELECT SUM(TotalRevenue) FROM LifecycleStageAssignment), 2) AS RevenueSharePct
```

**Mathematical Formula:**
$$\text{RevenueSharePct}_s = \frac{\text{TotalStageRevenue}_s}{\sum_{s'} \text{TotalStageRevenue}_{s'}} \times 100$$

**Range:** 0% to 100%, sum = 100%

**Business Purpose:** Reveals value concentration and guides resource allocation decisions.

## Examples
Typical distribution:
- Mature: 60% of revenue from 12% of customers → 5x concentration
- Growing: 24% of revenue from 18% of customers → 1.3x concentration
- At-Risk: 10% of revenue from 8% of customers → 1.25x concentration (high risk!)
- New: 3% of revenue from 15% of customers → 0.2x concentration

**Risk Assessment:** 10% revenue from At-Risk represents major vulnerability.

---

# KPI 32: AvgYearlyIncome (by Stage)

## Definition
**AvgYearlyIncome** calculates the mean annual income of customers within each lifecycle stage.

**SQL Expression:**
```sql
ROUND(AVG(lsa.YearlyIncome), 2) AS AvgYearlyIncome
```

**Mathematical Formula:**
$$\text{AvgYearlyIncome}_s = \frac{1}{n_s}\sum_{c \in s} \text{YearlyIncome}(c)$$

**Business Purpose:** Links lifecycle behavior to economic capacity and demographics.

## Examples
- Mature: $85,000 average (affluent, long-term customers)
- Growing: $70,000 average
- New: $65,000 average (mixed demographic)
- Churned: $55,000 average (may indicate product-market fit for income level)

---

# KPI 33: NextTargetStage

## Definition
**NextTargetStage** identifies the next lifecycle stage a customer should progress to, creating clear advancement goals.

**SQL Expression:**
```sql
CASE lsa.LifecycleStage
    WHEN 'New' THEN 'Developing'
    WHEN 'Developing' THEN 'Growing'
    WHEN 'Growing' THEN 'Mature'
    WHEN 'Mature' THEN 'Retain as Mature'
    WHEN 'At-Risk' THEN 'Reactivate to Growing'
    WHEN 'Churned' THEN 'Win Back to New'
    WHEN 'Inactive' THEN 'Activate to Developing'
END AS NextTargetStage
```

**Stage Progression Paths:**

- **New** → **Developing**: Natural progression, increase order frequency
- **Developing** → **Growing**: Expand engagement and basket size
- **Growing** → **Mature**: Solidify loyalty and habit
- **Mature** → **Retain as Mature**: Goal is retention, not advancement
- **At-Risk** → **Reactivate to Growing**: Recovery path skips back to active state
- **Churned** → **Win Back to New**: Full reactivation needed
- **Inactive** → **Activate to Developing**: Engagement boost required

**Business Purpose:** Provides clear, stage-specific goals for customer development strategies.

## Examples
- Customer in "New" → Target: "Developing" → Strategy: Encourage 3rd order
- Customer in "At-Risk" → Target: "Reactivate to Growing" → Strategy: Win-back campaign
- Customer in "Mature" → Target: "Retain as Mature" → Strategy: Loyalty rewards

---

# KPI 34: StageProgressionGap

## Definition
**StageProgressionGap** quantifies what's needed for a customer to advance to the next lifecycle stage, providing specific, actionable metrics.

**SQL Expression:**
```sql
CASE lsa.LifecycleStage
    WHEN 'New' THEN CONCAT(GREATEST(0, 3 - lsa.TotalOrders), ' more orders OR ', GREATEST(0, 91 - lsa.CustomerAgeDays), ' more days')
    WHEN 'Developing' THEN CONCAT(GREATEST(0, 5 - lsa.TotalOrders), ' more orders needed for Growing stage')
    WHEN 'Growing' THEN CONCAT(GREATEST(0, 11 - lsa.TotalOrders), ' more orders needed for Mature stage')
    WHEN 'At-Risk' THEN CONCAT('Purchase within ', GREATEST(0, 180 - lsa.DaysSinceLastPurchase), ' days to avoid churn')
    WHEN 'Churned' THEN 'Win-back campaign required'
    ELSE 'N/A'
END AS StageProgressionGap
```

**Gap Calculations by Stage:**

### New → Developing
**Gap:** $\max(0, 3 - \text{TotalOrders})$ orders OR $\max(0, 91 - \text{CustomerAgeDays})$ days

**Logic:** Need 3 orders or 91 days to graduate to Developing

**Examples:**
- Customer with 1 order, 30 days old → "2 more orders OR 61 more days"
- Customer with 2 orders, 85 days old → "1 more orders OR 6 more days"

### Developing → Growing
**Gap:** $\max(0, 5 - \text{TotalOrders})$ orders

**Logic:** Need 5 orders to reach Growing stage

**Examples:**
- Customer with 3 orders → "2 more orders needed for Growing stage"
- Customer with 4 orders → "1 more orders needed for Growing stage"

### Growing → Mature
**Gap:** $\max(0, 11 - \text{TotalOrders})$ orders

**Logic:** Need 11 orders (and be over 365 days old with recency < 180 days)

**Examples:**
- Customer with 7 orders → "4 more orders needed for Mature stage"
- Customer with 10 orders → "1 more orders needed for Mature stage"

### At-Risk (avoiding churn)
**Gap:** Purchase within $(180 - \text{DaysSinceLastPurchase})$ days

**Logic:** Must purchase before reaching 365 days of inactivity (churned threshold)

**Examples:**
- Customer at-risk for 200 days → "Purchase within -20 days to avoid churn" (already in danger zone)
- Customer at-risk for 220 days → "Purchase within -40 days to avoid churn" (critical)

**Note:** Negative values indicate already past safe threshold.

**Business Purpose:** Translates strategic goals into concrete, measurable actions. Enables personalized messaging (e.g., "Just 2 more orders to unlock Growing benefits!").

## Examples
- New customer with 1 order, 45 days → "2 more orders OR 46 more days"
- Developing customer with 3 orders → "2 more orders needed for Growing stage"
- At-Risk customer, 250 days inactive → "Purchase within -70 days..." (urgent!)

---

# KPI 35: RecommendedAction

## Definition
**RecommendedAction** provides specific, actionable marketing tactics for each customer based on their lifecycle stage.

**SQL Expression:**
```sql
CASE lsa.LifecycleStage
    WHEN 'New' THEN 'Onboarding campaign: Product education, repeat purchase incentive'
    WHEN 'Developing' THEN 'Engagement campaign: Cross-sell, loyalty program enrollment'
    WHEN 'Growing' THEN 'Expansion campaign: Premium tiers, volume discounts'
    WHEN 'Mature' THEN 'Retention campaign: VIP benefits, exclusive access'
    WHEN 'At-Risk' THEN 'URGENT: Re-engagement campaign, win-back offer'
    WHEN 'Churned' THEN 'Win-back campaign: Reactivation incentive'
    WHEN 'Inactive' THEN 'Activation campaign: Limited-time promotion'
END AS RecommendedAction
```

**Actions by Stage:**

### New
**Action:** "Onboarding campaign: Product education, repeat purchase incentive"

**Tactics:**
- Welcome email series
- How-to content and tutorials
- First-repeat-purchase discount (e.g., "20% off your next order")
- Product recommendation quiz
- Success stories from similar customers

**Goal:** Convert to second purchase within 30 days

### Developing
**Action:** "Engagement campaign: Cross-sell, loyalty program enrollment"

**Tactics:**
- Cross-category product recommendations
- Loyalty program invitation
- Bundle offers
- Educational content on product range
- "Complete your setup" campaigns

**Goal:** Increase order frequency and expand product usage

### Growing
**Action:** "Expansion campaign: Premium tiers, volume discounts"

**Tactics:**
- Premium product introductions
- Volume discount offers
- Subscription program enrollment
- Early access to new products
- Referral program with rewards

**Goal:** Accelerate path to Mature stage

### Mature
**Action:** "Retention campaign: VIP benefits, exclusive access"

**Tactics:**
- VIP tier with exclusive benefits
- Personal account manager
- Beta access to new features
- Exclusive events and experiences
- Co-creation opportunities

**Goal:** Maintain engagement and prevent movement to At-Risk

### At-Risk
**Action:** "URGENT: Re-engagement campaign, win-back offer"

**Tactics:**
- Personalized win-back emails
- Significant discount (30-50%)
- "We miss you" messaging
- Satisfaction survey to understand issues
- Phone outreach for high-value customers
- Time-limited urgency

**Goal:** Reactivate before becoming Churned

### Churned
**Action:** "Win-back campaign: Reactivation incentive"

**Tactics:**
- Deep reactivation discounts
- "What changed" messaging highlighting improvements
- Low-risk trial offers
- Limited investment (lower ROI expected)
- Product update announcements

**Goal:** Bring back to New stage

### Inactive
**Action:** "Activation campaign: Limited-time promotion"

**Tactics:**
- Flash sales
- Seasonal promotions
- New product launches
- Category-specific offers
- Low-cost touches (email only)

**Goal:** Stimulate engagement and move to Developing

**Business Purpose:** Translates lifecycle stage into operational marketing playbooks. Enables immediate action for campaign teams.

## Examples
- New customer → Receives automated onboarding series with 20% next purchase coupon
- At-Risk customer → Gets personal email from account manager with 40% win-back offer
- Mature customer → Invited to exclusive VIP event

---

# KPI 36: StageRevenueRank

## Definition
**StageRevenueRank** ranks customers within their lifecycle stage based on total revenue, with rank 1 being the highest value customer in that stage.

**SQL Expression:**
```sql
RANK() OVER (PARTITION BY lsa.LifecycleStage ORDER BY lsa.TotalRevenue DESC) AS StageRevenueRank
```

**Mathematical Formula:**
$$\text{StageRevenueRank}_s(c) = |\{c' \in s : \text{TotalRevenue}(c') > \text{TotalRevenue}(c)\}| + 1$$

for customer $c$ in stage $s$.

**Business Purpose:** Prioritizes within-stage actions. Identifies highest-value customers in At-Risk stage for immediate intervention.

## Examples
In At-Risk stage with 500 customers:
- Customer A: $50,000 revenue → StageRevenueRank = 1 (highest priority)
- Customer B: $35,000 revenue → StageRevenueRank = 5
- Customer C: $5,000 revenue → StageRevenueRank = 250 (medium priority)
- Customer D: $500 revenue → StageRevenueRank = 490 (low priority)

**Application:**
- At-Risk Stage Rank 1-10: Executive outreach, phone calls
- At-Risk Stage Rank 11-50: Personal emails with high discounts
- At-Risk Stage Rank 51+: Automated email campaigns

---

# KPI 37: InterventionPriority

## Definition
**InterventionPriority** assigns a priority level (High, Medium, Low, Stable) to each customer based on their lifecycle stage, guiding resource allocation and urgency.

**SQL Expression:**
```sql
CASE
    WHEN sto.LifecycleStage = 'At-Risk' THEN 'High'
    WHEN sto.LifecycleStage IN ('New', 'Developing') THEN 'Medium'
    WHEN sto.LifecycleStage = 'Churned' THEN 'Low'
    ELSE 'Stable'
END AS InterventionPriority
```

**Priority Levels:**

### High Priority
**Stage:** At-Risk

**Rationale:**
- High historical engagement (3+ orders)
- Active disengagement in progress
- Still reachable (haven't fully churned)
- High ROI on retention efforts
- Time-sensitive opportunity

**Resource Allocation:** Maximum attention, personal touches, aggressive offers

### Medium Priority
**Stages:** New, Developing

**Rationale:**
- Critical formation period
- High conversion potential
- Relatively low cost to influence
- Strategic importance for pipeline
- Scalable interventions

**Resource Allocation:** Systematic campaigns, moderate investment, automation with personalization

### Low Priority
**Stage:** Churned

**Rationale:**
- Already lost (> 1 year inactive)
- Low recovery probability
- High cost per reactivation
- Better ROI elsewhere
- Minimal touch strategy

**Resource Allocation:** Low-cost reactivation attempts, may exclude from paid campaigns

### Stable
**Stages:** Growing, Mature, Inactive

**Rationale:**
- Growing/Mature: Positive trajectory, routine nurturing sufficient
- Inactive: Mixed signals, watch-and-wait appropriate
- No immediate risk
- Maintenance mode

**Resource Allocation:** Standard nurture campaigns, monitoring, no urgent action

**Business Purpose:** Directs limited resources to customers where intervention has highest impact and urgency.

## Examples
- At-Risk customer with $50,000 lifetime value → High Priority → Assign account manager
- New customer → Medium Priority → Automated onboarding sequence
- Churned customer → Low Priority → Seasonal reactivation email only
- Mature customer → Stable → Regular loyalty rewards, no special intervention

---

# Summary: Lifecycle Stage Framework

## Query Structure
The query builds lifecycle analysis through five progressive CTEs:

### CTE Flow:
1. **CustomerPurchaseTimeline** → Transaction-level sequencing with window functions (KPI 1-6)
2. **CustomerCurrentState** → Customer-level aggregation (KPI 7-18)
3. **LifecycleStageAssignment** → Stage classification and enrichment (KPI 19-20)
4. **StageCharacteristics** → Aggregate stage statistics (KPI 21-32)
5. **StageTransitionOpportunities** → Progression analysis and recommendations (KPI 33-37)

## Lifecycle Stage Framework

### Core Stages:
1. **New** (0-90 days, 1-2 orders): Onboarding phase
2. **Developing** (91-180 days OR 2-4 orders): Building engagement
3. **Growing** (181-365 days OR 5-10 orders): Expanding usage
4. **Mature** (365+ days, 11+ orders, recent): Loyal core
5. **At-Risk** (180-365 days inactive, was engaged): Intervention needed
6. **Churned** (365+ days inactive): Recovery stage
7. **Inactive** (Fallback): Low engagement

### Progression Pathways:
**Positive Flow:** New → Developing → Growing → Mature → (Retained)

**Risk Flow:** Any stage → At-Risk → Churned

**Recovery Flow:** Churned → Win Back to New; At-Risk → Reactivate to Growing

## Business Applications

### 1. Pipeline Management
- **New Customer Conversion:** 60% of New should reach Developing within 90 days
- **Growth Trajectory:** Track progression rates through stages
- **Churn Prevention:** Identify customers approaching At-Risk threshold

### 2. Resource Allocation
- **High Priority (At-Risk):** Personal outreach, high-touch campaigns
- **Medium Priority (New/Developing):** Automated nurture with personalization
- **Low Priority (Churned):** Minimal investment
- **Stable (Growing/Mature):** Maintenance campaigns

### 3. Revenue Protection
- **At-Risk Revenue:** Calculate total revenue at risk
- **Intervention ROI:** At-Risk customers with $8K average justify $1K+ retention spend
- **Churn Impact:** Monitor revenue lost to Churned stage monthly

### 4. Growth Strategies
- **Accelerate New → Developing:** Onboarding optimization
- **Expand Mature Base:** Target 15-25% of customers in Mature stage
- **Reduce Time-to-Mature:** Shorten journey from New to Mature

### 5. Campaign Automation
- **Stage-Triggered Campaigns:** Automatic emails based on stage transitions
- **Progression Tracking:** "You're 2 orders away from VIP status!"
- **Urgency Messaging:** At-Risk customers get countdown timers

## Key Metrics for Executive Dashboard

### Stage Distribution Health:
- % New: 15-20% (acquisition rate)
- % Mature: 15-25% (loyalty base)
- % At-Risk: <10% (retention health)
- % Churned: <20% (churn control)

### Stage Progression Rates:
- New → Developing conversion: >60%
- Developing → Growing conversion: >50%
- Growing → Mature conversion: >40%
- At-Risk → Reactivated: >25%

### Revenue Concentration:
- Mature revenue share: 50-70% (value concentration)
- At-Risk revenue share: <15% (risk exposure)
- Growing revenue share: 20-30% (pipeline health)

### Intervention Effectiveness:
- At-Risk recovery rate (to Growing/Mature)
- Churned win-back rate (to New)
- Average progression time through stages

This lifecycle framework provides a complete, actionable customer development system that translates customer age and engagement into strategic interventions and clear progression goals.
