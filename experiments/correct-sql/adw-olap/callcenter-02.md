# Bug Fixing in SQL Query
you are a sql specialist
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

## Query
```sql
WITH DailyOperatorMetrics AS (
    SELECT
        dd.FullDateAlternateKey AS Date,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.CalendarMonth,
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
        ROUND(STDEV(ConversionRate), 2) AS StdDevConversionRate,
        ROUND(STDEV(ServiceGrade), 4) AS StdDevServiceGrade,
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
```



## Task
- fix bugs in the given query 
- provide correct code for duckdb database system 
- fix wrong column names
- fix wrong function names
- the following error messages were given:
  - Table "dd" does not have a column named "CalendarMonth"
  - Scalar Function with name stdev does not exist!
- provide the rewritten query in file callcenter-02.sql in directory experiments/correct-sql/adw-olap
- only provide sql code


Think hard.