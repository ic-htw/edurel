-- ETL Script: OLTP (AdventureWorks) to OLAP (Data Warehouse) Transformation
-- Source: AdventureWorks OLTP Database
-- Target: Star/Snowflake Schema Data Warehouse

-- ============================================================================
-- DIMENSION TABLES ETL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- DimCurrency: Currency dimension
-- Source: Currency table
-- ----------------------------------------------------------------------------
INSERT INTO DimCurrency (CurrencyKey, CurrencyName)
SELECT
    ROW_NUMBER() OVER (ORDER BY CurrencyCode) AS CurrencyKey,
    Name AS CurrencyName
FROM Currency;

-- ----------------------------------------------------------------------------
-- DimProductCategory: Product category dimension
-- Source: ProductCategory table
-- ----------------------------------------------------------------------------
INSERT INTO DimProductCategory (ProductCategoryKey, EnglishProductCategoryName)
SELECT
    ProductCategoryID AS ProductCategoryKey,
    Name AS EnglishProductCategoryName
FROM ProductCategory;

-- ----------------------------------------------------------------------------
-- DimProductSubcategory: Product subcategory dimension
-- Source: ProductSubcategory table
-- ----------------------------------------------------------------------------
INSERT INTO DimProductSubcategory (
    ProductSubcategoryKey,
    EnglishProductSubcategoryName,
    ProductCategoryKey
)
SELECT
    ProductSubcategoryID AS ProductSubcategoryKey,
    Name AS EnglishProductSubcategoryName,
    ProductCategoryID AS ProductCategoryKey
FROM ProductSubcategory;

-- ----------------------------------------------------------------------------
-- DimProduct: Product dimension
-- Source: Product table
-- ----------------------------------------------------------------------------
INSERT INTO DimProduct (ProductKey, ProductSubcategoryKey, EnglishProductName)
SELECT
    ProductID AS ProductKey,
    ProductSubcategoryID AS ProductSubcategoryKey,
    Name AS EnglishProductName
FROM Product
WHERE ProductSubcategoryID IS NOT NULL;

-- ----------------------------------------------------------------------------
-- DimGeography: Geography dimension
-- Source: Address, StateProvince, CountryRegion tables
-- Creates unique geography combinations
-- ----------------------------------------------------------------------------
INSERT INTO DimGeography (
    GeographyKey,
    City,
    StateProvinceCode,
    StateProvinceName,
    CountryRegionCode,
    EnglishCountryRegionName,
    PostalCode
)
SELECT DISTINCT
    ROW_NUMBER() OVER (
        ORDER BY a.City, sp.StateProvinceCode, cr.CountryRegionCode, a.PostalCode
    ) AS GeographyKey,
    a.City,
    sp.StateProvinceCode,
    sp.Name AS StateProvinceName,
    cr.CountryRegionCode,
    cr.Name AS EnglishCountryRegionName,
    a.PostalCode
FROM Address a
LEFT JOIN StateProvince sp ON a.StateProvinceID = sp.StateProvinceID
LEFT JOIN CountryRegion cr ON sp.CountryRegionCode = cr.CountryRegionCode;

-- ----------------------------------------------------------------------------
-- DimCustomer: Customer dimension
-- Source: Customer, Person tables
-- Note: Many demographic fields are placeholders as source doesn't contain them
-- ----------------------------------------------------------------------------
INSERT INTO DimCustomer (
    CustomerKey,
    GeographyKey,
    FirstName,
    LastName,
    BirthDate,
    MaritalStatus,
    Gender,
    YearlyIncome,
    TotalChildren,
    NumberChildrenAtHome,
    EnglishEducation,
    EnglishOccupation,
    HouseOwnerFlag,
    NumberCarsOwned
)
SELECT
    c.CustomerID AS CustomerKey,
    (
        SELECT g.GeographyKey
        FROM DimGeography g
        INNER JOIN Address a ON
            g.City = a.City
            AND g.PostalCode = a.PostalCode
        INNER JOIN BusinessEntityAddress bea ON a.AddressID = bea.AddressID
        WHERE bea.BusinessEntityID = p.BusinessEntityID
        LIMIT 1
    ) AS GeographyKey,
    p.FirstName,
    p.LastName,
    NULL AS BirthDate,  -- Not available in source
    NULL AS MaritalStatus,  -- Not available for customers
    NULL AS Gender,  -- Not available for customers
    NULL AS YearlyIncome,  -- Not available in source
    NULL AS TotalChildren,  -- Not available in source
    NULL AS NumberChildrenAtHome,  -- Not available in source
    NULL AS EnglishEducation,  -- Not available in source
    NULL AS EnglishOccupation,  -- Not available in source
    NULL AS HouseOwnerFlag,  -- Not available in source
    NULL AS NumberCarsOwned  -- Not available in source
FROM Customer c
LEFT JOIN Person p ON c.PersonID = p.BusinessEntityID;

-- ----------------------------------------------------------------------------
-- DimPromotion: Promotion/Special offer dimension
-- Source: SpecialOffer table
-- ----------------------------------------------------------------------------
INSERT INTO DimPromotion (
    PromotionKey,
    EnglishPromotionName,
    DiscountPct,
    EnglishPromotionType,
    EnglishPromotionCategory,
    StartDate,
    EndDate,
    MinQty,
    MaxQty
)
SELECT
    SpecialOfferID AS PromotionKey,
    Description AS EnglishPromotionName,
    DiscountPct,
    Type AS EnglishPromotionType,
    Category AS EnglishPromotionCategory,
    StartDate,
    EndDate,
    MinQty,
    MaxQty
FROM SpecialOffer;

-- ----------------------------------------------------------------------------
-- DimDate: Date dimension
-- Generate dates for a reasonable range (e.g., 2000-2030)
-- This is a common date dimension with calendar attributes
-- ----------------------------------------------------------------------------
INSERT INTO DimDate (
    DateKey,
    DayNumberOfWeek,
    EnglishDayNameOfWeek,
    DayNumberOfMonth,
    DayNumberOfYear,
    WeekNumberOfYear,
    EnglishMonthName,
    MonthNumberOfYear,
    CalendarQuarter,
    CalendarYear,
    CalendarSemester
)
WITH RECURSIVE date_range AS (
    SELECT DATE '2000-01-01' AS date_value
    UNION ALL
    SELECT date_value + INTERVAL '1 day'
    FROM date_range
    WHERE date_value < DATE '2030-12-31'
)
SELECT
    CAST(STRFTIME(date_value, '%Y%m%d') AS INTEGER) AS DateKey,
    EXTRACT(ISODOW FROM date_value) AS DayNumberOfWeek,
    DAYNAME(date_value) AS EnglishDayNameOfWeek,
    EXTRACT(DAY FROM date_value) AS DayNumberOfMonth,
    EXTRACT(DOY FROM date_value) AS DayNumberOfYear,
    EXTRACT(WEEK FROM date_value) AS WeekNumberOfYear,
    MONTHNAME(date_value) AS EnglishMonthName,
    EXTRACT(MONTH FROM date_value) AS MonthNumberOfYear,
    EXTRACT(QUARTER FROM date_value) AS CalendarQuarter,
    EXTRACT(YEAR FROM date_value) AS CalendarYear,
    CASE
        WHEN EXTRACT(MONTH FROM date_value) <= 6 THEN 1
        ELSE 2
    END AS CalendarSemester
FROM date_range;

-- ----------------------------------------------------------------------------
-- DimDepartmentGroup: Department group dimension
-- Source: Department table (GroupName)
-- Creates unique department groups
-- ----------------------------------------------------------------------------
INSERT INTO DimDepartmentGroup (DepartmentGroupKey, DepartmentGroupName)
SELECT DISTINCT
    ROW_NUMBER() OVER (ORDER BY GroupName) AS DepartmentGroupKey,
    GroupName AS DepartmentGroupName
FROM Department;

-- ----------------------------------------------------------------------------
-- DimAccount: Account dimension
-- Note: No direct source in OLTP, creating placeholder entries
-- In a real scenario, this would come from a chart of accounts
-- ----------------------------------------------------------------------------
INSERT INTO DimAccount (AccountKey, AccountDescription, AccountType)
VALUES
    (1, 'Revenue', 'Income'),
    (2, 'Cost of Goods Sold', 'Expense'),
    (3, 'Operating Expenses', 'Expense'),
    (4, 'Assets', 'Balance Sheet'),
    (5, 'Liabilities', 'Balance Sheet'),
    (6, 'Equity', 'Balance Sheet');

-- ----------------------------------------------------------------------------
-- DimOrganization: Organization dimension
-- Note: No direct source in OLTP, creating placeholder entries
-- In a real scenario, this would come from organizational hierarchy
-- ----------------------------------------------------------------------------
INSERT INTO DimOrganization (OrganizationKey, OrganizationName, CurrencyKey)
VALUES
    (1, 'Adventure Works Headquarters', 1),
    (2, 'North America Division', 1),
    (3, 'Europe Division', 1),
    (4, 'Asia Pacific Division', 1);

-- ----------------------------------------------------------------------------
-- DimScenario: Scenario dimension (for financial planning)
-- Note: No direct source in OLTP, creating standard entries
-- ----------------------------------------------------------------------------
INSERT INTO DimScenario (ScenarioKey, ScenarioName)
VALUES
    (1, 'Actual'),
    (2, 'Budget'),
    (3, 'Forecast');

-- ============================================================================
-- FACT TABLES ETL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- FactInternetSales: Internet sales fact table
-- Source: SalesOrderHeader and SalesOrderDetail tables
-- Only includes online orders (OnlineOrderFlag = 1)
-- ----------------------------------------------------------------------------
INSERT INTO FactInternetSales (
    ProductKey,
    OrderDateKey,
    DueDateKey,
    ShipDateKey,
    CustomerKey,
    PromotionKey,
    CurrencyKey,
    SalesOrderNumber,
    SalesOrderLineNumber,
    OrderQuantity,
    UnitPrice,
    SalesAmount
)
SELECT
    sod.ProductID AS ProductKey,
    CAST(STRFTIME(soh.OrderDate, '%Y%m%d') AS INTEGER) AS OrderDateKey,
    CAST(STRFTIME(soh.DueDate, '%Y%m%d') AS INTEGER) AS DueDateKey,
    CAST(STRFTIME(soh.ShipDate, '%Y%m%d') AS INTEGER) AS ShipDateKey,
    soh.CustomerID AS CustomerKey,
    sop.SpecialOfferID AS PromotionKey,
    COALESCE(
        (SELECT c.CurrencyKey
         FROM DimCurrency c
         INNER JOIN CurrencyRate cr ON c.CurrencyName = (
             SELECT Name FROM Currency WHERE CurrencyCode = cr.ToCurrencyCode
         )
         WHERE cr.CurrencyRateID = soh.CurrencyRateID
         LIMIT 1),
        1
    ) AS CurrencyKey,
    soh.SalesOrderNumber,
    sod.SalesOrderDetailID AS SalesOrderLineNumber,
    sod.OrderQty AS OrderQuantity,
    sod.UnitPrice,
    sod.LineTotal AS SalesAmount
FROM SalesOrderHeader soh
INNER JOIN SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
INNER JOIN SpecialOfferProduct sop ON
    sod.SpecialOfferID = sop.SpecialOfferID
    AND sod.ProductID = sop.ProductID
WHERE soh.OnlineOrderFlag = 1;

-- ----------------------------------------------------------------------------
-- FactProductInventory: Product inventory fact table
-- Source: ProductInventory table
-- Aggregates inventory by product
-- ----------------------------------------------------------------------------
INSERT INTO FactProductInventory (ProductKey, DateKey, Quantity)
SELECT
    pi.ProductID AS ProductKey,
    CAST(STRFTIME(pi.ModifiedDate, '%Y%m%d') AS INTEGER) AS DateKey,
    SUM(pi.Quantity) AS Quantity
FROM ProductInventory pi
GROUP BY pi.ProductID, CAST(STRFTIME(pi.ModifiedDate, '%Y%m%d') AS INTEGER);

-- ----------------------------------------------------------------------------
-- FactFinance: Finance fact table
-- Note: No direct source in OLTP, creating placeholder/sample entries
-- In a real scenario, this would come from an accounting/ERP system
-- This creates sample financial data based on sales
-- ----------------------------------------------------------------------------
INSERT INTO FactFinance (
    FinanceKey,
    DateKey,
    OrganizationKey,
    DepartmentGroupKey,
    ScenarioKey,
    AccountKey,
    Amount
)
SELECT
    ROW_NUMBER() OVER (ORDER BY DateKey, AccountKey) AS FinanceKey,
    DateKey,
    1 AS OrganizationKey,  -- Default to HQ
    1 AS DepartmentGroupKey,  -- Default to first dept group
    1 AS ScenarioKey,  -- Actual scenario
    AccountKey,
    Amount
FROM (
    -- Revenue from sales
    SELECT
        CAST(STRFTIME(soh.OrderDate, '%Y%m%d') AS INTEGER) AS DateKey,
        1 AS AccountKey,  -- Revenue account
        SUM(sod.LineTotal) AS Amount
    FROM SalesOrderHeader soh
    INNER JOIN SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
    GROUP BY CAST(STRFTIME(soh.OrderDate, '%Y%m%d') AS INTEGER)

    UNION ALL

    -- Cost of goods sold (estimated as 60% of revenue)
    SELECT
        CAST(STRFTIME(soh.OrderDate, '%Y%m%d') AS INTEGER) AS DateKey,
        2 AS AccountKey,  -- COGS account
        SUM(sod.LineTotal * 0.6) AS Amount
    FROM SalesOrderHeader soh
    INNER JOIN SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
    GROUP BY CAST(STRFTIME(soh.OrderDate, '%Y%m%d') AS INTEGER)
) finance_data;

-- ============================================================================
-- ETL COMPLETE
-- ============================================================================

-- Summary of transformations:
-- 1. DimCurrency: Direct mapping from Currency
-- 2. DimProductCategory: Direct mapping from ProductCategory
-- 3. DimProductSubcategory: Direct mapping from ProductSubcategory
-- 4. DimProduct: Direct mapping from Product (filtered for valid subcategories)
-- 5. DimGeography: Aggregated from Address, StateProvince, CountryRegion
-- 6. DimCustomer: Mapped from Customer + Person (many fields null due to source limitations)
-- 7. DimPromotion: Direct mapping from SpecialOffer
-- 8. DimDate: Generated date dimension for 2000-2030
-- 9. DimDepartmentGroup: Aggregated from Department.GroupName
-- 10. DimAccount: Placeholder data (no source available)
-- 11. DimOrganization: Placeholder data (no source available)
-- 12. DimScenario: Standard scenario entries (no source available)
-- 13. FactInternetSales: Mapped from SalesOrderHeader + SalesOrderDetail (online only)
-- 14. FactProductInventory: Aggregated from ProductInventory
-- 15. FactFinance: Derived/placeholder data from sales (no direct source)
