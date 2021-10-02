------ SQL Data Exploration ------

-- Selecting Everything From CovidDeaths TABLE
Select *
From PortfolioProject..CovidDeaths
Where continent Is Not Null
Order by 3,4
-- **********

-- Selecting Everything From CovidVaccinations TABLE
Select *
From PortfolioProject..CovidVaccinations
Order by 3,4
-- **********

-- Selecting Specific Coulumns to look at

Select location, date, total_cases, new_cases, total_deaths, population
From PortfolioProject..CovidDeaths
Order By 1,2
-- **********

-- Looking at the Total Cases vs Total Deaths
-- Shows the probability of someone dying if they are infected based on location

Select location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 as DeathPercentage
From PortfolioProject..CovidDeaths
Where location Like '%Pakistan%'
Order By 1,2
-- **********

-- Looking at the Population vs Total Cases 
-- Shows percentage of population infected

Select location, date, total_cases, population, (total_cases/population)*100 as InfectPercentage
From PortfolioProject..CovidDeaths
Where continent Is Not Null
And location Like '%Pakistan%'
Order By 1,2
-- **********

-- Showing countries with the highest infection rate vs Population

Select location, population, MAX(total_cases) as HighestInfectionCount, Max((total_cases/population)*100) as InfectPercentage
From PortfolioProject..CovidDeaths
Where continent Is Not Null
-- and location Like '%Pakistan%'
Group By location, population
Order By InfectPercentage desc
-- **********

-- Showing Countries with Highest Death Counts

Select 
	location, 
	MAX(total_deaths) as HighestDeath
	--, Max((total_cases/population)*100) as InfectPercentage
From PortfolioProject..CovidDeaths
Where continent Is Not Null
-- and location Like '%Pakistan%'
Group By location
Order By HighestDeath desc
-- **********

-- Breaking Things Down By Continent

-- First Way --
Select 
	location, 
	MAX(total_deaths) as HighestDeath
	--, Max((total_cases/population)*100) as InfectPercentage
From PortfolioProject..CovidDeaths
Where continent Is Null
-- and location Like '%Pakistan%'
Group By location
Order By HighestDeath desc
-- **********

-- Second Way
Select 
	continent, 
	MAX(total_deaths) as HighestDeath
	--, Max((total_cases/population)*100) as InfectPercentage
From PortfolioProject..CovidDeaths
Where continent Is Not Null
-- and location Like '%Pakistan%'
Group By continent
Order By HighestDeath desc
-- **********

-- GLOBAL NUMBERS

-- Looking at Total Cases Vs total Deaths
-- Shows Percentage of Deaths w.r.t Cases recorded Globally
Select 
	SUM(new_cases) As total_cases, 
	SUM(new_deaths) As total_deaths, 
	(SUM(new_deaths)/ SUM(new_cases))*100 as DeathPercentage
From PortfolioProject..CovidDeaths
Where continent Is Not Null
-- Group By date
--Order By 1 Desc
-- **********

-- Joining Both Deaths And Vaccinations Table
-- Looking at total population vs vaccinations

Select 
	cd.continent,
	cd.location,
	cd.date, 
	cd.population, 
	cv.new_vaccinations,
	SUM(CONVERT(int, cv.new_vaccinations)) --SUM(CAST(cv.new_vaccinations AS int)) can also be used 
	Over 
	(Partition By cd.location Order By cd.location,cd.date) As RollingVaccinatedSum 
From PortfolioProject..CovidDeaths cd
Join PortfolioProject..CovidVaccinations cv
	On cd.date = cv.date
	And cd.location = cv.location
Where cd.continent Is Not Null
Order By 2,3
-- **********

-- CREATING CTE for Population vs Vaccination
With PopVSVac (Continent, Location, Date, Population, new_vaccinations, RollingVaccinatedSum)
as
(
Select 
	cd.continent,
	cd.location,
	cd.date, 
	cd.population, 
	cv.new_vaccinations,
	SUM(CONVERT(int, cv.new_vaccinations)) 
	Over 
	(Partition By cd.location Order By cd.location,cd.date) As RollingVaccinatedSum 
From PortfolioProject..CovidDeaths cd
Join PortfolioProject..CovidVaccinations cv
	On cd.date = cv.date
	And cd.location = cv.location
Where cd.continent Is Not Null
--Order By 2,3
)

Select *,(RollingVaccinatedSum/Population)*100 as RollingPercent
From PopVSVac
Order By 2,3
-- **********

-- Building a TEMP Table about percentage of People vaccinated
-- Shows Rolling Sum of People and percentage of people of a country that got vaccinated by Dates 

Drop Table If Exists #PercentPopulationVaccinated
Create Table #PercentPopulationVaccinated
(
	Continent nvarchar(255),
	Location nvarchar(255),
	Date datetime,
	Population numeric,
	New_Vaccinations numeric,
	RollingVaccinatedSum numeric
)

INSERT INTO #PercentPopulationVaccinated
Select 
	cd.continent,
	cd.location,
	cd.date, 
	cd.population, 
	cv.new_vaccinations,
	SUM(CONVERT(int, cv.new_vaccinations)) 
	Over 
	(Partition By cd.location Order By cd.location,cd.date) As RollingVaccinatedSum 
From PortfolioProject..CovidDeaths cd
Join PortfolioProject..CovidVaccinations cv
	On cd.date = cv.date
	And cd.location = cv.location
Where cd.continent Is Not Null
--Order By 2,3

Select *,(RollingVaccinatedSum/Population)*100 as RollingPercent
From #PercentPopulationVaccinated
Order By 2,3
-- **********


-- Creating View to Store Data For Later Use For Example Visualizations
USE PortfolioProject
GO
CREATE VIEW PercentVaccinated
AS
Select 
	cd.continent,
	cd.location,
	cd.date, 
	cd.population, 
	cv.new_vaccinations,
	SUM(CONVERT(int, cv.new_vaccinations)) 
	Over 
	(Partition By cd.location Order By cd.location,cd.date) As RollingVaccinatedSum 
From PortfolioProject..CovidDeaths cd
Join PortfolioProject..CovidVaccinations cv
	On cd.date = cv.date
	And cd.location = cv.location
Where cd.continent Is Not Null
--Order By 2,3
-- **********
