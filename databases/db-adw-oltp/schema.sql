CREATE TABLE PhoneNumberType (
PhoneNumberTypeID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE UnitMeasure (
UnitMeasureCode TEXT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Currency (
CurrencyCode TEXT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Shift (
ShiftID UTINYINT NOT NULL primary key, 
Name TEXT NOT NULL, 
StartTime TIME NOT NULL, 
EndTime TIME NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE ScrapReason (
ScrapReasonID SMALLINT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Culture (
CultureID TEXT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Department (
DepartmentID SMALLINT NOT NULL primary key, 
Name TEXT NOT NULL, 
GroupName TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Location (
LocationID SMALLINT NOT NULL primary key, 
Name TEXT NOT NULL, 
CostRate Decimal(18,4) NOT NULL, 
Availability DECIMAL(8, 2) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE ShipMethod (
ShipMethodID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
ShipBase DECIMAL(18,4) NOT NULL, 
ShipRate DECIMAL(18,4) NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE SalesReason (
SalesReasonID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
ReasonType TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);
CREATE TABLE ProductDescription (
ProductDescriptionID INT NOT NULL primary key, 
Description TEXT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE ProductModel (
ProductModelID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
CatalogDescription TEXT NULL, 
Instructions TEXT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE ProductModelProductDescriptionCulture (
ProductModelID INT NOT NULL, 
ProductDescriptionID INT NOT NULL, 
CultureID TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (ProductModelID, ProductDescriptionID, CultureID),
CONSTRAINT FK_ProductModelProductDescriptionCulture_ProductDescription_ProductDescriptionID FOREIGN KEY (ProductDescriptionID) REFERENCES ProductDescription (ProductDescriptionID), 
CONSTRAINT FK_ProductModelProductDescriptionCulture_Culture_CultureID FOREIGN KEY (CultureID) REFERENCES Culture (CultureID), 
CONSTRAINT FK_ProductModelProductDescriptionCulture_ProductModel_ProductModelID FOREIGN KEY (ProductModelID) REFERENCES ProductModel (ProductModelID)
);

CREATE TABLE CreditCard (
CreditCardID INT NOT NULL primary key, 
CardType TEXT NOT NULL, 
CardNumber TEXT NOT NULL, 
ExpMonth UTINYINT NOT NULL, 
ExpYear SMALLINT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE CurrencyRate (
CurrencyRateID INT NOT NULL primary key, 
CurrencyRateDate TIMESTAMP NOT NULL, 
FromCurrencyCode TEXT NOT NULL, 
ToCurrencyCode TEXT NOT NULL, 
AverageRate DECIMAL(18,4) NOT NULL, 
EndOfDayRate DECIMAL(18,4) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_CurrencyRate_Currency_FromCurrencyCode FOREIGN KEY (FromCurrencyCode) REFERENCES Currency (CurrencyCode), 
CONSTRAINT FK_CurrencyRate_Currency_ToCurrencyCode FOREIGN KEY (ToCurrencyCode) REFERENCES Currency (CurrencyCode)
);

CREATE TABLE CountryRegion (
CountryRegionCode TEXT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE SalesTerritory (
TerritoryID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
CountryRegionCode TEXT NOT NULL, 
Grp TEXT NOT NULL, 
SalesYTD DECIMAL(18,4) NOT NULL, 
SalesLastYear DECIMAL(18,4) NOT NULL , 
CostYTD DECIMAL(18,4) NOT NULL , 
CostLastYear DECIMAL(18,4) NOT NULL , 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_SalesTerritory_CountryRegion_CountryRegionCode FOREIGN KEY (CountryRegionCode) REFERENCES CountryRegion (CountryRegionCode)
);

CREATE TABLE StateProvince (
StateProvinceID INT NOT NULL primary key, 
StateProvinceCode TEXT NOT NULL, 
CountryRegionCode TEXT NOT NULL, 
IsOnlyStateProvinceFlag BIT NOT NULL , 
Name TEXT NOT NULL, 
TerritoryID INT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_StateProvince_CountryRegion_CountryRegionCode FOREIGN KEY (CountryRegionCode) REFERENCES CountryRegion (CountryRegionCode), 
CONSTRAINT FK_StateProvince_SalesTerritory_TerritoryID FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory (TerritoryID)
);


CREATE TABLE SalesTaxRate (
SalesTaxRateID INT NOT NULL primary key, 
StateProvinceID INT NOT NULL, 
TaxType UTINYINT NOT NULL, 
TaxRate DECIMAL(8, 4) NOT NULL,
Name TEXT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
CONSTRAINT FK_SalesTaxRate_StateProvince_StateProvinceID FOREIGN KEY (StateProvinceID) REFERENCES StateProvince (StateProvinceID)
);

CREATE TABLE ContactType (
ContactTypeID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE BusinessEntity (
BusinessEntityID INT NOT NULL primary key, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Vendor (
BusinessEntityID INT NOT NULL primary key, 
AccountNumber TEXT NOT NULL, 
Name TEXT NOT NULL, 
CreditRating UTINYINT NOT NULL, 
PreferredVendorStatus BIT NOT NULL, 
ActiveFlag BIT NOT NULL , 
PurchasingWebServiceURL TEXT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_Vendor_BusinessEntity_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES BusinessEntity (BusinessEntityID)
);

CREATE TABLE Person (
BusinessEntityID INT NOT NULL primary key, 
PersonType TEXT NOT NULL, 
NameStyle BIT NOT NULL, 
Title TEXT NULL, 
FirstName TEXT NOT NULL, 
MiddleName TEXT NULL, 
LastName TEXT NOT NULL, 
Suffix TEXT NULL, 
EmailPromotion INT NOT NULL, 
AdditionalContactInfo TEXT NULL, 
Demographics TEXT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
CONSTRAINT FK_Person_BusinessEntity_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES BusinessEntity (BusinessEntityID)
);

CREATE TABLE PersonCreditCard (
BusinessEntityID INT NOT NULL, 
CreditCardID INT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (BusinessEntityID, CreditCardID),
CONSTRAINT FK_PersonCreditCard_Person_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Person (BusinessEntityID), 
CONSTRAINT FK_PersonCreditCard_CreditCard_CreditCardID FOREIGN KEY (CreditCardID) REFERENCES CreditCard (CreditCardID)
); 

CREATE TABLE Password (
BusinessEntityID INT NOT NULL primary key, 
PasswordHash TEXT NOT NULL, 
PasswordSalt TEXT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_Password_Person_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Person (BusinessEntityID)
);

CREATE TABLE PersonPhone (
BusinessEntityID INT NOT NULL, 
PhoneNumber TEXT NOT NULL, 
PhoneNumberTypeID INT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (BusinessEntityID, PhoneNumber, PhoneNumberTypeID),
CONSTRAINT FK_PersonPhone_Person_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Person (BusinessEntityID), 
CONSTRAINT FK_PersonPhone_PhoneNumberType_PhoneNumberTypeID FOREIGN KEY (PhoneNumberTypeID) REFERENCES PhoneNumberType (PhoneNumberTypeID)
); 

CREATE TABLE Employee (
BusinessEntityID INT NOT NULL primary key, 
NationalIDNumber TEXT NOT NULL, 
LoginID TEXT NOT NULL, 
OrganizationNode TEXT NULL, 
OrganizationLevel INT, 
JobTitle TEXT NOT NULL, 
BirthDate DATE NOT NULL, 
MaritalStatus TEXT NOT NULL, 
Gender TEXT NOT NULL, 
HireDate DATE NOT NULL, 
SalariedFlag BIT NOT NULL , 
VacationHours SMALLINT NOT NULL, 
SickLeaveHours SMALLINT NOT NULL, 
CurrentFlag BIT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_Employee_Person_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Person (BusinessEntityID)
);

CREATE TABLE EmployeeDepartmentHistory (
BusinessEntityID INT NOT NULL, 
DepartmentID SMALLINT NOT NULL, 
ShiftID UTINYINT NOT NULL, 
StartDate DATE NOT NULL, 
EndDate DATE NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (BusinessEntityID, StartDate, DepartmentID, ShiftID),
CONSTRAINT FK_EmployeeDepartmentHistory_Department_DepartmentID FOREIGN KEY (DepartmentID) REFERENCES Department (DepartmentID), 
CONSTRAINT FK_EmployeeDepartmentHistory_Employee_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Employee (BusinessEntityID), 
CONSTRAINT FK_EmployeeDepartmentHistory_Shift_ShiftID FOREIGN KEY (ShiftID) REFERENCES Shift (ShiftID)
);

CREATE TABLE EmployeePayHistory (
BusinessEntityID INT NOT NULL, 
RateChangeDate TIMESTAMP NOT NULL, 
Rate DECIMAL(18,4) NOT NULL, 
PayFrequency UTINYINT NOT NULL, /* 1 = monthly salary, 2 = biweekly salary */
ModifiedDate TIMESTAMP NOT NULL, 
primary key (BusinessEntityID, RateChangeDate),
CONSTRAINT FK_EmployeePayHistory_Employee_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Employee (BusinessEntityID)
);

CREATE TABLE EmailAddress (
BusinessEntityID INT NOT NULL, 
EmailAddressID INT NOT NULL, 
EmailAddress TEXT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (BusinessEntityID, EmailAddressID),
CONSTRAINT FK_EmailAddress_Person_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Person (BusinessEntityID)
);

CREATE TABLE BusinessEntityContact (
BusinessEntityID INT NOT NULL, 
PersonID INT NOT NULL, 
ContactTypeID INT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (BusinessEntityID, PersonID, ContactTypeID),
CONSTRAINT FK_BusinessEntityContact_Person_PersonID FOREIGN KEY (PersonID) REFERENCES Person (BusinessEntityID), 
CONSTRAINT FK_BusinessEntityContact_ContactType_ContactTypeID FOREIGN KEY (ContactTypeID) REFERENCES ContactType (ContactTypeID), 
CONSTRAINT FK_BusinessEntityContact_BusinessEntity_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES BusinessEntity (BusinessEntityID)
);

CREATE TABLE AddressType (
AddressTypeID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE Address (
AddressID INT NOT NULL primary key, 
AddressLine1 TEXT NOT NULL, 
AddressLine2 TEXT NULL, 
City TEXT NOT NULL, 
StateProvinceID INT NOT NULL, 
PostalCode TEXT NOT NULL, 
SpatialLocation TEXT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE BusinessEntityAddress (
BusinessEntityID INT NOT NULL, 
AddressID INT NOT NULL, 
AddressTypeID INT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (BusinessEntityID, AddressID, AddressTypeID),
CONSTRAINT FK_BusinessEntityAddress_Address_AddressID FOREIGN KEY (AddressID) REFERENCES Address (AddressID), 
CONSTRAINT FK_BusinessEntityAddress_AddressType_AddressTypeID FOREIGN KEY (AddressTypeID) REFERENCES AddressType (AddressTypeID), 
CONSTRAINT FK_BusinessEntityAddress_BusinessEntity_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES BusinessEntity (BusinessEntityID)
);

CREATE TABLE CountryRegionCurrency (
CountryRegionCode TEXT NOT NULL, 
CurrencyCode TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (CountryRegionCode, CurrencyCode),
CONSTRAINT FK_CountryRegionCurrency_CountryRegion_CountryRegionCode FOREIGN KEY (CountryRegionCode) REFERENCES CountryRegion (CountryRegionCode), 
CONSTRAINT FK_CountryRegionCurrency_Currency_CurrencyCode FOREIGN KEY (CurrencyCode) REFERENCES Currency (CurrencyCode)
);

CREATE TABLE ProductCategory (
ProductCategoryID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE ProductSubcategory (
ProductSubcategoryID INT NOT NULL primary key, 
ProductCategoryID INT NOT NULL, 
Name TEXT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_ProductSubcategory_ProductCategory_ProductCategoryID FOREIGN KEY (ProductCategoryID) REFERENCES ProductCategory (ProductCategoryID)
);

CREATE TABLE Product (
ProductID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
ProductNumber TEXT NOT NULL, 
MakeFlag BIT NOT NULL , 
FinishedGoodsFlag BIT NOT NULL, 
Color TEXT NULL, 
SafetyStockLevel SMALLINT NOT NULL, 
ReorderPoint SMALLINT NOT NULL, 
StandardCost DECIMAL(18,4) NOT NULL, 
ListPrice DECIMAL(18,4) NOT NULL, 
Size TEXT NULL, 
SizeUnitMeasureCode TEXT NULL, 
WeightUnitMeasureCode TEXT NULL, 
Weight DECIMAL(8, 2) NULL, 
DaysToManufacture INT NOT NULL, 
ProductLine TEXT NULL, 
Class TEXT NULL, 
Style TEXT NULL, 
ProductSubcategoryID INT NULL, 
ProductModelID INT NULL, 
SellStartDate TIMESTAMP NOT NULL, 
SellEndDate TIMESTAMP NULL, 
DiscontinuedDate TIMESTAMP NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_Product_UnitMeasure_SizeUnitMeasureCode FOREIGN KEY (SizeUnitMeasureCode) REFERENCES UnitMeasure (UnitMeasureCode), 
CONSTRAINT FK_Product_UnitMeasure_WeightUnitMeasureCode FOREIGN KEY (WeightUnitMeasureCode) REFERENCES UnitMeasure (UnitMeasureCode), 
CONSTRAINT FK_Product_ProductModel_ProductModelID FOREIGN KEY (ProductModelID) REFERENCES ProductModel (ProductModelID), 
CONSTRAINT FK_Product_ProductSubcategory_ProductSubcategoryID FOREIGN KEY (ProductSubcategoryID) REFERENCES ProductSubcategory (ProductSubcategoryID)
);

CREATE TABLE ProductVendor (
ProductID INT NOT NULL, 
BusinessEntityID INT NOT NULL, 
AverageLeadTime INT NOT NULL, 
StandardPrice DECIMAL(18,4) NOT NULL, 
LastReceiptCost DECIMAL(18,4) NULL, 
LastReceiptDate TIMESTAMP NULL, 
MinOrderQty INT NOT NULL, 
MaxOrderQty INT NOT NULL, 
OnOrderQty INT NULL, 
UnitMeasureCode TEXT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (ProductID, BusinessEntityID),
CONSTRAINT FK_ProductVendor_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID), 
CONSTRAINT FK_ProductVendor_UnitMeasure_UnitMeasureCode FOREIGN KEY (UnitMeasureCode) REFERENCES UnitMeasure (UnitMeasureCode), 
CONSTRAINT FK_ProductVendor_Vendor_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Vendor (BusinessEntityID)
);

CREATE TABLE ProductInventory (
ProductID INT NOT NULL, 
LocationID SMALLINT NOT NULL, 
Shelf TEXT NOT NULL, 
Bin UTINYINT NOT NULL, 
Quantity SMALLINT NOT NULL , 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (ProductID, LocationID),
CONSTRAINT FK_ProductInventory_Location_LocationID FOREIGN KEY (LocationID) REFERENCES Location (LocationID), 
CONSTRAINT FK_ProductInventory_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
); 

CREATE TABLE ProductCostHistory (
ProductID INT NOT NULL, 
StartDate TIMESTAMP NOT NULL, 
EndDate TIMESTAMP NULL, 
StandardCost DECIMAL(18,4) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (ProductID, StartDate),
CONSTRAINT FK_ProductCostHistory_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
); 

CREATE TABLE ProductListPriceHistory (
ProductID INT NOT NULL, 
StartDate TIMESTAMP NOT NULL, 
EndDate TIMESTAMP NULL, 
ListPrice DECIMAL(18,4) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (ProductID, StartDate),
CONSTRAINT FK_ProductListPriceHistory_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
);

CREATE TABLE TransactionHistory (
TransactionID INT NOT NULL, 
ProductID INT NOT NULL, 
ReferenceOrderID INT NOT NULL, 
ReferenceOrderLineID INT NOT NULL , 
TransactionDate TIMESTAMP NOT NULL, 
TransactionType TEXT NOT NULL, 
Quantity INT NOT NULL, 
ActualCost DECIMAL(18, 4) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (TransactionID),
CONSTRAINT FK_TransactionHistory_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
);

CREATE TABLE TransactionHistoryArchive (
TransactionID INT NOT NULL primary key, 
ProductID INT NOT NULL, 
ReferenceOrderID INT NOT NULL, 
ReferenceOrderLineID INT NOT NULL CONSTRAINT DF_TransactionHistoryArchive_ReferenceOrderLineID DEFAULT (0), 
TransactionDate TIMESTAMP NOT NULL, 
TransactionType TEXT NOT NULL, 
Quantity INT NOT NULL, 
ActualCost DECIMAL(18, 4) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_TransactionHistoryArchive_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID),

);

CREATE TABLE SpecialOffer (
SpecialOfferID INT NOT NULL primary key, 
Description TEXT NOT NULL, 
DiscountPct DECIMAL(18,4) NOT NULL , 
Type TEXT NOT NULL, 
Category TEXT NOT NULL, 
StartDate TIMESTAMP NOT NULL, 
EndDate TIMESTAMP NOT NULL, 
MinQty INT NOT NULL, 
MaxQty INT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL
);

CREATE TABLE SpecialOfferProduct (
SpecialOfferID INT NOT NULL, 
ProductID INT NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (SpecialOfferID, ProductID),
CONSTRAINT FK_SpecialOfferProduct_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID), 
CONSTRAINT FK_SpecialOfferProduct_SpecialOffer_SpecialOfferID FOREIGN KEY (SpecialOfferID) REFERENCES SpecialOffer (SpecialOfferID)
);

CREATE TABLE ShoppingCartItem (
ShoppingCartItemID INT NOT NULL primary key, 
ShoppingCartID TEXT NOT NULL, 
Quantity INT NOT NULL CONSTRAINT DF_ShoppingCartItem_Quantity DEFAULT (1), 
ProductID INT NOT NULL, 
DateCreated TIMESTAMP NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
CONSTRAINT FK_ShoppingCartItem_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID)
);

CREATE TABLE BillOfMaterials (
BillOfMaterialsID INT NOT NULL primary key, 
ProductAssemblyID INT NULL, 
ComponentID INT NOT NULL, 
StartDate TIMESTAMP NOT NULL, 
EndDate TIMESTAMP NULL, 
UnitMeasureCode TEXT NOT NULL, 
BOMLevel SMALLINT NOT NULL, 
PerAssemblyQty DECIMAL(8, 2) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
CONSTRAINT FK_BillOfMaterials_Product_ProductAssemblyID FOREIGN KEY (ProductAssemblyID) REFERENCES Product (ProductID), 
CONSTRAINT FK_BillOfMaterials_Product_ComponentID FOREIGN KEY (ComponentID) REFERENCES Product (ProductID), 
CONSTRAINT FK_BillOfMaterials_UnitMeasure_UnitMeasureCode FOREIGN KEY (UnitMeasureCode) REFERENCES UnitMeasure (UnitMeasureCode)
);


CREATE TABLE SalesPerson (
BusinessEntityID INT NOT NULL primary key, 
TerritoryID INT NULL, 
SalesQuota DECIMAL(18,4) NULL, 
Bonus DECIMAL(18,4) NOT NULL , 
CommissionPct DECIMAL(18,4) NOT NULL , 
SalesYTD DECIMAL(18,4) NOT NULL , 
SalesLastYear DECIMAL(18,4) NOT NULL , 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_SalesPerson_Employee_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES Employee (BusinessEntityID), 
CONSTRAINT FK_SalesPerson_SalesTerritory_TerritoryID FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory (TerritoryID)
);

CREATE TABLE Store (
BusinessEntityID INT NOT NULL primary key, 
Name TEXT NOT NULL, 
SalesPersonID INT NULL, 
Demographics TEXT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_Store_BusinessEntity_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES BusinessEntity (BusinessEntityID), 
CONSTRAINT FK_Store_SalesPerson_SalesPersonID FOREIGN KEY (SalesPersonID) REFERENCES SalesPerson (BusinessEntityID)
);

CREATE TABLE SalesTerritoryHistory (
BusinessEntityID INT NOT NULL /* A sales person */, 
TerritoryID INT NOT NULL, 
StartDate TIMESTAMP NOT NULL, 
EndDate TIMESTAMP NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (BusinessEntityID, StartDate, TerritoryID),
CONSTRAINT FK_SalesTerritoryHistory_SalesPerson_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES SalesPerson (BusinessEntityID), 
CONSTRAINT FK_SalesTerritoryHistory_SalesTerritory_TerritoryID FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory (TerritoryID)
);

CREATE TABLE SalesPersonQuotaHistory (
BusinessEntityID INT NOT NULL, 
QuotaDate TIMESTAMP NOT NULL, 
SalesQuota DECIMAL(18,4) NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (BusinessEntityID, QuotaDate),
CONSTRAINT FK_SalesPersonQuotaHistory_SalesPerson_BusinessEntityID FOREIGN KEY (BusinessEntityID) REFERENCES SalesPerson (BusinessEntityID)
);

/* A customer may either be a person, a store, or a person who works for a store */
/* If this customer represents a person, this is non-null */
/* If the customer is a store, or is associated with a store then this is non-null. */
CREATE TABLE Customer (
CustomerID INT NOT NULL primary key, 
PersonID  INT NULL, 
StoreID INT NULL, 
TerritoryID INT NULL, 
AccountNumber TEXT, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL,
CONSTRAINT FK_Customer_Person_PersonID FOREIGN KEY (PersonID) REFERENCES Person (BusinessEntityID), 
CONSTRAINT FK_Customer_Store_StoreID FOREIGN KEY (StoreID) REFERENCES Store (BusinessEntityID), 
CONSTRAINT FK_Customer_SalesTerritory_TerritoryID FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory (TerritoryID)
);

/* 1 = Pending;
 2 = Approved;
 3 = Rejected;
 4 = Complete */
CREATE TABLE PurchaseOrderHeader (
PurchaseOrderID INT NOT NULL primary key, 
RevisionNumber UTINYINT NOT NULL, 
Status UTINYINT NOT NULL, 
EmployeeID INT NOT NULL, 
VendorID INT NOT NULL, 
ShipMethodID INT NOT NULL, 
OrderDate TIMESTAMP NOT NULL, 
ShipDate TIMESTAMP NULL, 
SubTotal DECIMAL(18,4) NOT NULL , 
TaxAmt DECIMAL(18,4) NOT NULL , 
Freight DECIMAL(18,4) NOT NULL , 
TotalDue DECIMAL(18,4) NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
);

CREATE TABLE PurchaseOrderDetail (
PurchaseOrderID INT NOT NULL, 
PurchaseOrderDetailID INT NOT NULL, 
DueDate TIMESTAMP NOT NULL, 
OrderQty SMALLINT NOT NULL, 
ProductID INT NOT NULL, 
UnitPrice DECIMAL(18,4) NOT NULL, 
LineTotal DECIMAL(18,4), 
ReceivedQty DECIMAL(8,2) NOT NULL, 
RejectedQty DECIMAL(8,2) NOT NULL, 
StockedQty DECIMAL(8,2), 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (PurchaseOrderID, PurchaseOrderDetailID),
CONSTRAINT FK_PurchaseOrderDetail_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID), 
CONSTRAINT FK_PurchaseOrderDetail_PurchaseOrderHeader_PurchaseOrderID FOREIGN KEY (PurchaseOrderID) REFERENCES PurchaseOrderHeader (PurchaseOrderID)
);

CREATE TABLE SalesOrderHeader (
SalesOrderID INT NOT NULL primary key, 
RevisionNumber UTINYINT NOT NULL , 
OrderDate TIMESTAMP NOT NULL, 
DueDate TIMESTAMP NOT NULL, 
ShipDate TIMESTAMP NULL, 
Status UTINYINT NOT NULL , 
OnlineOrderFlag BIT NOT NULL , 
SalesOrderNumber TEXT NOT NULL, 
PurchaseOrderNumber TEXT NULL, 
AccountNumber TEXT NULL, 
CustomerID INT NOT NULL, 
SalesPersonID INT NULL, 
TerritoryID INT NULL, 
BillToAddressID INT NOT NULL, 
ShipToAddressID INT NOT NULL, 
ShipMethodID INT NOT NULL, 
CreditCardID INT NULL, 
CreditCardApprovalCode TEXT NULL, 
CurrencyRateID INT NULL, 
SubTotal DECIMAL(18,4) NOT NULL , 
TaxAmt DECIMAL(18,4) NOT NULL , 
Freight DECIMAL(18,4) NOT NULL , 
TotalDue DECIMAL(18,4) NOT NULL, 
Comment TEXT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
CONSTRAINT FK_SalesOrderHeader_Address_BillToAddressID FOREIGN KEY (BillToAddressID) REFERENCES Address (AddressID), 
CONSTRAINT FK_SalesOrderHeader_Address_ShipToAddressID FOREIGN KEY (ShipToAddressID) REFERENCES Address (AddressID), 
CONSTRAINT FK_SalesOrderHeader_CreditCard_CreditCardID FOREIGN KEY (CreditCardID) REFERENCES CreditCard (CreditCardID), 
CONSTRAINT FK_SalesOrderHeader_CurrencyRate_CurrencyRateID FOREIGN KEY (CurrencyRateID) REFERENCES CurrencyRate (CurrencyRateID), 
CONSTRAINT FK_SalesOrderHeader_Customer_CustomerID FOREIGN KEY (CustomerID) REFERENCES Customer (CustomerID), 
CONSTRAINT FK_SalesOrderHeader_SalesPerson_SalesPersonID FOREIGN KEY (SalesPersonID) REFERENCES SalesPerson (BusinessEntityID), 
CONSTRAINT FK_SalesOrderHeader_ShipMethod_ShipMethodID FOREIGN KEY (ShipMethodID) REFERENCES ShipMethod (ShipMethodID), 
CONSTRAINT FK_SalesOrderHeader_SalesTerritory_TerritoryID FOREIGN KEY (TerritoryID) REFERENCES SalesTerritory (TerritoryID)
);

CREATE TABLE SalesOrderDetail (
SalesOrderID INT NOT NULL, 
SalesOrderDetailID INT NOT NULL, 
CarrierTrackingNumber TEXT NULL, 
OrderQty SMALLINT NOT NULL, 
ProductID INT NOT NULL, 
SpecialOfferID INT NOT NULL, 
UnitPrice DECIMAL(18,4) NOT NULL, 
UnitPriceDiscount DECIMAL(18,4) NOT NULL , 
LineTotal DECIMAL(18,4) NOT NULL, 
rowguid TEXT, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (SalesOrderID, SalesOrderDetailID),
CONSTRAINT FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeader (SalesOrderID), 
CONSTRAINT FK_SalesOrderDetail_SpecialOfferProduct_SpecialOfferIDProductID FOREIGN KEY (SpecialOfferID, ProductID) REFERENCES SpecialOfferProduct (SpecialOfferID, ProductID)
);

CREATE TABLE SalesOrderHeaderSalesReason (
SalesOrderID INT NOT NULL, 
SalesReasonID INT NOT NULL, 
ModifiedDate TIMESTAMP NOT NULL,
primary key (SalesOrderID, SalesReasonID),
CONSTRAINT FK_SalesOrderHeaderSalesReason_SalesOrderHeader_SalesOrderID FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeader (SalesOrderID), 
CONSTRAINT FK_SalesOrderHeaderSalesReason_SalesReason_SalesReasonID FOREIGN KEY (SalesReasonID) REFERENCES SalesReason (SalesReasonID)
);

CREATE TABLE WorkOrder (
WorkOrderID INT NOT NULL primary key, 
ProductID INT NOT NULL, 
OrderQty INT NOT NULL, 
StockedQty INT NOT NULL, 
ScrappedQty SMALLINT NOT NULL, 
StartDate TIMESTAMP NOT NULL, 
EndDate TIMESTAMP NULL, 
DueDate TIMESTAMP NOT NULL, 
ScrapReasonID SMALLINT NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
CONSTRAINT FK_WorkOrder_Product_ProductID FOREIGN KEY (ProductID) REFERENCES Product (ProductID), 
CONSTRAINT FK_WorkOrder_ScrapReason_ScrapReasonID FOREIGN KEY (ScrapReasonID) REFERENCES ScrapReason (ScrapReasonID)
);

CREATE TABLE WorkOrderRouting (
WorkOrderID INT NOT NULL, 
ProductID INT NOT NULL, 
OperationSequence SMALLINT NOT NULL, 
LocationID SMALLINT NOT NULL, 
ScheduledStartDate TIMESTAMP NOT NULL, 
ScheduledEndDate TIMESTAMP NOT NULL, 
ActualStartDate TIMESTAMP NULL, 
ActualEndDate TIMESTAMP NULL, 
ActualResourceHrs DECIMAL(9, 4) NULL, 
PlannedCost DECIMAL(18, 4) NOT NULL, 
ActualCost DECIMAL(18, 4) NULL, 
ModifiedDate TIMESTAMP NOT NULL, 
primary key (WorkOrderID, ProductID, OperationSequence),
CONSTRAINT FK_WorkOrderRouting_Location_LocationID FOREIGN KEY (LocationID) REFERENCES Location (LocationID), 
CONSTRAINT FK_WorkOrderRouting_WorkOrder_WorkOrderID FOREIGN KEY (WorkOrderID) REFERENCES WorkOrder (WorkOrderID)
); 
