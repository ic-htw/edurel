# RFM Customer Segmentation Analysis - KPI Documentation

This document provides a comprehensive analysis of all Key Performance Indicators (KPIs) calculated in the RFM (Recency, Frequency, Monetary) customer segmentation SQL query. The query uses a multi-CTE approach to segment customers into actionable marketing groups with specific recommendations.

---

# KPI 1: FirstPurchaseDate

## Definition
**FirstPurchaseDate** represents the date of a customer's first purchase transaction. This marks the beginning of the customer relationship and is used for cohort analysis and customer age calculations.

**SQL Expression:**
```sql
MIN(fis.OrderDate) AS FirstPurchaseDate
```

**Mathematical Formula:**
$$\text{FirstPurchaseDate} = \min_{i}(\text{OrderDate}_i)$$

where $i$ ranges over all orders for the customer.

**Business Purpose:** Establishes the customer's entry point into the business ecosystem, enabling age-based analysis and cohort tracking.

## Examples
- Customer A: First purchase on 2019-01-15 (5-year customer if analyzed in 2024)
- Customer B: First purchase on 2023-11-20 (new customer, <2 years old)
- Customer C: First purchase on 2015-06-10 (veteran customer, 9+ years)

---

# KPI 2: LastPurchaseDate

## Definition
**LastPurchaseDate** represents the date of a customer's most recent purchase. This is the foundation for recency analysis in RFM segmentation.

**SQL Expression:**
```sql
MAX(fis.OrderDate) AS LastPurchaseDate
```

**Mathematical Formula:**
$$\text{LastPurchaseDate} = \max_{i}(\text{OrderDate}_i)$$

**Business Purpose:** Critical for determining customer activity status and identifying at-risk or churned customers.

## Examples
- Customer A: Last purchase 2024-12-15 (active, recent)
- Customer B: Last purchase 2023-06-20 (18 months ago, at risk)
- Customer C: Last purchase 2021-03-10 (dormant/churned)

---

# KPI 3: TotalOrders

## Definition
**TotalOrders** counts the number of distinct purchase orders a customer has placed. This is the foundation for the Frequency dimension in RFM analysis.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders
```

**Mathematical Formula:**
$$\text{TotalOrders} = |\{\text{SalesOrderNumber}_i : i \in \text{all transactions}\}|$$

where $|\cdot|$ denotes cardinality (count of unique values).

**Business Purpose:** Measures purchase frequency and customer engagement level. Higher values indicate more frequent purchasers.

## Examples
- Customer A: 50 orders → highly engaged, frequent buyer
- Customer B: 5 orders → moderate engagement
- Customer C: 1 order → one-time buyer, not yet loyal

---

# KPI 4: DaysSinceLastPurchase

## Definition
**DaysSinceLastPurchase** calculates the number of days from the customer's most recent purchase to the current date. This is the raw recency metric.

**SQL Expression:**
```sql
(CURRENT_DATE - MAX(fis.OrderDate)::DATE) AS DaysSinceLastPurchase
```

**Mathematical Formula:**
$$\text{DaysSinceLastPurchase} = \text{CURRENT\_DATE} - \text{LastPurchaseDate}$$

**Business Purpose:** Direct measure of customer recency, used to calculate RecencyScore and identify churn risk.

## Examples
- Customer A: 30 days since last purchase → active
- Customer B: 150 days since last purchase → at risk
- Customer C: 600 days since last purchase → likely churned

**Critical Thresholds (used in RecencyScore):**
- ≤60 days: Very active
- 61-120 days: Active
- 121-240 days: Declining
- 241-480 days: At risk
- >480 days: Churned

---

# KPI 5: CustomerTenureDays

## Definition
**CustomerTenureDays** measures the span of days between a customer's first and last purchase, representing the duration of their active relationship.

**SQL Expression:**
```sql
(MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays
```

**Mathematical Formula:**
$$\text{CustomerTenureDays} = \text{LastPurchaseDate} - \text{FirstPurchaseDate}$$

**Business Purpose:** Indicates the length of the customer relationship. Used to differentiate new customers from longstanding ones.

## Examples
- Customer A: First: 2020-01-01, Last: 2024-01-01 → 1461 days (4 years)
- Customer B: First: 2023-12-01, Last: 2024-01-01 → 31 days (new)
- Customer C: First: 2018-01-01, Last: 2024-01-01 → 2192 days (6 years)

**Note:** Single-purchase customers have 0 tenure days.

---

# KPI 6: TotalRevenue

## Definition
**TotalRevenue** sums all sales amounts across all customer purchases, representing their lifetime monetary contribution. This forms the Monetary dimension in RFM analysis.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount), 2) AS TotalRevenue
```

**Mathematical Formula:**
$$\text{TotalRevenue} = \sum_{i=1}^{n} \text{SalesAmount}_i$$

where $n$ is the total number of line items purchased.

**Business Purpose:** Primary monetary value metric for customer ranking. Used in MonetaryScore calculation.

## Examples
- Customer A: $100,000 total revenue → high-value customer
- Customer B: $5,000 total revenue → moderate-value customer
- Customer C: $200 total revenue → low-value customer

---

# KPI 7: TotalGrossProfit

## Definition
**TotalGrossProfit** calculates the cumulative gross profit (revenue minus product costs) generated by the customer, representing true margin contribution.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS TotalGrossProfit
```

**Mathematical Formula:**
$$\text{TotalGrossProfit} = \sum_{i=1}^{n} (\text{SalesAmount}_i - \text{TotalProductCost}_i)$$

**Business Purpose:** More accurate value assessment than revenue alone. Identifies customers who buy high-margin vs. low-margin products.

## Examples
- Customer A: $100,000 revenue, $40,000 profit → 40% margin
- Customer B: $50,000 revenue, $5,000 profit → 10% margin (low-margin buyer)
- Customer C: $20,000 revenue, $14,000 profit → 70% margin (high-margin buyer)

---

# KPI 8: AvgTransactionValue

## Definition
**AvgTransactionValue** calculates the average sales amount per line item across all customer purchases, indicating typical transaction size.

**SQL Expression:**
```sql
ROUND(AVG(fis.SalesAmount), 2) AS AvgTransactionValue
```

**Mathematical Formula:**
$$\text{AvgTransactionValue} = \frac{1}{n}\sum_{i=1}^{n} \text{SalesAmount}_i$$

where $n$ is the total number of line items.

**Business Purpose:** Indicates price point preference and basket size characteristics.

## Examples
- Customer A: Average $500 per transaction → premium buyer
- Customer B: Average $50 per transaction → value buyer
- Customer C: Average $25 per transaction → discount/small-item buyer

---

# KPI 9: RecencyScore

## Definition
**RecencyScore** assigns a 1-5 score based on how recently the customer made their last purchase, with 5 being most recent. This quantifies the "R" in RFM analysis.

**SQL Expression:**
```sql
CASE
    WHEN cph.DaysSinceLastPurchase <= 60 THEN 5
    WHEN cph.DaysSinceLastPurchase <= 120 THEN 4
    WHEN cph.DaysSinceLastPurchase <= 240 THEN 3
    WHEN cph.DaysSinceLastPurchase <= 480 THEN 2
    ELSE 1
END AS RecencyScore
```

**Mathematical Formula (Piecewise Function):**
$$\text{RecencyScore} = \begin{cases}
5 & \text{if } d \leq 60 \\
4 & \text{if } 60 < d \leq 120 \\
3 & \text{if } 120 < d \leq 240 \\
2 & \text{if } 240 < d \leq 480 \\
1 & \text{if } d > 480
\end{cases}$$

where $d = \text{DaysSinceLastPurchase}$.

**Range:** 1 to 5 (higher is better)

**Business Purpose:** Standardizes recency into a comparable score. Recency is the strongest predictor of future purchase behavior in RFM analysis.

## Examples
- Customer last purchased 45 days ago → RecencyScore = 5 (excellent)
- Customer last purchased 180 days ago → RecencyScore = 3 (moderate)
- Customer last purchased 600 days ago → RecencyScore = 1 (poor, likely churned)

**Interpretation:**
- **5**: Hot lead, very active
- **4**: Active, engaged
- **3**: Warm, needs nurturing
- **2**: At risk, requires attention
- **1**: Cold, churned or near-churned

---

# KPI 10: FrequencyScore

## Definition
**FrequencyScore** assigns customers to quintiles (1-5) based on total order count, with 5 representing the most frequent purchasers. This quantifies the "F" in RFM analysis.

**SQL Expression:**
```sql
NTILE(5) OVER (ORDER BY cph.TotalOrders ASC) AS FrequencyScore
```

**Mathematical Formula:**
$$\text{FrequencyScore} = \text{NTILE}_5(\text{TotalOrders}_{\text{asc}})$$

This divides customers into 5 equal-sized groups based on their TotalOrders rank (ascending order).

**Range:** 1 to 5 (higher is better)
- 5 = Top 20% (most frequent)
- 1 = Bottom 20% (least frequent)

**Business Purpose:** Standardizes purchase frequency into comparable quintiles, enabling cross-customer comparison regardless of absolute order counts.

## Examples
With 1,000 customers:
- **Score 5** (Rank 801-1000): Customers with most orders (e.g., 30+ orders)
- **Score 3** (Rank 401-600): Median frequency customers (e.g., 8-12 orders)
- **Score 1** (Rank 1-200): Customers with fewest orders (e.g., 1-3 orders)

**Note:** Using ASC ordering means higher order counts get higher scores.

---

# KPI 11: MonetaryScore

## Definition
**MonetaryScore** assigns customers to quintiles (1-5) based on total revenue, with 5 representing the highest-value customers. This quantifies the "M" in RFM analysis.

**SQL Expression:**
```sql
NTILE(5) OVER (ORDER BY cph.TotalRevenue ASC) AS MonetaryScore
```

**Mathematical Formula:**
$$\text{MonetaryScore} = \text{NTILE}_5(\text{TotalRevenue}_{\text{asc}})$$

**Range:** 1 to 5 (higher is better)
- 5 = Top 20% by revenue
- 1 = Bottom 20% by revenue

**Business Purpose:** Normalizes monetary value into comparable quintiles. Often reveals Pareto distribution (top 20% generate 60-80% of revenue).

## Examples
With $10M total revenue across 1,000 customers:
- **Score 5**: Top 200 customers, ~$7M revenue (~$35K average per customer)
- **Score 3**: Middle 200 customers, ~$1.5M revenue (~$7.5K average per customer)
- **Score 1**: Bottom 200 customers, ~$300K revenue (~$1.5K average per customer)

---

# KPI 12: RFMString

## Definition
**RFMString** concatenates the three RFM scores into a single 3-digit identifier (e.g., "555", "321") that uniquely identifies the customer's RFM profile.

**SQL Expression:**
```sql
CAST(rfm.RecencyScore AS TEXT) || CAST(rfm.FrequencyScore AS TEXT) || CAST(rfm.MonetaryScore AS TEXT) AS RFMString
```

**Mathematical Formula:**
$$\text{RFMString} = \text{concat}(R, F, M)$$

where $R, F, M \in \{1,2,3,4,5\}$.

**Range:** 111 to 555 (125 possible combinations)

**Business Purpose:** Provides a compact representation of customer profile for quick identification and segment grouping.

## Examples
- **"555"**: Best customers (recent, frequent, high-value) → Champions
- **"511"**: Recent and frequent but low spenders → Potential loyalists needing upsell
- **"111"**: Worst profile (old, infrequent, low-value) → Lost customers
- **"145"**: Not recent, infrequent, but high-value when they buy → Cannot lose them
- **"511"**: Very recent, infrequent, low value → New customers

**Pattern Analysis:**
- First digit = Recency (most predictive)
- Second digit = Frequency (loyalty indicator)
- Third digit = Monetary (value indicator)

---

# KPI 13: AvgRFMScore

## Definition
**AvgRFMScore** calculates the arithmetic mean of the three RFM scores, providing a single composite metric of overall customer quality.

**SQL Expression:**
```sql
ROUND((rfm.RecencyScore + rfm.FrequencyScore + rfm.MonetaryScore) / 3.0, 2) AS AvgRFMScore
```

**Mathematical Formula:**
$$\text{AvgRFMScore} = \frac{R + F + M}{3}$$

where $R, F, M \in \{1,2,3,4,5\}$.

**Range:** 1.00 to 5.00

**Business Purpose:** Simplifies customer comparison with a single metric. Useful for quick ranking when detailed segment analysis isn't needed.

## Examples
- Customer A: R=5, F=5, M=5 → AvgRFMScore = 5.00 (perfect)
- Customer B: R=4, F=4, M=3 → AvgRFMScore = 3.67 (good)
- Customer C: R=2, F=3, M=4 → AvgRFMScore = 3.00 (moderate, but not recent)
- Customer D: R=1, F=1, M=1 → AvgRFMScore = 1.00 (poor)

**Limitation:** Simple average treats all dimensions equally, but recency is typically most predictive. Segment-based classification (RFMSegment) is more nuanced.

---

# KPI 14: RFMSegment

## Definition
**RFMSegment** classifies customers into 11 strategic marketing segments based on their RFM score patterns. This is the core output of RFM analysis, translating scores into actionable business categories.

**SQL Expression:**
```sql
CASE
    WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 THEN 'Champions'
    WHEN rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 AND rfm.RecencyScore >= 3 THEN 'Loyal Customers'
    WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore >= 3 AND rfm.MonetaryScore >= 3 THEN 'Potential Loyalists'
    WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore <= 2 THEN 'New Customers'
    WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore <= 3 AND rfm.MonetaryScore <= 3 THEN 'Promising'
    WHEN rfm.RecencyScore = 3 AND rfm.FrequencyScore >= 3 AND rfm.MonetaryScore >= 3 THEN 'Need Attention'
    WHEN rfm.RecencyScore = 2 AND rfm.FrequencyScore >= 3 AND rfm.MonetaryScore >= 3 THEN 'About To Sleep'
    WHEN rfm.RecencyScore <= 2 AND rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 THEN 'At Risk'
    WHEN rfm.RecencyScore = 1 AND rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 THEN 'Cannot Lose Them'
    WHEN rfm.RecencyScore <= 2 AND rfm.FrequencyScore <= 3 AND rfm.MonetaryScore <= 3 THEN 'Hibernating'
    WHEN rfm.RecencyScore = 1 AND rfm.FrequencyScore <= 2 AND rfm.MonetaryScore <= 2 THEN 'Lost'
    ELSE 'Others'
END AS RFMSegment
```

**Segments Defined:**

### 1. Champions
**Criteria:** $R \geq 4$ AND $F \geq 4$ AND $M \geq 4$

**Profile:** Recent, frequent, high-value customers. Best customers.

**Example:** RFM "555", "544", "454"

### 2. Loyal Customers
**Criteria:** $F \geq 4$ AND $M \geq 4$ AND $R \geq 3$

**Profile:** Frequent and valuable, but slightly less recent than Champions.

**Example:** RFM "345", "354"

### 3. Potential Loyalists
**Criteria:** $R \geq 4$ AND $F \geq 3$ AND $M \geq 3$

**Profile:** Recent with moderate frequency and value, showing loyalty potential.

**Example:** RFM "433", "443", "434"

### 4. New Customers
**Criteria:** $R \geq 4$ AND $F \leq 2$

**Profile:** Recent purchasers but low frequency (new to the business).

**Example:** RFM "411", "512", "521"

### 5. Promising
**Criteria:** $R \geq 4$ AND $F \leq 3$ AND $M \leq 3$

**Profile:** Recent but with moderate-low frequency and value. Show promise.

**Example:** RFM "423", "431", "422"

### 6. Need Attention
**Criteria:** $R = 3$ AND $F \geq 3$ AND $M \geq 3$

**Profile:** Moderate recency with good frequency and value. Starting to decline.

**Example:** RFM "334", "343", "344"

### 7. About To Sleep
**Criteria:** $R = 2$ AND $F \geq 3$ AND $M \geq 3$

**Profile:** Declining recency but were previously active and valuable.

**Example:** RFM "234", "243", "244"

### 8. At Risk
**Criteria:** $R \leq 2$ AND $F \geq 4$ AND $M \geq 4$

**Profile:** Low recency but historically very frequent and valuable. High churn risk.

**Example:** RFM "145", "245", "154"

### 9. Cannot Lose Them
**Criteria:** $R = 1$ AND $F \geq 4$ AND $M \geq 4$

**Profile:** Worst recency but were champions. Critical recovery priority.

**Example:** RFM "145", "154", "155"

**Note:** Overlaps with "At Risk" but specifically the lowest recency (R=1).

### 10. Hibernating
**Criteria:** $R \leq 2$ AND $F \leq 3$ AND $M \leq 3$

**Profile:** Low recency, moderate-low frequency and value. Dormant.

**Example:** RFM "122", "223", "233"

### 11. Lost
**Criteria:** $R = 1$ AND $F \leq 2$ AND $M \leq 2$

**Profile:** Lowest scores across all dimensions. Effectively churned.

**Example:** RFM "111", "121", "112"

### 12. Others
**Fallback:** Any patterns not matching above criteria.

**Business Purpose:** Enables targeted marketing strategies by grouping customers with similar behavioral patterns and needs.

## Examples

**Customer A:** R=5, F=5, M=5 → "Champions"
- Action: Reward with VIP benefits

**Customer B:** R=4, F=2, M=3 → "New Customers"
- Action: Onboarding and welcome campaigns

**Customer C:** R=2, F=4, M=5 → "About To Sleep"
- Action: Win-back campaign urgently needed

**Customer D:** R=1, F=1, M=1 → "Lost"
- Action: Exclude from campaigns or minimal brand awareness only

---

# KPI 15: CustomerCount (by Segment)

## Definition
**CustomerCount** aggregates the number of customers within each RFM segment, showing segment size distribution.

**SQL Expression:**
```sql
COUNT(*) AS CustomerCount
```

**Mathematical Formula:**
$$\text{CustomerCount}_s = |\{c : \text{RFMSegment}(c) = s\}|$$

for each segment $s$.

**Business Purpose:** Reveals customer base composition. Identifies which segments are largest and may need specific attention.

## Examples
Example distribution across 10,000 customers:
- Champions: 500 customers (5%)
- Loyal Customers: 800 customers (8%)
- New Customers: 1,500 customers (15%)
- At Risk: 400 customers (4%)
- Lost: 1,200 customers (12%)
- Others: distributed across remaining segments

---

# KPI 16: SegmentPct

## Definition
**SegmentPct** calculates what percentage of the total customer base each segment represents, enabling proportional understanding of segment sizes.

**SQL Expression:**
```sql
ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM RFMSegmentation), 2) AS SegmentPct
```

**Mathematical Formula:**
$$\text{SegmentPct}_s = \frac{\text{CustomerCount}_s}{\sum_{s'} \text{CustomerCount}_{s'}} \times 100$$

**Range:** 0% to 100%, sum across all segments = 100%

**Business Purpose:** Provides relative segment sizing for resource allocation and benchmark comparison.

## Examples
- Champions: 5.2% (excellent if they drive >30% of revenue)
- Loyal Customers: 8.7%
- New Customers: 15.3% (healthy acquisition rate)
- At Risk: 4.1% (needs attention)
- Lost: 12.0% (consider reactivation economics)

**Industry Benchmarks:**
- Top-tier segments (Champions + Loyal): 10-20% is healthy
- New Customers: 15-25% indicates good acquisition
- At-Risk + Lost: <25% is ideal

---

# KPI 17: AvgRecencyScore (by Segment)

## Definition
**AvgRecencyScore** calculates the mean RecencyScore within each segment, validating that segment definitions align with recency patterns.

**SQL Expression:**
```sql
ROUND(AVG(rfms.RecencyScore), 2) AS AvgRecencyScore
```

**Mathematical Formula:**
$$\text{AvgRecencyScore}_s = \frac{1}{n_s}\sum_{c \in s} \text{RecencyScore}(c)$$

where $n_s$ is the number of customers in segment $s$.

**Business Purpose:** Quality check for segmentation logic. Verifies expected recency patterns within segments.

## Examples
Expected average recency by segment:
- Champions: 4.8 (should be very high)
- Loyal Customers: 4.2
- At Risk: 1.5 (should be low)
- Lost: 1.0 (should be lowest)
- Hibernating: 1.8

---

# KPI 18: AvgFrequencyScore (by Segment)

## Definition
**AvgFrequencyScore** calculates the mean FrequencyScore within each segment, validating frequency patterns align with segment definitions.

**SQL Expression:**
```sql
ROUND(AVG(rfms.FrequencyScore), 2) AS AvgFrequencyScore
```

**Mathematical Formula:**
$$\text{AvgFrequencyScore}_s = \frac{1}{n_s}\sum_{c \in s} \text{FrequencyScore}(c)$$

**Business Purpose:** Validates that segment classification correctly identifies frequency patterns.

## Examples
Expected average frequency by segment:
- Champions: 4.6 (high frequency)
- Loyal Customers: 4.5 (high frequency)
- New Customers: 1.5 (low frequency by definition)
- At Risk: 4.2 (high historical frequency)

---

# KPI 19: AvgMonetaryScore (by Segment)

## Definition
**AvgMonetaryScore** calculates the mean MonetaryScore within each segment, confirming monetary value patterns.

**SQL Expression:**
```sql
ROUND(AVG(rfms.MonetaryScore), 2) AS AvgMonetaryScore
```

**Mathematical Formula:**
$$\text{AvgMonetaryScore}_s = \frac{1}{n_s}\sum_{c \in s} \text{MonetaryScore}(c)$$

**Business Purpose:** Validates segment value characteristics and helps prioritize high-value segments.

## Examples
Expected average monetary score by segment:
- Champions: 4.7 (high value)
- Cannot Lose Them: 4.8 (historically very high value)
- New Customers: 2.8 (mixed, too early to tell)
- Lost: 1.3 (low value)

---

# KPI 20: AvgDaysSinceLastPurchase (by Segment)

## Definition
**AvgDaysSinceLastPurchase** calculates the mean days since last purchase for customers in each segment, providing concrete recency metrics in days.

**SQL Expression:**
```sql
ROUND(AVG(rfms.DaysSinceLastPurchase), 0) AS AvgDaysSinceLastPurchase
```

**Mathematical Formula:**
$$\text{AvgDaysSinceLastPurchase}_s = \frac{1}{n_s}\sum_{c \in s} \text{DaysSinceLastPurchase}(c)$$

**Business Purpose:** Translates RecencyScore back into actionable time metrics. Helps set campaign timing.

## Examples
Expected averages by segment:
- Champions: 35 days (very recent)
- Loyal Customers: 55 days (recent)
- At Risk: 400 days (over 1 year)
- Lost: 700 days (nearly 2 years)
- Hibernating: 450 days

**Application:** If "At Risk" averages 400 days, campaigns should trigger at 300-350 days to prevent reaching this stage.

---

# KPI 21: AvgTotalOrders (by Segment)

## Definition
**AvgTotalOrders** calculates the mean number of lifetime orders for customers in each segment.

**SQL Expression:**
```sql
ROUND(AVG(rfms.TotalOrders), 2) AS AvgTotalOrders
```

**Mathematical Formula:**
$$\text{AvgTotalOrders}_s = \frac{1}{n_s}\sum_{c \in s} \text{TotalOrders}(c)$$

**Business Purpose:** Reveals typical engagement levels within segments. Validates frequency-based segment definitions.

## Examples
Expected averages by segment:
- Champions: 45 orders (highly engaged)
- Loyal Customers: 38 orders (very engaged)
- New Customers: 2 orders (just starting)
- At Risk: 30 orders (were previously engaged)
- Lost: 3 orders (never engaged deeply)

---

# KPI 22: AvgLifetimeRevenue (by Segment)

## Definition
**AvgLifetimeRevenue** calculates the mean total revenue per customer within each segment.

**SQL Expression:**
```sql
ROUND(AVG(rfms.TotalRevenue), 2) AS AvgLifetimeRevenue
```

**Mathematical Formula:**
$$\text{AvgLifetimeRevenue}_s = \frac{1}{n_s}\sum_{c \in s} \text{TotalRevenue}(c)$$

**Business Purpose:** Quantifies average customer value by segment, informing marketing investment levels and prioritization.

## Examples
Expected averages by segment (hypothetical retail business):
- Champions: $25,000 average (highest value)
- Cannot Lose Them: $28,000 average (historically very valuable)
- Loyal Customers: $18,000 average
- New Customers: $800 average (too early)
- Lost: $500 average (never engaged)

**ROI Calculation:** If recovering one "Cannot Lose Them" customer costs $500 in marketing but they average $28K lifetime, ROI is 56x.

---

# KPI 23: AvgLifetimeProfit (by Segment)

## Definition
**AvgLifetimeProfit** calculates the mean gross profit per customer within each segment, providing a margin-adjusted value metric.

**SQL Expression:**
```sql
ROUND(AVG(rfms.TotalGrossProfit), 2) AS AvgLifetimeProfit
```

**Mathematical Formula:**
$$\text{AvgLifetimeProfit}_s = \frac{1}{n_s}\sum_{c \in s} \text{TotalGrossProfit}(c)$$

**Business Purpose:** More accurate than revenue for investment decisions, as it accounts for cost structure and product mix differences.

## Examples
Expected averages by segment:
- Champions: $10,000 average profit (40% margin on $25K revenue)
- New Customers: $300 average profit (37.5% margin on $800 revenue)
- At Risk: $6,000 average profit (demonstrates value worth saving)

**Application:** If "At Risk" customers average $6K profit, spending up to $1K per customer on retention has strong ROI.

---

# KPI 24: TotalSegmentRevenue

## Definition
**TotalSegmentRevenue** sums the total revenue generated by all customers within a segment, showing absolute segment contribution.

**SQL Expression:**
```sql
ROUND(SUM(rfms.TotalRevenue), 2) AS TotalSegmentRevenue
```

**Mathematical Formula:**
$$\text{TotalSegmentRevenue}_s = \sum_{c \in s} \text{TotalRevenue}(c)$$

**Business Purpose:** Identifies which segments drive total business revenue, often revealing Pareto distributions.

## Examples
With $50M total revenue across segments:
- Champions (5% of customers): $20M revenue (40%)
- Loyal Customers (8% of customers): $12M revenue (24%)
- At Risk (4% of customers): $8M revenue (16%)
- Lost (12% of customers): $1M revenue (2%)

**Insight:** Top 13% of customers (Champions + Loyal) drive 64% of revenue - classic Pareto.

---

# KPI 25: RevenueSharePct (by Segment)

## Definition
**RevenueSharePct** calculates what percentage of total company revenue each segment generates, enabling proportional value assessment.

**SQL Expression:**
```sql
ROUND(100.0 * SUM(rfms.TotalRevenue) / (SELECT SUM(TotalRevenue) FROM RFMSegmentation), 2) AS RevenueSharePct
```

**Mathematical Formula:**
$$\text{RevenueSharePct}_s = \frac{\text{TotalSegmentRevenue}_s}{\sum_{s'} \text{TotalSegmentRevenue}_{s'}} \times 100$$

**Range:** 0% to 100%, sum across all segments = 100%

**Business Purpose:** Reveals disproportionate value concentration. Guides resource allocation and risk assessment.

## Examples
Typical distribution:
- Champions: 35% of revenue (5% of customers) → 7x concentration
- Loyal Customers: 25% of revenue (8% of customers) → 3.1x concentration
- New Customers: 5% of revenue (15% of customers) → 0.33x concentration
- At Risk: 15% of revenue (4% of customers) → 3.75x concentration (high value at risk!)
- Lost: 2% of revenue (12% of customers) → 0.17x concentration

**Strategic Insight:** "At Risk" segment with 15% revenue share from 4% of customers represents major risk if they churn.

---

# KPI 26: AvgYearlyIncome (by Segment)

## Definition
**AvgYearlyIncome** calculates the mean annual income of customers within each segment, revealing demographic-economic patterns.

**SQL Expression:**
```sql
ROUND(AVG(rfms.YearlyIncome), 2) AS AvgYearlyIncome
```

**Mathematical Formula:**
$$\text{AvgYearlyIncome}_s = \frac{1}{n_s}\sum_{c \in s} \text{YearlyIncome}(c)$$

**Business Purpose:** Links RFM behavior to economic capacity. Helps tailor messaging and product recommendations by segment income levels.

## Examples
Expected patterns:
- Champions: $85,000 average income (affluent)
- Loyal Customers: $72,000 average income
- New Customers: $65,000 average income (mixed demographic)
- Lost: $48,000 average income (may indicate product-market fit issues)

**Insight:** If "Champions" have significantly higher income, consider whether lower-income segments are being adequately served with appropriate product lines.

---

# KPI 27: MinLifetimeRevenue & MaxLifetimeRevenue (by Segment)

## Definition
**MinLifetimeRevenue** and **MaxLifetimeRevenue** show the range of customer values within each segment, revealing segment heterogeneity.

**SQL Expression:**
```sql
MIN(rfms.TotalRevenue) AS MinLifetimeRevenue,
MAX(rfms.TotalRevenue) AS MaxLifetimeRevenue
```

**Mathematical Formula:**
$$\text{MinLifetimeRevenue}_s = \min_{c \in s}(\text{TotalRevenue}(c))$$
$$\text{MaxLifetimeRevenue}_s = \max_{c \in s}(\text{TotalRevenue}(c))$$

**Business Purpose:** Identifies segments with high internal variance, suggesting potential for further sub-segmentation.

## Examples
Champions segment range:
- Min: $15,000
- Max: $250,000
- Range: $235,000 (high variance suggests sub-segments)

New Customers segment range:
- Min: $50
- Max: $5,000
- Range: $4,950 (indicates diverse entry points)

**Action:** High-variance segments may benefit from additional stratification (e.g., "Champions - Tier 1" for >$100K customers).

---

# KPI 28: MarketingAction

## Definition
**MarketingAction** provides specific, actionable marketing recommendations for each customer based on their RFM segment, translating analytical segments into operational tactics.

**SQL Expression:**
```sql
CASE
    WHEN rfms.RFMSegment = 'Champions' THEN 'Reward with VIP benefits, early access, exclusive offers'
    WHEN rfms.RFMSegment = 'Loyal Customers' THEN 'Upsell premium products, loyalty program, referral incentives'
    WHEN rfms.RFMSegment = 'Potential Loyalists' THEN 'Nurture with membership offers, personalized recommendations'
    WHEN rfms.RFMSegment = 'New Customers' THEN 'Onboarding campaigns, product education, welcome discounts'
    WHEN rfms.RFMSegment = 'Promising' THEN 'Cross-sell campaigns, bundle offers, engagement emails'
    WHEN rfms.RFMSegment = 'Need Attention' THEN 'Re-engagement campaigns, limited-time offers, feedback surveys'
    WHEN rfms.RFMSegment = 'About To Sleep' THEN 'Win-back campaigns, personalized discounts, reminder emails'
    WHEN rfms.RFMSegment = 'At Risk' THEN 'Urgent win-back offers, satisfaction surveys, retention discounts'
    WHEN rfms.RFMSegment = 'Cannot Lose Them' THEN 'HIGH PRIORITY: Executive outreach, special recovery offers'
    WHEN rfms.RFMSegment = 'Hibernating' THEN 'Low-cost reactivation, seasonal promotions, product updates'
    WHEN rfms.RFMSegment = 'Lost' THEN 'Minimal investment, brand awareness only, or exclude from campaigns'
    ELSE 'Standard marketing communications'
END AS MarketingAction
```

**Recommended Actions by Segment:**

### Champions
**Action:** Reward with VIP benefits, early access, exclusive offers

**Rationale:** Already best customers, focus on retention and deepening relationship

**Tactics:** VIP events, exclusive product previews, concierge service, brand ambassador programs

### Loyal Customers
**Action:** Upsell premium products, loyalty program, referral incentives

**Rationale:** Strong relationship established, ready for premium offerings and advocacy

**Tactics:** Premium tier upgrades, refer-a-friend bonuses, co-creation opportunities

### Potential Loyalists
**Action:** Nurture with membership offers, personalized recommendations

**Rationale:** Showing loyalty signals, need encouragement to become fully loyal

**Tactics:** Personalized product recommendations, membership benefits preview, engagement content

### New Customers
**Action:** Onboarding campaigns, product education, welcome discounts

**Rationale:** Early in journey, need education and positive reinforcement

**Tactics:** Welcome series, how-to content, first-purchase discount, satisfaction checks

### Promising
**Action:** Cross-sell campaigns, bundle offers, engagement emails

**Rationale:** Recent but light engagement, expand basket and frequency

**Tactics:** Bundle promotions, category exploration emails, use case content

### Need Attention
**Action:** Re-engagement campaigns, limited-time offers, feedback surveys

**Rationale:** Declining activity, need intervention before they slip further

**Tactics:** "We miss you" emails, special reactivation discounts, feedback requests

### About To Sleep
**Action:** Win-back campaigns, personalized discounts, reminder emails

**Rationale:** At critical inflection point, aggressive intervention needed

**Tactics:** Personalized win-back offers, cart abandonment reminders, lifecycle emails

### At Risk
**Action:** Urgent win-back offers, satisfaction surveys, retention discounts

**Rationale:** High-value customers at serious churn risk, justify high investment

**Tactics:** Deep discounts, executive outreach, satisfaction investigations, service recovery

### Cannot Lose Them
**Action:** HIGH PRIORITY: Executive outreach, special recovery offers

**Rationale:** Were champions, now lost - highest priority recovery given historical value

**Tactics:** Executive calls, special recovery packages, account review meetings, loyalty restoration plans

### Hibernating
**Action:** Low-cost reactivation, seasonal promotions, product updates

**Rationale:** Low historical value, limit investment but maintain presence

**Tactics:** Seasonal campaigns, new product announcements, low-cost email touches

### Lost
**Action:** Minimal investment, brand awareness only, or exclude from campaigns

**Rationale:** Low probability of recovery, avoid wasting resources

**Tactics:** Passive brand awareness, exclude from paid campaigns, suppression lists

## Examples
- Customer in "Champions" → Receives invitation to exclusive VIP event
- Customer in "At Risk" → Receives personal call from account manager with 30% discount
- Customer in "New Customers" → Receives automated welcome series with tutorials
- Customer in "Lost" → Excluded from email campaigns, reducing costs

---

# KPI 29: MarketingPriority

## Definition
**MarketingPriority** assigns a priority level (High, Medium, Moderate, Low) to each customer based on their segment, guiding resource allocation and attention levels.

**SQL Expression:**
```sql
CASE
    WHEN rfms.RFMSegment IN ('Champions', 'Loyal Customers', 'Cannot Lose Them') THEN 'High Priority'
    WHEN rfms.RFMSegment IN ('Potential Loyalists', 'At Risk', 'Need Attention') THEN 'Medium Priority'
    WHEN rfms.RFMSegment IN ('New Customers', 'Promising', 'About To Sleep') THEN 'Moderate Priority'
    ELSE 'Low Priority'
END AS MarketingPriority
```

**Priority Definitions:**

### High Priority
**Segments:** Champions, Loyal Customers, Cannot Lose Them

**Rationale:** Highest current or historical value, deserve maximum attention

**Resource Allocation:** Premium service, personal touches, high marketing spend justified

**Metrics:** Typically 10-20% of customers, 50-70% of revenue

### Medium Priority
**Segments:** Potential Loyalists, At Risk, Need Attention

**Rationale:** Growth potential or retention risk, strategic importance

**Resource Allocation:** Targeted campaigns, moderate investment, systematic monitoring

**Metrics:** Typically 20-30% of customers, 20-30% of revenue

### Moderate Priority
**Segments:** New Customers, Promising, About To Sleep

**Rationale:** Unknown potential or moderate value, deserve standard attention

**Resource Allocation:** Automated campaigns, standard service, selective investment

**Metrics:** Typically 25-35% of customers, 10-20% of revenue

### Low Priority
**Segments:** Hibernating, Lost, Others

**Rationale:** Low value or recovery probability, minimize investment

**Resource Allocation:** Passive communications, low-cost touches, suppression consideration

**Metrics:** Typically 30-40% of customers, 5-10% of revenue

## Examples
- "Champions" → High Priority → Personal account manager assigned
- "At Risk" → Medium Priority → Automated risk alerts trigger retention workflows
- "New Customers" → Moderate Priority → Standard onboarding automation
- "Lost" → Low Priority → Removed from paid campaigns

---

# KPI 30: ExpectedROI

## Definition
**ExpectedROI** categorizes the expected return on marketing investment for each customer based on their segment characteristics, guiding budget allocation decisions.

**SQL Expression:**
```sql
CASE
    WHEN rfms.RFMSegment IN ('Champions', 'Loyal Customers', 'Potential Loyalists') THEN 'High ROI Expected'
    WHEN rfms.RFMSegment IN ('New Customers', 'Promising', 'At Risk', 'Cannot Lose Them') THEN 'Medium ROI Expected'
    ELSE 'Low ROI Expected'
END AS ExpectedROI
```

**ROI Categories:**

### High ROI Expected
**Segments:** Champions, Loyal Customers, Potential Loyalists

**Rationale:**
- Already engaged and responsive
- High conversion rates on campaigns
- Strong lifetime value trajectory
- Low acquisition cost (already customers)

**Investment Strategy:** Justify premium spend, maximize share-of-wallet

**Expected Campaign ROI:** 5:1 to 20:1

### Medium ROI Expected
**Segments:** New Customers, Promising, At Risk, Cannot Lose Them

**Rationale:**
- Uncertain outcomes (New/Promising: untested; At Risk/Cannot Lose: recovery uncertain)
- Moderate success rates
- Strategic importance justifies investment
- Mixed cost-benefit

**Investment Strategy:** Targeted investment with clear metrics

**Expected Campaign ROI:** 2:1 to 5:1

### Low ROI Expected
**Segments:** Hibernating, Lost, About To Sleep, Need Attention, Others

**Rationale:**
- Low historical value or engagement
- Low response rates
- High cost relative to expected return
- Better opportunities elsewhere

**Investment Strategy:** Minimize spend, focus on high-efficiency channels

**Expected Campaign ROI:** 0.5:1 to 2:1 (often negative)

## Examples

**High ROI Scenario:**
- Segment: Champions
- Campaign Cost: $50 per customer
- Expected Response Rate: 40%
- Expected Revenue per Responder: $500
- ROI: ($500 × 0.40) / $50 = 4:1 or 400% ROI

**Medium ROI Scenario:**
- Segment: At Risk
- Campaign Cost: $100 per customer
- Expected Response Rate: 15%
- Expected Revenue per Responder: $2,000
- ROI: ($2,000 × 0.15) / $100 = 3:1 or 300% ROI

**Low ROI Scenario:**
- Segment: Lost
- Campaign Cost: $25 per customer
- Expected Response Rate: 2%
- Expected Revenue per Responder: $200
- ROI: ($200 × 0.02) / $25 = 0.16:1 or -84% (loss)

---

# Summary: RFM Analysis Framework

## Query Structure
The query builds customer segmentation through five progressive CTEs:

### CTE Flow:
1. **CustomerPurchaseHistory** → Basic metrics (KPI 1-8)
2. **RFMScores** → Adds customer attributes and RFM scores (KPI 9-11)
3. **RFMSegmentation** → Creates segments and composite metrics (KPI 12-14)
4. **SegmentCharacteristics** → Aggregate segment statistics (KPI 15-27)
5. **MarketingRecommendations** → Operational recommendations (KPI 28-30)

## RFM Methodology

### Core Dimensions:
1. **Recency (R):** How recently did the customer purchase?
   - Most predictive of future behavior
   - Scored 1-5 based on days since last purchase

2. **Frequency (F):** How often do they purchase?
   - Indicates loyalty and engagement
   - Scored 1-5 via quintile ranking

3. **Monetary (M):** How much do they spend?
   - Indicates customer value
   - Scored 1-5 via quintile ranking

### Segmentation Logic:
Combines RFM scores into 11 strategic segments:
- **Active/Valuable:** Champions, Loyal Customers, Potential Loyalists
- **New/Developing:** New Customers, Promising
- **Declining:** Need Attention, About To Sleep
- **At-Risk:** At Risk, Cannot Lose Them
- **Inactive:** Hibernating, Lost

## Business Applications

### 1. Marketing Campaign Targeting
- **Champions:** VIP rewards, exclusive access
- **At Risk:** Aggressive retention offers
- **New Customers:** Onboarding and education
- **Lost:** Exclude from campaigns

### 2. Resource Allocation
- **High Priority (High/Cannot Lose/Loyal):** Premium service, personal touches
- **Medium Priority (Potential/At Risk/Need Attention):** Targeted campaigns
- **Low Priority (Hibernating/Lost):** Minimal investment

### 3. Revenue Protection
- **Identify At-Risk Segments:** 15% of revenue from 4% of customers
- **Proactive Intervention:** Before they reach "Cannot Lose" stage
- **Recovery Economics:** Calculate max spend based on historical value

### 4. Growth Strategies
- **Convert New → Loyal:** Onboarding sequences
- **Upgrade Potential → Loyal:** Personalized nurturing
- **Expand Champions:** Upsell and cross-sell premium offerings

### 5. Efficiency Optimization
- **Expected ROI Tiers:** Guide budget allocation
- **Segment-Specific Channels:** Email for low-cost segments, personal outreach for high-value
- **Suppression Lists:** Exclude "Lost" from paid campaigns

## Key Metrics for Executive Dashboard

### Customer Health Metrics:
- % in Champions + Loyal (target: 12-20%)
- % in At-Risk + Cannot Lose (red flag if >10%)
- % in New Customers (acquisition indicator: 15-25%)

### Revenue Concentration:
- Top 2 segments revenue share (should be 50-65%)
- At-Risk segment revenue (risk indicator)
- Revenue per segment vs. customer count (efficiency)

### Engagement Indicators:
- Avg days since last purchase by segment
- Segment migration patterns (Champions → At Risk is critical alert)
- New customer conversion rate to Loyal

This RFM framework provides a complete, actionable customer segmentation system that translates analytical scores into strategic business decisions and tactical marketing actions.
