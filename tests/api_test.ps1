# PowerShell script for direct API testing
param(
    [string]$Query = "What is Retrieval-Augmented Generation?"
)

$baseUrl = "http://localhost:8000"

Write-Host "🧪 RAG API Direct Testing" -ForegroundColor Green
Write-Host "=" * 50

# Test Health
Write-Host "`n=== HEALTH CHECK ===" -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "Status: OK" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $healthResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test Chat API
Write-Host "`n=== CHAT API TEST ===" -ForegroundColor Yellow
try {
    $chatBody = @{
        query = $Query
    } | ConvertTo-Json

    $chatResponse = Invoke-RestMethod -Uri "$baseUrl/chat" -Method POST -Body $chatBody -ContentType "application/json"
    Write-Host "Status: OK" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $chatResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Chat API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test WebSource API
Write-Host "`n=== WEBSOURCE API TEST ===" -ForegroundColor Yellow
try {
    $sourcesResponse = Invoke-RestMethod -Uri "$baseUrl/websource" -Method GET
    Write-Host "Status: OK" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $sourcesResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "WebSource API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Related API
Write-Host "`n=== RELATED API TEST ===" -ForegroundColor Yellow
try {
    $relatedResponse = Invoke-RestMethod -Uri "$baseUrl/related" -Method GET
    Write-Host "Status: OK" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $relatedResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Related API failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + "=" * 50
Write-Host "✅ API testing completed" -ForegroundColor Green
