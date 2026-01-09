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
WITH CustomerPurchaseMetrics AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        (CURRENT_DATE - MAX(fis.OrderDate)::DATE) AS DaysSinceLastPurchase,
        (MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays,
        ROUND(CAST((MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS DOUBLE) / NULLIF(COUNT(DISTINCT fis.SalesOrderNumber) - 1, 0), 2) AS AvgDaysBetweenOrders,
        ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS LifetimeGrossProfit,
        ROUND(AVG(fis.SalesAmount), 2) AS AvgTransactionValue,
        ROUND(SUM(fis.DiscountAmount), 2) AS TotalDiscounts
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

RecentActivityTrends AS (
    -- Compare recent 3 months vs. previous 3 months
    SELECT
        fis.CustomerKey,
        COUNT(DISTINCT CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) <= 90 THEN fis.SalesOrderNumber END) AS OrdersLast90Days,
        COUNT(DISTINCT CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) BETWEEN 91 AND 180 THEN fis.SalesOrderNumber END) AS OrdersPrevious90Days,
        ROUND(SUM(CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) <= 90 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenueLast90Days,
        ROUND(SUM(CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) BETWEEN 91 AND 180 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenuePrevious90Days
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

ChurnRiskFactors AS (
    SELECT
        cpm.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        cpm.FirstPurchaseDate,
        cpm.LastPurchaseDate,
        cpm.DaysSinceLastPurchase,
        cpm.CustomerTenureDays,
        ROUND(cpm.CustomerTenureDays / 365.25, 2) AS CustomerTenureYears,
        cpm.TotalOrders,
        cpm.AvgDaysBetweenOrders,
        cpm.LifetimeRevenue,
        cpm.LifetimeGrossProfit,
        cpm.AvgTransactionValue,
        rat.OrdersLast90Days,
        rat.OrdersPrevious90Days,
        rat.RevenueLast90Days,
        rat.RevenuePrevious90Days,
        -- Risk Factor 1: Recency Risk (0-35 points)
        CASE
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 3 THEN 35
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 2 THEN 25
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 1.5 THEN 15
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders THEN 5
            ELSE 0
        END AS RecencyRiskScore,
        -- Risk Factor 2: Activity Decline (0-30 points)
        CASE
            WHEN rat.OrdersLast90Days = 0 AND rat.OrdersPrevious90Days > 0 THEN 30
            WHEN rat.OrdersLast90Days < rat.OrdersPrevious90Days * 0.5 THEN 20
            WHEN rat.OrdersLast90Days < rat.OrdersPrevious90Days THEN 10
            ELSE 0
        END AS ActivityDeclineScore,
        -- Risk Factor 3: Revenue Decline (0-20 points)
        CASE
            WHEN rat.RevenueLast90Days = 0 AND rat.RevenuePrevious90Days > 0 THEN 20
            WHEN rat.RevenueLast90Days < rat.RevenuePrevious90Days * 0.5 THEN 15
            WHEN rat.RevenueLast90Days < rat.RevenuePrevious90Days THEN 8
            ELSE 0
        END AS RevenueDeclineScore,
        -- Risk Factor 4: Low Engagement (0-15 points)
        CASE
            WHEN cpm.TotalOrders <= 2 AND cpm.CustomerTenureDays > 365 THEN 15
            WHEN cpm.TotalOrders <= 3 AND cpm.CustomerTenureDays > 180 THEN 10
            WHEN cpm.TotalOrders <= 5 THEN 5
            ELSE 0
        END AS LowEngagementScore
    FROM CustomerPurchaseMetrics cpm
    LEFT JOIN RecentActivityTrends rat ON cpm.CustomerKey = rat.CustomerKey
    INNER JOIN DimCustomer c ON cpm.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
),

ChurnRiskScoring AS (
    SELECT
        crf.*,
        -- Total Churn Risk Score (0-100)
        crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore AS TotalChurnRiskScore,
        -- Churn Risk Category
        CASE
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 70 THEN 'Critical Risk'
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 50 THEN 'High Risk'
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 30 THEN 'Moderate Risk'
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 15 THEN 'Low Risk'
            ELSE 'Healthy'
        END AS ChurnRiskCategory,
        -- Value Tier
        NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) AS ValueQuartile,
        CASE
            WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 1 THEN 'High Value'
            WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 2 THEN 'Medium-High Value'
            WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 3 THEN 'Medium-Low Value'
            ELSE 'Low Value'
        END AS ValueTier
    FROM ChurnRiskFactors crf
),

RetentionPrioritization AS (
    SELECT
        crs.CustomerKey,
        crs.CustomerName,
        crs.ValueTier,
        crs.ChurnRiskCategory,
        crs.TotalChurnRiskScore,
        crs.Country,
        crs.SalesTerritoryRegion,
        crs.YearlyIncome,
        crs.FirstPurchaseDate,
        crs.LastPurchaseDate,
        crs.DaysSinceLastPurchase,
        crs.CustomerTenureYears,
        crs.TotalOrders,
        crs.LifetimeRevenue,
        crs.LifetimeGrossProfit,
        crs.AvgTransactionValue,
        crs.OrdersLast90Days,
        crs.OrdersPrevious90Days,
        crs.RevenueLast90Days,
        crs.RevenuePrevious90Days,
        crs.RecencyRiskScore,
        crs.ActivityDeclineScore,
        crs.RevenueDeclineScore,
        crs.LowEngagementScore,
        -- Expected Annual Value (based on historical patterns)
        ROUND(crs.LifetimeRevenue / NULLIF(crs.CustomerTenureYears, 0), 2) AS ExpectedAnnualRevenue,
        -- Value at Risk (what we stand to lose)
        ROUND((crs.LifetimeRevenue / NULLIF(crs.CustomerTenureYears, 0)) * 2, 2) AS TwoYearValueAtRisk,
        -- Retention Priority Score (combines risk and value)
        ROUND(
            (crs.TotalChurnRiskScore * 0.6) +
            (crs.ValueQuartile * 10 * 0.4)
        , 2) AS RetentionPriorityScore,
        -- Recommended retention investment
        CASE
            WHEN crs.ValueTier = 'High Value' AND crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'HIGH: Up to 20% of annual value'
            WHEN crs.ValueTier = 'High Value' AND crs.ChurnRiskCategory = 'Moderate Risk' THEN 'MEDIUM-HIGH: Up to 10% of annual value'
            WHEN crs.ValueTier IN ('High Value', 'Medium-High Value') AND crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'MEDIUM: Up to 15% of annual value'
            WHEN crs.ValueTier = 'Medium-High Value' THEN 'MEDIUM: Up to 8% of annual value'
            WHEN crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'LOW-MEDIUM: Up to 5% of annual value'
            ELSE 'LOW: Standard retention budget'
        END AS RetentionInvestmentRecommendation,
        -- Recommended retention action
        CASE
            WHEN crs.ChurnRiskCategory = 'Critical Risk' AND crs.ValueTier = 'High Value' THEN 'URGENT: Executive outreach, personalized offer, satisfaction survey'
            WHEN crs.ChurnRiskCategory = 'Critical Risk' THEN 'URGENT: Personal call/email, win-back offer, identify issues'
            WHEN crs.ChurnRiskCategory = 'High Risk' AND crs.ValueTier IN ('High Value', 'Medium-High Value') THEN 'HIGH PRIORITY: Personalized re-engagement, special incentive'
            WHEN crs.ChurnRiskCategory = 'High Risk' THEN 'Re-engagement campaign, limited-time offer'
            WHEN crs.ChurnRiskCategory = 'Moderate Risk' THEN 'Proactive outreach, engagement content, reminder campaign'
            WHEN crs.ChurnRiskCategory = 'Low Risk' THEN 'Standard nurture campaign'
            ELSE 'Continue standard customer communications'
        END AS RetentionAction,
        RANK() OVER (ORDER BY
            (crs.TotalChurnRiskScore * 0.6) + (crs.ValueQuartile * 10 * 0.4) DESC,
            crs.LifetimeRevenue DESC
        ) AS RetentionPriorityRank
    FROM ChurnRiskScoring crs
    WHERE crs.TotalChurnRiskScore >= 15  -- Only customers with some risk
)

SELECT
    rp.CustomerKey,
    rp.CustomerName,
    rp.ValueTier,
    rp.ChurnRiskCategory,
    rp.TotalChurnRiskScore,
    rp.RetentionPriorityScore,
    rp.RetentionPriorityRank,
    rp.Country,
    rp.SalesTerritoryRegion,
    rp.YearlyIncome,
    rp.DaysSinceLastPurchase,
    rp.CustomerTenureYears,
    rp.TotalOrders,
    rp.LifetimeRevenue,
    rp.LifetimeGrossProfit,
    rp.ExpectedAnnualRevenue,
    rp.TwoYearValueAtRisk,
    rp.OrdersLast90Days,
    rp.OrdersPrevious90Days,
    rp.RevenueLast90Days,
    rp.RevenuePrevious90Days,
    rp.RecencyRiskScore,
    rp.ActivityDeclineScore,
    rp.RevenueDeclineScore,
    rp.LowEngagementScore,
    rp.RetentionInvestmentRecommendation,
    rp.RetentionAction
FROM RetentionPrioritization rp
WHERE rp.ChurnRiskCategory IN ('Critical Risk', 'High Risk', 'Moderate Risk')
ORDER BY rp.RetentionPriorityScore DESC, rp.LifetimeRevenue DESC;
```

## Task
- analyse the given SQL query
- for each calculated column in each CTE
  - analyse column definition (KPI)
  - provide a verbal definition of that KPI
  - give a mathematical formula in latex if posible
  - provide examples if possible
  

# Output
the output should be put into a markdown file with name q-clv05.md in directory databases/adw-olap
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