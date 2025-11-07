# PowerShell script to create empty Django HTML template files

# Define the base directory for your Django templates
$baseDir = "templates\admin\bookings"

# Ensure the directory exists
if (!(Test-Path $baseDir)) {
    New-Item -ItemType Directory -Path $baseDir -Force | Out-Null
    Write-Host "Created directory: $baseDir"
}

# List of HTML files to create
$htmlFiles = @(
    "booking_list.html",
    "booking_detail.html",
    "pending_payments.html",
    "payment_list.html"
)

# Create each file if it doesn't exist
foreach ($file in $htmlFiles) {
    $filePath = Join-Path $baseDir $file
    if (!(Test-Path $filePath)) {
        New-Item -ItemType File -Path $filePath | Out-Null
        Write-Host "Created: $filePath"
    } else {
        Write-Host "Already exists: $filePath"
    }
}

Write-Host "✅ All HTML files created successfully."
