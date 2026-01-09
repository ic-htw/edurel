# Explanation of customer life cycle value queries
you are a SQL and customer analytics specialist
## the following star/snowflake schema ist given
```yaml
tables:
- tablename: DimAccount
  columns:
  - columnname: AccountKey
    type: INTEGER
  - columnname: ParentAccountKey
    type: INTEGER
  - columnname: AccountCodeAlternateKey
    type: INTEGER
  - columnname: ParentAccountCodeAlternateKey
    type: INTEGER
  - columnname: AccountDescription
    type: VARCHAR
  - columnname: AccountType
    type: VARCHAR
  - columnname: Operator
    type: VARCHAR
  - columnname: CustomMembers
    type: VARCHAR
  - columnname: ValueType
    type: VARCHAR
  - columnname: CustomMemberOptions
    type: VARCHAR
  primary_key:
  - AccountKey
  foreign_keys:
  - sourcecolumns:
    - ParentAccountKey
    targettable: DimAccount
    targetcolumns:
    - AccountKey
- tablename: DimCurrency
  columns:
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: CurrencyAlternateKey
    type: VARCHAR
  - columnname: CurrencyName
    type: VARCHAR
  primary_key:
  - CurrencyKey
- tablename: DimCustomer
  columns:
  - columnname: CustomerKey
    type: INTEGER
  - columnname: GeographyKey
    type: INTEGER
  - columnname: CustomerAlternateKey
    type: VARCHAR
  - columnname: Title
    type: VARCHAR
  - columnname: FirstName
    type: VARCHAR
  - columnname: MiddleName
    type: VARCHAR
  - columnname: LastName
    type: VARCHAR
  - columnname: NameStyle
    type: BIT
  - columnname: BirthDate
    type: DATE
  - columnname: MaritalStatus
    type: VARCHAR
  - columnname: Suffix
    type: VARCHAR
  - columnname: Gender
    type: VARCHAR
  - columnname: EmailAddress
    type: VARCHAR
  - columnname: YearlyIncome
    type: DECIMAL(13,2)
  - columnname: TotalChildren
    type: INTEGER
  - columnname: NumberChildrenAtHome
    type: INTEGER
  - columnname: EnglishEducation
    type: VARCHAR
  - columnname: SpanishEducation
    type: VARCHAR
  - columnname: FrenchEducation
    type: VARCHAR
  - columnname: EnglishOccupation
    type: VARCHAR
  - columnname: SpanishOccupation
    type: VARCHAR
  - columnname: FrenchOccupation
    type: VARCHAR
  - columnname: HouseOwnerFlag
    type: VARCHAR
  - columnname: NumberCarsOwned
    type: INTEGER
  - columnname: AddressLine1
    type: VARCHAR
  - columnname: AddressLine2
    type: VARCHAR
  - columnname: Phone
    type: VARCHAR
  - columnname: DateFirstPurchase
    type: DATE
  - columnname: CommuteDistance
    type: VARCHAR
  primary_key:
  - CustomerKey
  foreign_keys:
  - sourcecolumns:
    - GeographyKey
    targettable: DimGeography
    targetcolumns:
    - GeographyKey
- tablename: DimDate
  columns:
  - columnname: DateKey
    type: INTEGER
  - columnname: FullDateAlternateKey
    type: DATE
  - columnname: DayNumberOfWeek
    type: INTEGER
  - columnname: EnglishDayNameOfWeek
    type: VARCHAR
  - columnname: SpanishDayNameOfWeek
    type: VARCHAR
  - columnname: FrenchDayNameOfWeek
    type: VARCHAR
  - columnname: DayNumberOfMonth
    type: INTEGER
  - columnname: DayNumberOfYear
    type: INTEGER
  - columnname: WeekNumberOfYear
    type: INTEGER
  - columnname: EnglishMonthName
    type: VARCHAR
  - columnname: SpanishMonthName
    type: VARCHAR
  - columnname: FrenchMonthName
    type: VARCHAR
  - columnname: MonthNumberOfYear
    type: INTEGER
  - columnname: CalendarQuarter
    type: INTEGER
  - columnname: CalendarYear
    type: INTEGER
  - columnname: CalendarSemester
    type: INTEGER
  - columnname: FiscalQuarter
    type: INTEGER
  - columnname: FiscalYear
    type: INTEGER
  - columnname: FiscalSemester
    type: INTEGER
  primary_key:
  - DateKey
- tablename: DimDepartmentGroup
  columns:
  - columnname: DepartmentGroupKey
    type: INTEGER
  - columnname: ParentDepartmentGroupKey
    type: INTEGER
  - columnname: DepartmentGroupName
    type: VARCHAR
  primary_key:
  - DepartmentGroupKey
  foreign_keys:
  - sourcecolumns:
    - ParentDepartmentGroupKey
    targettable: DimDepartmentGroup
    targetcolumns:
    - DepartmentGroupKey
- tablename: DimEmployee
  columns:
  - columnname: EmployeeKey
    type: INTEGER
  - columnname: ParentEmployeeKey
    type: INTEGER
  - columnname: EmployeeNationalIDAlternateKey
    type: VARCHAR
  - columnname: ParentEmployeeNationalIDAlternateKey
    type: VARCHAR
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: FirstName
    type: VARCHAR
  - columnname: LastName
    type: VARCHAR
  - columnname: MiddleName
    type: VARCHAR
  - columnname: NameStyle
    type: BIT
  - columnname: Title
    type: VARCHAR
  - columnname: HireDate
    type: DATE
  - columnname: BirthDate
    type: DATE
  - columnname: LoginID
    type: VARCHAR
  - columnname: EmailAddress
    type: VARCHAR
  - columnname: Phone
    type: VARCHAR
  - columnname: MaritalStatus
    type: VARCHAR
  - columnname: EmergencyContactName
    type: VARCHAR
  - columnname: EmergencyContactPhone
    type: VARCHAR
  - columnname: SalariedFlag
    type: BIT
  - columnname: Gender
    type: VARCHAR
  - columnname: PayFrequency
    type: INTEGER
  - columnname: BaseRate
    type: DECIMAL(13,2)
  - columnname: VacationHours
    type: INTEGER
  - columnname: SickLeaveHours
    type: INTEGER
  - columnname: CurrentFlag
    type: BIT
  - columnname: SalesPersonFlag
    type: BIT
  - columnname: DepartmentName
    type: VARCHAR
  - columnname: StartDate
    type: DATE
  - columnname: EndDate
    type: DATE
  - columnname: Status
    type: VARCHAR
  - columnname: EmployeePhoto
    type: VARCHAR
  primary_key:
  - EmployeeKey
  foreign_keys:
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
  - sourcecolumns:
    - ParentEmployeeKey
    targettable: DimEmployee
    targetcolumns:
    - EmployeeKey
- tablename: DimGeography
  columns:
  - columnname: GeographyKey
    type: INTEGER
  - columnname: City
    type: VARCHAR
  - columnname: StateProvinceCode
    type: VARCHAR
  - columnname: StateProvinceName
    type: VARCHAR
  - columnname: CountryRegionCode
    type: VARCHAR
  - columnname: EnglishCountryRegionName
    type: VARCHAR
  - columnname: SpanishCountryRegionName
    type: VARCHAR
  - columnname: FrenchCountryRegionName
    type: VARCHAR
  - columnname: PostalCode
    type: VARCHAR
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: IpAddressLocator
    type: VARCHAR
  primary_key:
  - GeographyKey
  foreign_keys:
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
- tablename: DimOrganization
  columns:
  - columnname: OrganizationKey
    type: INTEGER
  - columnname: ParentOrganizationKey
    type: INTEGER
  - columnname: PercentageOfOwnership
    type: VARCHAR
  - columnname: OrganizationName
    type: VARCHAR
  - columnname: CurrencyKey
    type: INTEGER
  primary_key:
  - OrganizationKey
  foreign_keys:
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
  - sourcecolumns:
    - ParentOrganizationKey
    targettable: DimOrganization
    targetcolumns:
    - OrganizationKey
- tablename: DimProduct
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: ProductAlternateKey
    type: VARCHAR
  - columnname: ProductSubcategoryKey
    type: INTEGER
  - columnname: WeightUnitMeasureCode
    type: VARCHAR
  - columnname: SizeUnitMeasureCode
    type: VARCHAR
  - columnname: EnglishProductName
    type: VARCHAR
  - columnname: SpanishProductName
    type: VARCHAR
  - columnname: FrenchProductName
    type: VARCHAR
  - columnname: StandardCost
    type: DECIMAL(13,2)
  - columnname: FinishedGoodsFlag
    type: BIT
  - columnname: Color
    type: VARCHAR
  - columnname: SafetyStockLevel
    type: INTEGER
  - columnname: ReorderPoint
    type: INTEGER
  - columnname: ListPrice
    type: DECIMAL(13,2)
  - columnname: Size
    type: VARCHAR
  - columnname: SizeRange
    type: VARCHAR
  - columnname: Weight
    type: FLOAT
  - columnname: DaysToManufacture
    type: INTEGER
  - columnname: ProductLine
    type: VARCHAR
  - columnname: DealerPrice
    type: DECIMAL(13,2)
  - columnname: Class
    type: VARCHAR
  - columnname: Style
    type: VARCHAR
  - columnname: ModelName
    type: VARCHAR
  - columnname: LargePhoto
    type: VARCHAR
  - columnname: EnglishDescription
    type: VARCHAR
  - columnname: FrenchDescription
    type: VARCHAR
  - columnname: ChineseDescription
    type: VARCHAR
  - columnname: ArabicDescription
    type: VARCHAR
  - columnname: HebrewDescription
    type: VARCHAR
  - columnname: ThaiDescription
    type: VARCHAR
  - columnname: GermanDescription
    type: VARCHAR
  - columnname: JapaneseDescription
    type: VARCHAR
  - columnname: TurkishDescription
    type: VARCHAR
  - columnname: StartDate
    type: TIMESTAMP
  - columnname: EndDate
    type: TIMESTAMP
  - columnname: Status
    type: VARCHAR
  primary_key:
  - ProductKey
  foreign_keys:
  - sourcecolumns:
    - ProductSubcategoryKey
    targettable: DimProductSubcategory
    targetcolumns:
    - ProductSubcategoryKey
- tablename: DimProductCategory
  columns:
  - columnname: ProductCategoryKey
    type: INTEGER
  - columnname: ProductCategoryAlternateKey
    type: INTEGER
  - columnname: EnglishProductCategoryName
    type: VARCHAR
  - columnname: SpanishProductCategoryName
    type: VARCHAR
  - columnname: FrenchProductCategoryName
    type: VARCHAR
  primary_key:
  - ProductCategoryKey
- tablename: DimProductSubcategory
  columns:
  - columnname: ProductSubcategoryKey
    type: INTEGER
  - columnname: ProductSubcategoryAlternateKey
    type: INTEGER
  - columnname: EnglishProductSubcategoryName
    type: VARCHAR
  - columnname: SpanishProductSubcategoryName
    type: VARCHAR
  - columnname: FrenchProductSubcategoryName
    type: VARCHAR
  - columnname: ProductCategoryKey
    type: INTEGER
  primary_key:
  - ProductSubcategoryKey
  foreign_keys:
  - sourcecolumns:
    - ProductCategoryKey
    targettable: DimProductCategory
    targetcolumns:
    - ProductCategoryKey
- tablename: DimPromotion
  columns:
  - columnname: PromotionKey
    type: INTEGER
  - columnname: PromotionAlternateKey
    type: INTEGER
  - columnname: EnglishPromotionName
    type: VARCHAR
  - columnname: SpanishPromotionName
    type: VARCHAR
  - columnname: FrenchPromotionName
    type: VARCHAR
  - columnname: DiscountPct
    type: FLOAT
  - columnname: EnglishPromotionType
    type: VARCHAR
  - columnname: SpanishPromotionType
    type: VARCHAR
  - columnname: FrenchPromotionType
    type: VARCHAR
  - columnname: EnglishPromotionCategory
    type: VARCHAR
  - columnname: SpanishPromotionCategory
    type: VARCHAR
  - columnname: FrenchPromotionCategory
    type: VARCHAR
  - columnname: StartDate
    type: TIMESTAMP
  - columnname: EndDate
    type: TIMESTAMP
  - columnname: MinQty
    type: INTEGER
  - columnname: MaxQty
    type: INTEGER
  primary_key:
  - PromotionKey
- tablename: DimReseller
  columns:
  - columnname: ResellerKey
    type: INTEGER
  - columnname: GeographyKey
    type: INTEGER
  - columnname: ResellerAlternateKey
    type: VARCHAR
  - columnname: Phone
    type: VARCHAR
  - columnname: BusinessType
    type: VARCHAR
  - columnname: ResellerName
    type: VARCHAR
  - columnname: NumberEmployees
    type: INTEGER
  - columnname: OrderFrequency
    type: VARCHAR
  - columnname: OrderMonth
    type: INTEGER
  - columnname: FirstOrderYear
    type: INTEGER
  - columnname: LastOrderYear
    type: INTEGER
  - columnname: ProductLine
    type: VARCHAR
  - columnname: AddressLine1
    type: VARCHAR
  - columnname: AddressLine2
    type: VARCHAR
  - columnname: AnnualSales
    type: DECIMAL(13,2)
  - columnname: BankName
    type: VARCHAR
  - columnname: MinPaymentType
    type: INTEGER
  - columnname: MinPaymentAmount
    type: DECIMAL(13,2)
  - columnname: AnnualRevenue
    type: DECIMAL(13,2)
  - columnname: YearOpened
    type: INTEGER
  primary_key:
  - ResellerKey
  foreign_keys:
  - sourcecolumns:
    - GeographyKey
    targettable: DimGeography
    targetcolumns:
    - GeographyKey
- tablename: DimSalesReason
  columns:
  - columnname: SalesReasonKey
    type: INTEGER
  - columnname: SalesReasonAlternateKey
    type: INTEGER
  - columnname: SalesReasonName
    type: VARCHAR
  - columnname: SalesReasonReasonType
    type: VARCHAR
  primary_key:
  - SalesReasonKey
- tablename: DimSalesTerritory
  columns:
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: SalesTerritoryAlternateKey
    type: INTEGER
  - columnname: SalesTerritoryRegion
    type: VARCHAR
  - columnname: SalesTerritoryCountry
    type: VARCHAR
  - columnname: SalesTerritoryGroup
    type: VARCHAR
  - columnname: SalesTerritoryImage
    type: VARCHAR
  primary_key:
  - SalesTerritoryKey
- tablename: DimScenario
  columns:
  - columnname: ScenarioKey
    type: INTEGER
  - columnname: ScenarioName
    type: VARCHAR
  primary_key:
  - ScenarioKey
- tablename: FactCallCenter
  columns:
  - columnname: FactCallCenterID
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: WageType
    type: VARCHAR
  - columnname: Shift
    type: VARCHAR
  - columnname: LevelOneOperators
    type: INTEGER
  - columnname: LevelTwoOperators
    type: INTEGER
  - columnname: TotalOperators
    type: INTEGER
  - columnname: Calls
    type: INTEGER
  - columnname: AutomaticResponses
    type: INTEGER
  - columnname: Orders
    type: INTEGER
  - columnname: IssuesRaised
    type: INTEGER
  - columnname: AverageTimePerIssue
    type: INTEGER
  - columnname: ServiceGrade
    type: FLOAT
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
- tablename: FactCurrencyRate
  columns:
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: AverageRate
    type: FLOAT
  - columnname: EndOfDayRate
    type: FLOAT
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
- tablename: FactFinance
  columns:
  - columnname: FinanceKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: OrganizationKey
    type: INTEGER
  - columnname: DepartmentGroupKey
    type: INTEGER
  - columnname: ScenarioKey
    type: INTEGER
  - columnname: AccountKey
    type: INTEGER
  - columnname: Amount
    type: FLOAT
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - ScenarioKey
    targettable: DimScenario
    targetcolumns:
    - ScenarioKey
  - sourcecolumns:
    - OrganizationKey
    targettable: DimOrganization
    targetcolumns:
    - OrganizationKey
  - sourcecolumns:
    - DepartmentGroupKey
    targettable: DimDepartmentGroup
    targetcolumns:
    - DepartmentGroupKey
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - AccountKey
    targettable: DimAccount
    targetcolumns:
    - AccountKey
- tablename: FactInternetSales
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: OrderDateKey
    type: INTEGER
  - columnname: DueDateKey
    type: INTEGER
  - columnname: ShipDateKey
    type: INTEGER
  - columnname: CustomerKey
    type: INTEGER
  - columnname: PromotionKey
    type: INTEGER
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: SalesOrderNumber
    type: VARCHAR
  - columnname: SalesOrderLineNumber
    type: INTEGER
  - columnname: RevisionNumber
    type: INTEGER
  - columnname: OrderQuantity
    type: INTEGER
  - columnname: UnitPrice
    type: DECIMAL(13,2)
  - columnname: ExtendedAmount
    type: DECIMAL(13,2)
  - columnname: UnitPriceDiscountPct
    type: FLOAT
  - columnname: DiscountAmount
    type: FLOAT
  - columnname: ProductStandardCost
    type: DECIMAL(13,2)
  - columnname: TotalProductCost
    type: DECIMAL(13,2)
  - columnname: SalesAmount
    type: DECIMAL(13,2)
  - columnname: TaxAmt
    type: DECIMAL(13,2)
  - columnname: Freight
    type: DECIMAL(13,2)
  - columnname: CarrierTrackingNumber
    type: VARCHAR
  - columnname: CustomerPONumber
    type: VARCHAR
  - columnname: OrderDate
    type: TIMESTAMP
  - columnname: DueDate
    type: TIMESTAMP
  - columnname: ShipDate
    type: TIMESTAMP
  primary_key:
  - SalesOrderNumber
  - SalesOrderLineNumber
  foreign_keys:
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
  - sourcecolumns:
    - CustomerKey
    targettable: DimCustomer
    targetcolumns:
    - CustomerKey
  - sourcecolumns:
    - OrderDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - DueDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ShipDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ProductKey
    targettable: DimProduct
    targetcolumns:
    - ProductKey
  - sourcecolumns:
    - PromotionKey
    targettable: DimPromotion
    targetcolumns:
    - PromotionKey
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
- tablename: FactInternetSalesReason
  columns:
  - columnname: SalesOrderNumber
    type: VARCHAR
  - columnname: SalesOrderLineNumber
    type: INTEGER
  - columnname: SalesReasonKey
    type: INTEGER
  foreign_keys:
  - sourcecolumns:
    - SalesOrderNumber
    - SalesOrderLineNumber
    targettable: FactInternetSales
    targetcolumns:
    - SalesOrderNumber
    - SalesOrderLineNumber
  - sourcecolumns:
    - SalesReasonKey
    targettable: DimSalesReason
    targetcolumns:
    - SalesReasonKey
- tablename: FactProductInventory
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: MovementDate
    type: DATE
  - columnname: UnitCost
    type: DECIMAL(13,2)
  - columnname: UnitsIn
    type: INTEGER
  - columnname: UnitsOut
    type: INTEGER
  - columnname: UnitsBalance
    type: INTEGER
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ProductKey
    targettable: DimProduct
    targetcolumns:
    - ProductKey
- tablename: FactResellerSales
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: OrderDateKey
    type: INTEGER
  - columnname: DueDateKey
    type: INTEGER
  - columnname: ShipDateKey
    type: INTEGER
  - columnname: ResellerKey
    type: INTEGER
  - columnname: EmployeeKey
    type: INTEGER
  - columnname: PromotionKey
    type: INTEGER
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: SalesOrderNumber
    type: VARCHAR
  - columnname: SalesOrderLineNumber
    type: INTEGER
  - columnname: RevisionNumber
    type: INTEGER
  - columnname: OrderQuantity
    type: INTEGER
  - columnname: UnitPrice
    type: DECIMAL(13,2)
  - columnname: ExtendedAmount
    type: DECIMAL(13,2)
  - columnname: UnitPriceDiscountPct
    type: FLOAT
  - columnname: DiscountAmount
    type: FLOAT
  - columnname: ProductStandardCost
    type: DECIMAL(13,2)
  - columnname: TotalProductCost
    type: DECIMAL(13,2)
  - columnname: SalesAmount
    type: DECIMAL(13,2)
  - columnname: TaxAmt
    type: DECIMAL(13,2)
  - columnname: Freight
    type: DECIMAL(13,2)
  - columnname: CarrierTrackingNumber
    type: VARCHAR
  - columnname: CustomerPONumber
    type: VARCHAR
  - columnname: OrderDate
    type: TIMESTAMP
  - columnname: DueDate
    type: TIMESTAMP
  - columnname: ShipDate
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
  - sourcecolumns:
    - OrderDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - DueDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ShipDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - EmployeeKey
    targettable: DimEmployee
    targetcolumns:
    - EmployeeKey
  - sourcecolumns:
    - ProductKey
    targettable: DimProduct
    targetcolumns:
    - ProductKey
  - sourcecolumns:
    - PromotionKey
    targettable: DimPromotion
    targetcolumns:
    - PromotionKey
  - sourcecolumns:
    - ResellerKey
    targettable: DimReseller
    targetcolumns:
    - ResellerKey
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
- tablename: FactSalesQuota
  columns:
  - columnname: SalesQuotaKey
    type: INTEGER
  - columnname: EmployeeKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: CalendarYear
    type: INTEGER
  - columnname: CalendarQuarter
    type: INTEGER
  - columnname: SalesAmountQuota
    type: DECIMAL(13,2)
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - EmployeeKey
    targettable: DimEmployee
    targetcolumns:
    - EmployeeKey
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
- tablename: FactSurveyResponse
  columns:
  - columnname: SurveyResponseKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: CustomerKey
    type: INTEGER
  - columnname: ProductCategoryKey
    type: INTEGER
  - columnname: EnglishProductCategoryName
    type: VARCHAR
  - columnname: ProductSubcategoryKey
    type: INTEGER
  - columnname: EnglishProductSubcategoryName
    type: VARCHAR
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - CustomerKey
    targettable: DimCustomer
    targetcolumns:
    - CustomerKey
```
# Semantics of schema
## Fact Tables, Dimensions, Hirarchies
### **Fact Tables** (contain metrics/measures)
1. **FactInternetSales** - Internet sales transactions
2. **FactResellerSales** - Reseller sales transactions
3. **FactFinance** - Financial data
4. **FactCallCenter** - Call center operations
5. **FactCurrencyRate** - Currency exchange rates
6. **FactProductInventory** - Product inventory movements
7. **FactSalesQuota** - Sales quotas for employees
8. **FactSurveyResponse** - Customer survey responses
9. **FactInternetSalesReason** - Bridge table linking sales to reasons

### **Dimension Tables** (contain descriptive attributes)
- **DimDate** - Time dimension
- **DimProduct** - Product information
- **DimCustomer** - Customer details
- **DimEmployee** - Employee information
- **DimReseller** - Reseller details
- **DimGeography** - Geographic locations
- **DimCurrency** - Currency information
- **DimPromotion** - Promotion details
- **DimSalesTerritory** - Sales territory data
- **DimSalesReason** - Sales reason categories
- **DimAccount** - Account information
- **DimOrganization** - Organization structure
- **DimDepartmentGroup** - Department groups
- **DimScenario** - Scenario planning
- **DimProductCategory** - Product categories
- **DimProductSubcategory** - Product subcategories

### **Hierarchies**

**Product Hierarchy:**
- DimProduct → DimProductSubcategory → DimProductCategory

**Geography Hierarchy:**
- DimGeography: City → StateProvince → Country → SalesTerritory

**Time Hierarchy:**
- DimDate: Day → Week → Month → Quarter → Semester → Year (both Calendar and Fiscal)

**Employee Hierarchy:**
- DimEmployee (ParentEmployeeKey → EmployeeKey) - organizational reporting structure

**Account Hierarchy:**
- DimAccount (ParentAccountKey → AccountKey) - chart of accounts structure

**Organization Hierarchy:**
- DimOrganization (ParentOrganizationKey → OrganizationKey) - corporate structure

**Department Hierarchy:**
- DimDepartmentGroup (ParentDepartmentGroupKey → DepartmentGroupKey)

**Customer-Geography:**
- DimCustomer → DimGeography → DimSalesTerritory

This is a classic **star/snowflake schema** for enterprise sales and financial analytics.

## Fact Table Relationships

### **FactInternetSales**
- **DimProduct** - What was sold
- **DimCustomer** - Who bought it
- **DimDate** (3x) - OrderDateKey, DueDateKey, ShipDateKey (when ordered/due/shipped)
- **DimPromotion** - Which promotion applied
- **DimCurrency** - Transaction currency
- **DimSalesTerritory** - Sales region

### **FactResellerSales**
- **DimProduct** - What was sold
- **DimReseller** - Which reseller made the sale
- **DimEmployee** - Employee who handled the sale
- **DimDate** (3x) - OrderDateKey, DueDateKey, ShipDateKey
- **DimPromotion** - Promotion applied
- **DimCurrency** - Transaction currency
- **DimSalesTerritory** - Sales region

### **FactFinance**
- **DimDate** - Financial period
- **DimOrganization** - Which organizational unit
- **DimDepartmentGroup** - Which department
- **DimScenario** - Budget/Actual/Forecast scenario
- **DimAccount** - Chart of accounts (revenue/expense type)

### **FactCallCenter**
- **DimDate** - Date of call center metrics

### **FactCurrencyRate**
- **DimDate** - Date of exchange rate
- **DimCurrency** - Which currency

### **FactProductInventory**
- **DimProduct** - Which product
- **DimDate** - Date of inventory movement

### **FactSalesQuota**
- **DimEmployee** - Employee with quota
- **DimDate** - Quota period

### **FactSurveyResponse**
- **DimDate** - Survey date
- **DimCustomer** - Customer responding
- **DimProductCategory** - (denormalized reference)
- **DimProductSubcategory** - (denormalized reference)

### **FactInternetSalesReason** (Bridge Table)
- **FactInternetSales** - Links to sales transaction
- **DimSalesReason** - Reason for purchase (many-to-many relationship)
## SQL Query
```sql
WITH CustomerValueTier AS (
    SELECT
        fis.CustomerKey,
        ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) AS ValueQuartile,
        CASE
            WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 1 THEN 'High Value'
            WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 2 THEN 'Medium-High Value'
            WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 3 THEN 'Medium-Low Value'
            ELSE 'Low Value'
        END AS ValueTier
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

CustomerCategoryPurchases AS (
    SELECT
        fis.CustomerKey,
        pc.EnglishProductCategoryName AS CategoryName,
        MIN(fis.OrderDate) AS FirstCategoryPurchaseDate,
        MAX(fis.OrderDate) AS LastCategoryPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS CategoryOrders,
        COUNT(*) AS CategoryLineItems,
        ROUND(SUM(fis.SalesAmount), 2) AS CategoryRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS CategoryGrossProfit,
        COUNT(DISTINCT fis.ProductKey) AS UniqueProductsInCategory
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    WHERE pc.EnglishProductCategoryName IS NOT NULL
    GROUP BY fis.CustomerKey, pc.EnglishProductCategoryName
),

AllCategories AS (
    SELECT DISTINCT EnglishProductCategoryName AS CategoryName
    FROM DimProductCategory
    WHERE EnglishProductCategoryName IS NOT NULL
),

CustomerCategoryMatrix AS (
    SELECT
        cvt.CustomerKey,
        cvt.ValueTier,
        cvt.LifetimeRevenue,
        cvt.TotalOrders,
        ac.CategoryName,
        COALESCE(ccp.CategoryOrders, 0) AS CategoryOrders,
        COALESCE(ccp.CategoryRevenue, 0) AS CategoryRevenue,
        COALESCE(ccp.CategoryGrossProfit, 0) AS CategoryGrossProfit,
        CASE WHEN ccp.CustomerKey IS NOT NULL THEN 1 ELSE 0 END AS HasPurchasedCategory,
        ccp.FirstCategoryPurchaseDate,
        ccp.LastCategoryPurchaseDate
    FROM CustomerValueTier cvt
    CROSS JOIN AllCategories ac
    LEFT JOIN CustomerCategoryPurchases ccp
        ON cvt.CustomerKey = ccp.CustomerKey
        AND ac.CategoryName = ccp.CategoryName
),

CustomerCategorySummary AS (
    SELECT
        ccm.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        ccm.ValueTier,
        ccm.LifetimeRevenue,
        ccm.TotalOrders,
        c.YearlyIncome,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        COUNT(*) AS TotalCategories,
        SUM(ccm.HasPurchasedCategory) AS CategoriesPurchased,
        COUNT(*) - SUM(ccm.HasPurchasedCategory) AS CategoriesNotPurchased,
        ROUND(100.0 * SUM(ccm.HasPurchasedCategory) / COUNT(*), 2) AS CategoryPenetrationPct,
        STRING_AGG(CASE WHEN ccm.HasPurchasedCategory = 1 THEN ccm.CategoryName END, ', ') AS PurchasedCategories,
        STRING_AGG(CASE WHEN ccm.HasPurchasedCategory = 0 THEN ccm.CategoryName END, ', ') AS UnpurchasedCategories
    FROM CustomerCategoryMatrix ccm
    INNER JOIN DimCustomer c ON ccm.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    GROUP BY ccm.CustomerKey, c.FirstName, c.LastName, ccm.ValueTier, ccm.LifetimeRevenue,
             ccm.TotalOrders, c.YearlyIncome, g.EnglishCountryRegionName, st.SalesTerritoryRegion
),

CategoryAffinityPatterns AS (
    -- Find which categories are commonly purchased together
    SELECT
        ccp1.CategoryName AS Category1,
        ccp2.CategoryName AS Category2,
        COUNT(DISTINCT ccp1.CustomerKey) AS CustomerCount,
        ROUND(AVG(ccp1.CategoryRevenue + ccp2.CategoryRevenue), 2) AS AvgCombinedRevenue
    FROM CustomerCategoryPurchases ccp1
    INNER JOIN CustomerCategoryPurchases ccp2
        ON ccp1.CustomerKey = ccp2.CustomerKey
        AND ccp1.CategoryName < ccp2.CategoryName
    GROUP BY ccp1.CategoryName, ccp2.CategoryName
    HAVING COUNT(DISTINCT ccp1.CustomerKey) >= 10
),

CrossSellOpportunities AS (
    SELECT
        ccm.CustomerKey,
        ccs.CustomerName,
        ccs.ValueTier,
        ccs.LifetimeRevenue,
        ccs.TotalOrders,
        ccs.YearlyIncome,
        ccs.Country,
        ccs.CategoryPenetrationPct,
        ccm.CategoryName AS OpportunityCategory,
        cap.Category1 AS OwnedCategory,
        cap.CustomerCount AS AffinityStrength,
        cap.AvgCombinedRevenue AS PotentialRevenue,
        RANK() OVER (PARTITION BY ccm.CustomerKey ORDER BY cap.CustomerCount DESC, cap.AvgCombinedRevenue DESC) AS OpportunityRank
    FROM CustomerCategoryMatrix ccm
    INNER JOIN CustomerCategorySummary ccs ON ccm.CustomerKey = ccs.CustomerKey
    INNER JOIN CategoryAffinityPatterns cap
        ON ccm.CategoryName = cap.Category2
        AND ccm.HasPurchasedCategory = 0
    INNER JOIN CustomerCategoryMatrix ccm_owned
        ON ccm.CustomerKey = ccm_owned.CustomerKey
        AND cap.Category1 = ccm_owned.CategoryName
        AND ccm_owned.HasPurchasedCategory = 1
    WHERE ccs.ValueTier IN ('High Value', 'Medium-High Value')
),

TopCrossSellOpportunities AS (
    SELECT
        cso.CustomerKey,
        cso.CustomerName,
        cso.ValueTier,
        cso.LifetimeRevenue,
        cso.TotalOrders,
        cso.YearlyIncome,
        cso.Country,
        cso.CategoryPenetrationPct,
        cso.OpportunityCategory AS RecommendedCategory,
        cso.OwnedCategory AS BasedOnOwnership,
        cso.AffinityStrength,
        cso.PotentialRevenue,
        cso.OpportunityRank,
        CASE
            WHEN cso.OpportunityRank = 1 THEN 'Top Priority'
            WHEN cso.OpportunityRank <= 3 THEN 'High Priority'
            WHEN cso.OpportunityRank <= 5 THEN 'Medium Priority'
            ELSE 'Low Priority'
        END AS CrossSellPriority,
        CASE
            WHEN cso.ValueTier = 'High Value' AND cso.OpportunityRank = 1 THEN 'Personalized outreach with premium offer'
            WHEN cso.ValueTier = 'High Value' THEN 'Targeted email with category-specific benefits'
            WHEN cso.ValueTier = 'Medium-High Value' THEN 'Automated campaign with bundle discount'
            ELSE 'Include in general cross-sell communications'
        END AS RecommendedApproach
    FROM CrossSellOpportunities cso
    WHERE cso.OpportunityRank <= 5
)

SELECT
    tcso.CustomerKey,
    tcso.CustomerName,
    tcso.ValueTier,
    tcso.LifetimeRevenue,
    tcso.TotalOrders,
    tcso.YearlyIncome,
    tcso.Country,
    tcso.CategoryPenetrationPct,
    tcso.RecommendedCategory,
    tcso.BasedOnOwnership,
    tcso.AffinityStrength,
    tcso.PotentialRevenue,
    tcso.OpportunityRank,
    tcso.CrossSellPriority,
    tcso.RecommendedApproach
FROM TopCrossSellOpportunities tcso
ORDER BY tcso.ValueTier, tcso.LifetimeRevenue DESC, tcso.OpportunityRank;
```

## Task
- analyse the given SQL query
- for each calculated column in each CTE
  - analyse column definition (KPI)
  - provide a verbal definition of that KPI
  - give a mathematical formula in latex if posible
  - provide examples if possible
  

# Output
the output should be put into a markdown file with name q-clv04.md in directory databases/adw-olap
it should have the following structure
# KPI 1
## Definition
## Examples
# KPI 2
## Definition
## Examples
# KPI 3
## Definition
## Examples
...

Think hard.