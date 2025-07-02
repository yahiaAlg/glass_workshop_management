# Django Glass Workshop Management System - PowerShell Launcher
# Usage: .\launch.ps1 [command]
# Commands: setup, run, migrate, shell, test, reset, populate, backup, restore

param(
    [string]$Command = "run"
)

$ProjectName = "Glass Workshop Management System"
$PythonCmd = "python"
$ManagePy = "manage.py"
$VenvDir = "venv"
$BackupDir = "backups"

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Cyan
}

function Write-Header {
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host " $ProjectName" -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
}

# Check if virtual environment exists
function Test-VirtualEnvironment {
    if (-not (Test-Path $VenvDir)) {
        Write-Warning "Virtual environment not found. Creating one..."
        & $PythonCmd -m venv $VenvDir
        Write-Status "Virtual environment created."
    }
}

# Activate virtual environment
function Enable-VirtualEnvironment {
    if (Test-Path $VenvDir) {
        if (Test-Path "$VenvDir\Scripts\Activate.ps1") {
            & "$VenvDir\Scripts\Activate.ps1"
        } else {
            Write-Error "Virtual environment activation script not found!"
            exit 1
        }
        Write-Status "Virtual environment activated."
    } else {
        Write-Error "Virtual environment not found!"
        exit 1
    }
}

# Install requirements
function Install-Requirements {
    if (Test-Path "requirements.txt") {
        Write-Status "Installing requirements..."
        pip install -r requirements.txt
        Write-Status "Requirements installed successfully."
    } else {
        Write-Warning "requirements.txt not found. Installing essential packages..."
        pip install django pillow django-import-export reportlab
        Write-Status "Essential packages installed."
    }
}

# Run migrations
function Invoke-Migrations {
    Write-Status "Running database migrations..."
    & $PythonCmd $ManagePy makemigrations
    & $PythonCmd $ManagePy migrate
    Write-Status "Migrations completed."
}

# Collect static files
function Invoke-CollectStatic {
    Write-Status "Collecting static files..."
    & $PythonCmd $ManagePy collectstatic --noinput
    Write-Status "Static files collected."
}

# Create media directories
function Initialize-MediaDirectories {
    Write-Status "Creating media directories..."
    $MediaDirs = @(
        "media",
        "media\company",
        "media\inventory",
        "media\backups",
        "media\backups\exports",
        "media\invoices",
        "media\documents"
    )
    
    foreach ($dir in $MediaDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "Created directory: $dir"
        }
    }
}

# Setup project
function Initialize-Project {
    Write-Header
    Write-Status "Setting up Glass Workshop Management System..."
    
    Test-VirtualEnvironment
    Enable-VirtualEnvironment
    Install-Requirements
    Initialize-MediaDirectories
    Invoke-Migrations
    
    # Run glass shop specific management commands
    Write-Status "Populating glass product categories..."
    if (Test-Path "apps\inventory\management\commands\populate_glass_categories.py") {
        & $PythonCmd $ManagePy populate_glass_categories
    }
    
    Write-Status "Creating sample glass products..."
    if (Test-Path "apps\inventory\management\commands\populate_glass_products.py") {
        & $PythonCmd $ManagePy populate_glass_products
    }
    
    Write-Status "Creating sample customers..."
    if (Test-Path "apps\customers\management\commands\populate_customers.py") {
        & $PythonCmd $ManagePy populate_customers
    }
    
    Write-Status "Creating sample suppliers..."
    if (Test-Path "apps\suppliers\management\commands\populate_suppliers.py") {
        & $PythonCmd $ManagePy populate_suppliers
    }
    
    Write-Status "Setting up company profile..."
    if (Test-Path "apps\company\management\commands\setup_company.py") {
        & $PythonCmd $ManagePy setup_company
    }
    
    Write-Status "Creating admin user..."
    if (Test-Path "apps\authentication\management\commands\create_admin.py") {
        & $PythonCmd $ManagePy create_admin
    } else {
        Write-Status "Creating superuser manually..."
        & $PythonCmd $ManagePy createsuperuser
    }
    
    Invoke-CollectStatic
    
    Write-Host ""
    Write-Success "Glass Workshop Management System setup completed!"
    Write-Status "Server will be available at: http://127.0.0.1:8000"
    Write-Status "Admin panel: http://127.0.0.1:8000/admin"
    Write-Status "Dashboard: http://127.0.0.1:8000/dashboard"
    Write-Status "Use: .\launch.ps1 run to start the server"
}

# Run development server
function Start-DevelopmentServer {
    Write-Header
    Enable-VirtualEnvironment
    Write-Status "Starting Glass Workshop Management System..."
    Write-Status "Server will be available at: http://127.0.0.1:8000"
    Write-Status "Admin panel: http://127.0.0.1:8000/admin"
    Write-Status "Dashboard: http://127.0.0.1:8000/dashboard"
    Write-Status "Invoices: http://127.0.0.1:8000/invoices"
    Write-Status "Inventory: http://127.0.0.1:8000/inventory"
    Write-Status "Customers: http://127.0.0.1:8000/customers"
    Write-Host ""
    Write-Status "Press Ctrl+C to stop the server"
    Write-Host ""
    & $PythonCmd $ManagePy runserver
}

# Run Django shell
function Start-DjangoShell {
    Enable-VirtualEnvironment
    Write-Status "Starting Django shell for Glass Workshop System..."
    & $PythonCmd $ManagePy shell
}

# Run tests
function Invoke-Tests {
    Enable-VirtualEnvironment
    Write-Status "Running Glass Workshop Management System tests..."
    & $PythonCmd $ManagePy test
}

# Populate sample data
function Populate-SampleData {
    Enable-VirtualEnvironment
    Write-Status "Populating Glass Workshop with sample data..."
    
    # Populate in order of dependencies
    $Commands = @(
        "populate_glass_categories",
        "populate_glass_products", 
        "populate_customers",
        "populate_suppliers",
        "populate_sample_orders",
        "populate_sample_invoices"
    )
    
    foreach ($cmd in $Commands) {
        if (Test-Path "apps\*\management\commands\$cmd.py") {
            Write-Status "Running: $cmd"
            & $PythonCmd $ManagePy $cmd
        } else {
            Write-Warning "Command $cmd not found, skipping..."
        }
    }
    
    Write-Success "Sample data population completed!"
}

# Create backup
function Create-Backup {
    Enable-VirtualEnvironment
    Write-Status "Creating Glass Workshop database backup..."
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    $BackupFile = "$BackupDir\glassworkshop_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    
    & $PythonCmd $ManagePy dumpdata --indent 2 --output $BackupFile
    
    if (Test-Path $BackupFile) {
        Write-Success "Backup created: $BackupFile"
    } else {
        Write-Error "Failed to create backup!"
    }
}

# Restore from backup
function Restore-Backup {
    Enable-VirtualEnvironment
    
    if (-not (Test-Path $BackupDir)) {
        Write-Error "Backup directory not found!"
        return
    }
    
    $BackupFiles = Get-ChildItem -Path $BackupDir -Filter "*.json" | Sort-Object LastWriteTime -Descending
    
    if ($BackupFiles.Count -eq 0) {
        Write-Error "No backup files found!"
        return
    }
    
    Write-Status "Available backup files:"
    for ($i = 0; $i -lt $BackupFiles.Count; $i++) {
        Write-Host "  [$i] $($BackupFiles[$i].Name)" -ForegroundColor Yellow
    }
    
    $Selection = Read-Host "Enter backup file number to restore (0-$($BackupFiles.Count - 1))"
    
    if ($Selection -match '^\d+$' -and [int]$Selection -lt $BackupFiles.Count) {
        $SelectedFile = $BackupFiles[[int]$Selection].FullName
        Write-Warning "This will replace all current data with backup data!"
        $Confirmation = Read-Host "Are you sure? (y/N)"
        
        if ($Confirmation -eq 'y' -or $Confirmation -eq 'Y') {
            Write-Status "Restoring from: $($BackupFiles[[int]$Selection].Name)"
            & $PythonCmd $ManagePy loaddata $SelectedFile
            Write-Success "Backup restored successfully!"
        } else {
            Write-Status "Restore cancelled."
        }
    } else {
        Write-Error "Invalid selection!"
    }
}

# Reset database
function Reset-Database {
    Write-Warning "This will delete your Glass Workshop database and all data!"
    Write-Warning "This includes all invoices, customers, inventory, and orders!"
    $confirmation = Read-Host "Are you sure? Type 'DELETE' to confirm"
    
    if ($confirmation -eq 'DELETE') {
        Enable-VirtualEnvironment
        Write-Status "Creating backup before reset..."
        Create-Backup
        
        Write-Status "Removing database..."
        if (Test-Path "db.sqlite3") {
            Remove-Item "db.sqlite3" -Force
        }
        
        Write-Status "Removing migration files..."
        Get-ChildItem -Path "apps" -Recurse -Filter "*.py" | Where-Object { 
            $_.FullName -like "*\migrations\*" -and $_.Name -ne "__init__.py"
        } | Remove-Item -Force
        
        Get-ChildItem -Path "apps" -Recurse -Filter "*.pyc" | Where-Object { 
            $_.FullName -like "*\migrations\*"
        } | Remove-Item -Force
        
        Invoke-Migrations
        Write-Success "Database reset completed."
        Write-Status "Run 'populate' command to add sample data."
    } else {
        Write-Status "Database reset cancelled."
    }
}

# Show system status
function Show-Status {
    Write-Header
    Write-Status "Glass Workshop Management System Status"
    Write-Host ""
    
    # Check virtual environment
    if (Test-Path $VenvDir) {
        Write-Host "✓ Virtual Environment: Found" -ForegroundColor Green
    } else {
        Write-Host "✗ Virtual Environment: Missing" -ForegroundColor Red
    }
    
    # Check database
    if (Test-Path "db.sqlite3") {
        Write-Host "✓ Database: Found" -ForegroundColor Green
    } else {
        Write-Host "✗ Database: Missing" -ForegroundColor Red
    }
    
    # Check media directories
    if (Test-Path "media") {
        Write-Host "✓ Media Directory: Found" -ForegroundColor Green
    } else {
        Write-Host "✗ Media Directory: Missing" -ForegroundColor Red
    }
    
    # Check static files
    if (Test-Path "static") {
        Write-Host "✓ Static Directory: Found" -ForegroundColor Green
    } else {
        Write-Host "✗ Static Directory: Missing" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Show help
function Show-Help {
    Write-Header
    Write-Host "Glass Workshop Management System - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  setup      - Complete initial setup (create venv, install deps, migrate, populate)" -ForegroundColor Yellow
    Write-Host "  run        - Start development server" -ForegroundColor Yellow
    Write-Host "  migrate    - Run database migrations only" -ForegroundColor Yellow
    Write-Host "  shell      - Open Django shell" -ForegroundColor Yellow
    Write-Host "  test       - Run all tests" -ForegroundColor Yellow
    Write-Host "  populate   - Populate database with sample glass shop data" -ForegroundColor Yellow
    Write-Host "  backup     - Create database backup" -ForegroundColor Yellow
    Write-Host "  restore    - Restore from backup" -ForegroundColor Yellow
    Write-Host "  reset      - Reset database (WARNING: destructive)" -ForegroundColor Yellow
    Write-Host "  status     - Show system status" -ForegroundColor Yellow
    Write-Host "  help       - Show this help message" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage: .\launch.ps1 [command]" -ForegroundColor Green
    Write-Host "If no command is provided, 'run' is used by default." -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick Start:" -ForegroundColor Cyan
    Write-Host "  1. .\launch.ps1 setup    # First time setup" -ForegroundColor White
    Write-Host "  2. .\launch.ps1 run      # Start the server" -ForegroundColor White
    Write-Host "  3. Open http://127.0.0.1:8000 in your browser" -ForegroundColor White
}

# Main script logic
switch ($Command.ToLower()) {
    "setup" {
        Initialize-Project
    }
    "run" {
        Start-DevelopmentServer
    }
    "migrate" {
        Enable-VirtualEnvironment
        Invoke-Migrations
    }
    "shell" {
        Start-DjangoShell
    }
    "test" {
        Invoke-Tests
    }
    "populate" {
        Populate-SampleData
    }
    "backup" {
        Create-Backup
    }
    "restore" {
        Restore-Backup
    }
    "reset" {
        Reset-Database
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}