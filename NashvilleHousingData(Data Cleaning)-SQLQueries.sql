--------------------------------------------------------------------------------------------------------------------------

-- Standardize Date Format

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
ADD SaleDateConverted Date;

Update PortfolioProject.dbo.NashvilleHousing
SET SaleDateConverted =	CONVERT(date,SaleDate);

SELECT SaleDate,SaleDateConverted
FROM PortfolioProject..NashvilleHousing

 --------------------------------------------------------------------------------------------------------------------------

-- Populate Property Address data

Update a
SET PropertyAddress = ISNULL(a.PropertyAddress,b.PropertyAddress)
FROM NashvilleHousing a
JOIN NashvilleHousing b
	On	a.ParcelID = b.ParcelID
	And a.[UniqueID ] != b.[UniqueID ]
Where a.PropertyAddress Is Null

SELECT ParcelID,PropertyAddress
FROM NashvilleHousing

--------------------------------------------------------------------------------------------------------------------------

-- Breaking out Address into Individual Columns (Address, City, State)

-- Select
--		SUBSTRING(PropertyAddress,1,CHARINDEX(',',PropertyAddress)-1)
--		SUBSTRING(PropertyAddress,CHARINDEX(',',PropertyAddress)+1, LEN(PropertyAddress))
-- From NashvilleHousing


ALTER TABLE PortfolioProject.dbo.NashvilleHousing
ADD SplitPropertyAddress VARCHAR(255);

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
ADD SplitPropertyCity VARCHAR(255);

Update PortfolioProject.dbo.NashvilleHousing
SET SplitPropertyAddress =	SUBSTRING(PropertyAddress,1,CHARINDEX(',',PropertyAddress)-1), 
	SplitPropertyCity =	SUBSTRING(PropertyAddress,CHARINDEX(',',PropertyAddress)+1, LEN(PropertyAddress))

--Update PortfolioProject.dbo.NashvilleHousing
--SET SplitPropertyCity =	SUBSTRING(PropertyAddress,CHARINDEX(',',PropertyAddress)+1, LEN(PropertyAddress))

Select SplitPropertyAddress,SplitPropertyCity
From NashvilleHousing



--------------------------------------------------------------------------------------------------------------------------
								--------- Alternative Method ------------
--------------------------------------------------------------------------------------------------------------------------

Select
	PARSENAME(REPLACE(OwnerAddress, ',', '.'),3) As SplitOwnerAddress,
	PARSENAME(REPLACE(OwnerAddress, ',', '.'),2) As SplitOwnerCity,
	PARSENAME(REPLACE(OwnerAddress, ',', '.'),1) As SplitOwnerState
From NashvilleHousing

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
ADD SplitOwnerAddress VARCHAR(255);

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
ADD SplitOwnerCity VARCHAR(255);

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
ADD SplitOwnerState VARCHAR(255);

Update PortfolioProject.dbo.NashvilleHousing
SET SplitOwnerAddress =	PARSENAME(REPLACE(OwnerAddress, ',', '.'),3)

Update PortfolioProject.dbo.NashvilleHousing
SET SplitOwnerCity = PARSENAME(REPLACE(OwnerAddress, ',', '.'),2)

Update PortfolioProject.dbo.NashvilleHousing
SET SplitOwnerState = PARSENAME(REPLACE(OwnerAddress, ',', '.'),1)

Select *
From NashvilleHousing



--------------------------------------------------------------------------------------------------------------------------


-- Change Y and N to Yes and No in "Sold as Vacant" field

Update NashvilleHousing
SET SoldAsVacant = 
(
	Select IIF(SoldAsVacant IN('Yes','Y'),'Yes','No')
)


--------------------------------------------------------------------------------------------------------------------------
								--------- Alternative Method ------------
--------------------------------------------------------------------------------------------------------------------------

Update NashvilleHousing
SET SoldAsVacant =
Case 
	When SoldAsVacant = 'Y' Then 'Yes'
	When SoldAsVacant = 'N' Then 'No'
	Else SoldAsVacant
END

Select DISTINCT(SoldAsVacant),Count(SoldAsVacant)
From NashvilleHousing
Group By SoldAsVacant
Order By 2

-----------------------------------------------------------------------------------------------------------------------------------------------------------

-- Remove Duplicates


With RowNumCTE AS(
Select *,
	ROW_NUMBER() Over (
	Partition By ParcelID,
				 PropertyAddress,
				 SaleDate,
				 SalePrice,
				 LegalReference
				 Order By UniqueID
				 ) row_num
From NashvilleHousing
)

Select *
From RowNumCTE
Where row_num > 1


---------------------------------------------------------------------------------------------------------

-- Delete Unused Columns


Select *
From NashvilleHousing

ALTER TABLE PortfolioProject.dbo.NashvilleHousing
Drop COLUMN SaleDate,PropertyAddress,OwnerAddress,TaxDistrict;


---------------------------------------------------------------------------------------------------------

-- Rename Columns

Select *
From NashvilleHousing

EXEC sp_rename 'PortfolioProject.dbo.NashvilleHousing.SaleDateConverted','SaleDate','COLUMN'

---------------------------------------------------------------------------------------------------------
