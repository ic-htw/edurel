create table DimAccount(
	AccountKey integer not null primary key,
	ParentAccountKey integer,
	AccountCodeAlternateKey integer,
	ParentAccountCodeAlternateKey integer,
	AccountDescription varchar,
	AccountType varchar,
	Operator varchar,
	CustomMembers varchar,
	ValueType varchar,
	CustomMemberOptions varchar,
  constraint FK_DimAccount_DimAccount foreign key (ParentAccountKey) references DimAccount (AccountKey)
);

create table DimCurrency(
	CurrencyKey integer not null primary key,
	CurrencyAlternateKey varchar,
	CurrencyName varchar
);


create table DimSalesTerritory(
	SalesTerritoryKey integer not null primary key,
	SalesTerritoryAlternateKey integer,
	SalesTerritoryRegion varchar,
	SalesTerritoryCountry varchar,
	SalesTerritoryGroup varchar,
	SalesTerritoryImage varchar
);


create table DimGeography(
	GeographyKey integer not null primary key,
	City varchar,
	StateProvinceCode varchar,
	StateProvinceName varchar,
	CountryRegionCode varchar,
	EnglishCountryRegionName varchar,
	SpanishCountryRegionName varchar,
	FrenchCountryRegionName varchar,
	PostalCode varchar,
	SalesTerritoryKey integer,
	IpAddressLocator varchar,
  constraint FK_DimGeography_DimSalesTerritory foreign key (SalesTerritoryKey) references DimSalesTerritory (SalesTerritoryKey)
);


create table DimCustomer(
	CustomerKey integer not null primary key,
	GeographyKey integer,
	CustomerAlternateKey varchar,
	Title varchar,
	FirstName varchar,
	MiddleName varchar,
	LastName varchar,
	NameStyle bit,
	BirthDate date,
	MaritalStatus varchar,
	Suffix varchar,
	Gender varchar,
	EmailAddress varchar,
	YearlyIncome decimal(13,2),
	TotalChildren integer,
	NumberChildrenAtHome integer,
	EnglishEducation varchar,
	SpanishEducation varchar,
	FrenchEducation varchar,
	EnglishOccupation varchar,
	SpanishOccupation varchar,
	FrenchOccupation varchar,
	HouseOwnerFlag varchar,
	NumberCarsOwned integer,
	AddressLine1 varchar,
	AddressLine2 varchar,
	Phone varchar,
	DateFirstPurchase date,
	CommuteDistance varchar,
  constraint FK_DimCustomer_DimGeography foreign key(GeographyKey) references DimGeography (GeographyKey)
);


create table DimDate(
	DateKey integer not null primary key,
	FullDateAlternateKey date,
	DayNumberOfWeek integer,
	EnglishDayNameOfWeek varchar,
	SpanishDayNameOfWeek varchar,
	FrenchDayNameOfWeek varchar,
	DayNumberOfMonth integer,
	DayNumberOfYear integer,
	WeekNumberOfYear integer,
	EnglishMonthName varchar,
	SpanishMonthName varchar,
	FrenchMonthName varchar,
	MonthNumberOfYear integer,
	CalendarQuarter integer,
	CalendarYear integer,
	CalendarSemester integer,
	FiscalQuarter integer,
	FiscalYear integer,
	FiscalSemester integer
);


create table DimDepartmentGroup(
	DepartmentGroupKey integer not null primary key,
	ParentDepartmentGroupKey integer,
	DepartmentGroupName varchar,
  constraint FK_DimDepartmentGroup_DimDepartmentGroup foreign key (ParentDepartmentGroupKey) references DimDepartmentGroup (DepartmentGroupKey)
);


create table DimEmployee(
	EmployeeKey integer not null primary key,
	ParentEmployeeKey integer,
	EmployeeNationalIDAlternateKey varchar,
	ParentEmployeeNationalIDAlternateKey varchar,
	SalesTerritoryKey integer,
	FirstName varchar,
	LastName varchar,
	MiddleName varchar,
	NameStyle bit,
	Title varchar,
	HireDate date,
	BirthDate date,
	LoginID varchar,
	EmailAddress varchar,
	Phone varchar,
	MaritalStatus varchar,
	EmergencyContactName varchar,
	EmergencyContactPhone varchar,
	SalariedFlag bit,
	Gender varchar,
	PayFrequency integer,
	BaseRate decimal(13,2),
	VacationHours integer,
	SickLeaveHours integer,
	CurrentFlag bit,
	SalesPersonFlag bit,
	DepartmentName varchar,
	StartDate date,
	EndDate date,
	Status varchar,
	EmployeePhoto varchar,
  constraint FK_DimEmployee_DimEmployee foreign key (ParentEmployeeKey) references DimEmployee (EmployeeKey),
  constraint FK_DimEmployee_DimSalesTerritory foreign key (SalesTerritoryKey) references DimSalesTerritory (SalesTerritoryKey),

);


create table DimOrganization(
	OrganizationKey integer not null primary key,
	ParentOrganizationKey integer,
	PercentageOfOwnership varchar,
	OrganizationName varchar,
	CurrencyKey integer,
  constraint FK_DimOrganization_DimCurrency foreign key (CurrencyKey) references DimCurrency (CurrencyKey),
  constraint FK_DimOrganization_DimOrganization foreign key (ParentOrganizationKey)references DimOrganization (OrganizationKey)
);


create table DimProductCategory(
	ProductCategoryKey integer not null primary key,
	ProductCategoryAlternateKey integer,
	EnglishProductCategoryName varchar,
	SpanishProductCategoryName varchar,
	FrenchProductCategoryName varchar
);


create table DimProductSubcategory(
	ProductSubcategoryKey integer not null primary key,
	ProductSubcategoryAlternateKey integer,
	EnglishProductSubcategoryName varchar,
	SpanishProductSubcategoryName varchar,
	FrenchProductSubcategoryName varchar,
	ProductCategoryKey integer,
  constraint FK_DimProductSubcategory_DimProductCategory foreign key (ProductCategoryKey) references DimProductCategory (ProductCategoryKey)
);


create table DimProduct(
	ProductKey integer not null primary key,
	ProductAlternateKey varchar,
	ProductSubcategoryKey integer,
	WeightUnitMeasureCode varchar,
	SizeUnitMeasureCode varchar,
	EnglishProductName varchar,
	SpanishProductName varchar,
	FrenchProductName varchar,
	StandardCost decimal(13,2),
	FinishedGoodsFlag bit,
	Color varchar,
	SafetyStockLevel integer,
	ReorderPoint integer,
	ListPrice decimal(13,2),
	Size varchar,
	SizeRange varchar,
	Weight float,
	DaysToManufacture integer,
	ProductLine varchar,
	DealerPrice decimal(13,2),
	Class varchar,
	Style varchar,
	ModelName varchar,
	LargePhoto varchar,
	EnglishDescription varchar,
	FrenchDescription varchar,
	ChineseDescription varchar,
	ArabicDescription varchar,
	HebrewDescription varchar,
	ThaiDescription varchar,
	GermanDescription varchar,
	JapaneseDescription varchar,
	TurkishDescription varchar,
	StartDate datetime,
	EndDate datetime,
	Status varchar,
  constraint FK_DimProduct_DimProductSubcategory foreign key (ProductSubcategoryKey) references DimProductSubcategory (ProductSubcategoryKey)
);


create table DimPromotion(
	PromotionKey integer not null primary key,
	PromotionAlternateKey integer,
	EnglishPromotionName varchar,
	SpanishPromotionName varchar,
	FrenchPromotionName varchar,
	DiscountPct float,
	EnglishPromotionType varchar,
	SpanishPromotionType varchar,
	FrenchPromotionType varchar,
	EnglishPromotionCategory varchar,
	SpanishPromotionCategory varchar,
	FrenchPromotionCategory varchar,
	StartDate datetime,
	EndDate datetime,
	MinQty integer,
	MaxQty integer
);


create table DimReseller(
	ResellerKey integer not null primary key,
	GeographyKey integer,
	ResellerAlternateKey varchar,
	Phone varchar,
	BusinessType varchar(20),
	ResellerName varchar,
	NumberEmployees integer,
	OrderFrequency char(1),
	OrderMonth integer,
	FirstOrderYear integer,
	LastOrderYear integer,
	ProductLine varchar,
	AddressLine1 varchar,
	AddressLine2 varchar,
	AnnualSales decimal(13,2),
	BankName varchar,
	MinPaymentType integer,
	MinPaymentAmount decimal(13,2),
	AnnualRevenue decimal(13,2),
	YearOpened integer,
  constraint FK_DimReseller_DimGeography foreign key (GeographyKey) references DimGeography (GeographyKey)
);


create table DimSalesReason(
	SalesReasonKey integer not null primary key,
	SalesReasonAlternateKey integer,
	SalesReasonName varchar,
	SalesReasonReasonType varchar
);


create table DimScenario(
	ScenarioKey integer not null primary key,
	ScenarioName varchar
);


create table FactAdditionalInternationalProductDescription(
	ProductKey integer,
	CultureName varchar,
	ProductDescription varchar
);


create table FactCallCenter(
	FactCallCenterID integer,
	DateKey integer,
	WageType varchar,
	Shift varchar,
	LevelOneOperators integer,
	LevelTwoOperators integer,
	TotalOperators integer,
	Calls integer,
	AutomaticResponses integer,
	Orders integer,
	IssuesRaised integer,
	AverageTimePerIssue integer,
	ServiceGrade float,
	Date datetime,
  constraint FK_FactCallCenter_DimDate foreign key (DateKey) references DimDate (DateKey)
);


create table FactCurrencyRate(
	CurrencyKey integer,
	DateKey integer,
	AverageRate float,
	EndOfDayRate float,
	Date datetime,
  constraint FK_FactCurrencyRate_DimDate foreign key (DateKey) references DimDate (DateKey),
  constraint FK_FactCurrencyRate_DimCurrency foreign key (CurrencyKey) references DimCurrency (CurrencyKey)
);


create table FactFinance(
	FinanceKey integer,
	DateKey integer,
	OrganizationKey integer,
	DepartmentGroupKey integer,
	ScenarioKey integer,
	AccountKey integer,
	Amount float,
	Date datetime,
  constraint FK_FactFinance_DimScenario foreign key (ScenarioKey) references DimScenario (ScenarioKey),
  constraint FK_FactFinance_DimOrganization foreign key (OrganizationKey) references DimOrganization (OrganizationKey),
  constraint FK_FactFinance_DimDepartmentGroup foreign key (DepartmentGroupKey) references DimDepartmentGroup (DepartmentGroupKey),
  constraint FK_FactFinance_DimDate foreign key (DateKey) references DimDate (DateKey),
  constraint FK_FactFinance_DimAccount foreign key (AccountKey) references DimAccount (AccountKey)
);


create table FactInternetSales(
	ProductKey integer,
	OrderDateKey integer,
	DueDateKey integer,
	ShipDateKey integer,
	CustomerKey integer,
	PromotionKey integer,
	CurrencyKey integer,
	SalesTerritoryKey integer,
	SalesOrderNumber varchar,
	SalesOrderLineNumber integer,
	RevisionNumber integer,
	OrderQuantity integer,
	UnitPrice decimal(13,2),
	ExtendedAmount decimal(13,2),
	UnitPriceDiscountPct float,
	DiscountAmount float,
	ProductStandardCost decimal(13,2),
	TotalProductCost decimal(13,2),
	SalesAmount decimal(13,2),
	TaxAmt decimal(13,2),
	Freight decimal(13,2),
	CarrierTrackingNumber varchar,
	CustomerPONumber varchar,
	OrderDate datetime,
	DueDate datetime,
	ShipDate datetime,
  constraint pk_FactInternetSales primary key (SalesOrderNumber, SalesOrderLineNumber),
  constraint FK_FactInternetSales_DimCurrency foreign key (CurrencyKey) references DimCurrency (CurrencyKey),
  constraint FK_FactInternetSales_DimCustomer foreign key (CustomerKey) references DimCustomer (CustomerKey),
  constraint FK_FactInternetSales_DimDate foreign key (OrderDateKey) references DimDate (DateKey),
  constraint FK_FactInternetSales_DimDate1 foreign key (DueDateKey) references DimDate (DateKey),
  constraint FK_FactInternetSales_DimDate2 foreign key (ShipDateKey) references DimDate (DateKey),
  constraint FK_FactInternetSales_DimProduct foreign key (ProductKey) references DimProduct (ProductKey),
  constraint FK_FactInternetSales_DimPromotion foreign key (PromotionKey) references DimPromotion (PromotionKey),
  constraint FK_FactInternetSales_DimSalesTerritory foreign key (SalesTerritoryKey) references DimSalesTerritory 
);


create table FactInternetSalesReason(
	SalesOrderNumber varchar,
	SalesOrderLineNumber integer,
	SalesReasonKey integer,
  constraint FK_FactInternetSalesReason_FactInternetSales foreign key (SalesOrderNumber, SalesOrderLineNumber) references FactInternetSales (SalesOrderNumber, SalesOrderLineNumber),
  constraint FK_FactInternetSalesReason_DimSalesReason foreign key (SalesReasonKey) references DimSalesReason (SalesReasonKey)
);


create table FactProductInventory(
	ProductKey integer,
	DateKey integer,
	MovementDate date,
	UnitCost decimal(13,2),
	UnitsIn integer,
	UnitsOut integer,
	UnitsBalance integer,
  constraint FK_FactProductInventory_DimDate foreign key (DateKey)references DimDate (DateKey),
  constraint FK_FactProductInventory_DimProduct foreign key (ProductKey) references DimProduct (ProductKey)
);


create table FactResellerSales(
	ProductKey integer,
	OrderDateKey integer,
	DueDateKey integer,
	ShipDateKey integer,
	ResellerKey integer,
	EmployeeKey integer,
	PromotionKey integer,
	CurrencyKey integer,
	SalesTerritoryKey integer,
	SalesOrderNumber varchar,
	SalesOrderLineNumber integer,
	RevisionNumber integer,
	OrderQuantity integer,
	UnitPrice decimal(13,2),
	ExtendedAmount decimal(13,2),
	UnitPriceDiscountPct float,
	DiscountAmount float,
	ProductStandardCost decimal(13,2),
	TotalProductCost decimal(13,2),
	SalesAmount decimal(13,2),
	TaxAmt decimal(13,2),
	Freight decimal(13,2),
	CarrierTrackingNumber varchar,
	CustomerPONumber varchar,
	OrderDate datetime,
	DueDate datetime,
	ShipDate datetime,
  constraint FK_FactResellerSales_DimCurrency foreign key(CurrencyKey) references DimCurrency (CurrencyKey),
  constraint FK_FactResellerSales_DimDate foreign key(OrderDateKey) references DimDate (DateKey),
  constraint FK_FactResellerSales_DimDate1 foreign key(DueDateKey) references DimDate (DateKey),
  constraint FK_FactResellerSales_DimDate2 foreign key(ShipDateKey) references DimDate (DateKey),
  constraint FK_FactResellerSales_DimEmployee foreign key(EmployeeKey) references DimEmployee (EmployeeKey),
  constraint FK_FactResellerSales_DimProduct foreign key(ProductKey) references DimProduct (ProductKey),
  constraint FK_FactResellerSales_DimPromotion foreign key(PromotionKey) references DimPromotion (PromotionKey),
  constraint FK_FactResellerSales_DimReseller foreign key(ResellerKey) references DimReseller (ResellerKey),
  constraint FK_FactResellerSales_DimSalesTerritory foreign key(SalesTerritoryKey) references DimSalesTerritory (SalesTerritoryKey)
);


create table FactSalesQuota(
	SalesQuotaKey integer,
	EmployeeKey integer,
	DateKey integer,
	CalendarYear integer,
	CalendarQuarter integer,
	SalesAmountQuota decimal(13,2),
	Date datetime,
  constraint FK_FactSalesQuota_DimEmployee foreign key(EmployeeKey) references DimEmployee (EmployeeKey),
  constraint FK_FactSalesQuota_DimDate foreign key(DateKey) references DimDate (DateKey)
);


create table FactSurveyResponse(
	SurveyResponseKey integer,
	DateKey integer,
	CustomerKey integer,
	ProductCategoryKey integer,
	EnglishProductCategoryName varchar,
	ProductSubcategoryKey integer,
	EnglishProductSubcategoryName varchar,
	Date datetime,
  constraint FK_FactSurveyResponse_DateKey foreign key(DateKey) references DimDate (DateKey),
	constraint FK_FactSurveyResponse_CustomerKey foreign key(CustomerKey) references DimCustomer (CustomerKey)
);


create table NewFactCurrencyRate(
	AverageRate real,
	CurrencyID varchar,
	CurrencyDate date,
	EndOfDayRate real,
	CurrencyKey integer,
	DateKey integer
);


create table ProspectiveBuyer(
	ProspectiveBuyerKey integer,
	ProspectAlternateKey varchar,
	FirstName varchar,
	MiddleName varchar,
	LastName varchar,
	BirthDate datetime,
	MaritalStatus varchar,
	Gender varchar,
	EmailAddress varchar,
	YearlyIncome decimal(13,2),
	TotalChildren integer,
	NumberChildrenAtHome integer,
	Education varchar,
	Occupation varchar,
	HouseOwnerFlag varchar,
	NumberCarsOwned integer,
	AddressLine1 varchar,
	AddressLine2 varchar,
	City varchar,
	StateProvinceCode varchar,
	PostalCode varchar,
	Phone varchar,
	Salutation varchar,
	Unknown integer
);