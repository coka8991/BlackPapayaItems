<#
.SYNOPSIS
    Exports RCLootCouncil loot history from WoW SavedVariables to CSV.

.DESCRIPTION
    Parses the RCLootCouncilLootDB section from the SavedVariables Lua file
    and exports all loot history entries to a CSV file, replicating the same
    columns as the addon's built-in ExportCSV() function.

.PARAMETER SavedVarsPath
    Path to the RCLootCouncil.lua SavedVariables file.
    Defaults to auto-detecting from common WoW install paths.

.PARAMETER OutputPath
    Path for the output CSV file. Defaults to Desktop\RCLootCouncil_History.csv

.EXAMPLE
    .\export_loot_history.ps1
    .\export_loot_history.ps1 -SavedVarsPath "D:\WoW\WTF\Account\12345\SavedVariables\RCLootCouncil.lua"
    .\export_loot_history.ps1 -OutputPath "C:\Users\Me\loot.csv"
#>
param(
    [string]$SavedVarsPath,
    [string]$OutputPath
)

# --- Auto-detect SavedVariables file ---
if (-not $SavedVarsPath) {
    $wowPaths = @(
        "C:\Program Files (x86)\World of Warcraft\_retail_\WTF\Account",
        "C:\Program Files\World of Warcraft\_retail_\WTF\Account",
        "D:\World of Warcraft\_retail_\WTF\Account",
        "E:\World of Warcraft\_retail_\WTF\Account"
    )
    foreach ($base in $wowPaths) {
        if (Test-Path $base) {
            $found = Get-ChildItem -Path $base -Recurse -Filter "RCLootCouncil.lua" -ErrorAction SilentlyContinue |
                     Where-Object { $_.DirectoryName -like "*SavedVariables*" } |
                     Select-Object -First 1
            if ($found) {
                $SavedVarsPath = $found.FullName
                break
            }
        }
    }
}

if (-not $SavedVarsPath -or -not (Test-Path $SavedVarsPath)) {
    Write-Error "No se encontro el archivo SavedVariables de RCLootCouncil. Usa -SavedVarsPath para especificarlo."
    exit 1
}

if (-not $OutputPath) {
    $OutputPath = Join-Path $PWD "RCLootCouncil_History.csv"
}

Write-Host "Leyendo: $SavedVarsPath" -ForegroundColor Cyan
# --- Read file and extract RCLootCouncilLootDB block ---
$rawContent = Get-Content $SavedVarsPath -Raw -Encoding UTF8

# Extract the RCLootCouncilLootDB section
$lootDBMatch = [regex]::Match($rawContent, '(?s)RCLootCouncilLootDB\s*=\s*\{(.+)')
if (-not $lootDBMatch.Success) {
    Write-Error "No se encontro RCLootCouncilLootDB en el archivo."
    exit 1
}

$lootDBContent = $lootDBMatch.Groups[1].Value

# --- Show available fields from the Lua file ---
$camposLua = [regex]::Matches($lootDBContent, '\["(\w+)"\]\s*=') |
    ForEach-Object { $_.Groups[1].Value } |
    Select-Object -Unique |
    Sort-Object
Write-Host ""
Write-Host "Campos encontrados en el archivo Lua:" -ForegroundColor Magenta
Write-Host ("  " + ($camposLua -join ", ")) -ForegroundColor Gray
Write-Host ""

# --- Simple Lua table parser ---
# We parse the factionrealm entries to extract loot history

function Extract-ItemIDFromLink([string]$link) {
    if ($link -match 'Hitem:(\d+)') {
        return $Matches[1]
    }
    return ""
}

function Extract-ItemStringFromLink([string]$link) {
    if ($link -match '(item:[^|]+)') {
        return $Matches[1]
    }
    return ""
}

function Clean-ItemLink([string]$link) {
    # Remove WoW color/hyperlink formatting for readability
    if (-not $link) { return "" }
    $link = $link -replace '\|c[0-9a-fA-F]{8}', ''
    $link = $link -replace '\|cn[^:]*:', ''
    $link = $link -replace '\|H[^|]*\|h', ''
    $link = $link -replace '\|h', ''
    $link = $link -replace '\|r', ''
    $link = $link -replace '[\[\]]', ''
    return $link.Trim()
}

# State machine parser for extracting loot entries
$entries = [System.Collections.Generic.List[PSObject]]::new()

# Find the factionrealm section
$frMatch = [regex]::Match($lootDBContent, '(?s)\["factionrealm"\]\s*=\s*\{')
if (-not $frMatch.Success) {
    Write-Error "No se encontro la seccion factionrealm. No hay datos de historial."
    exit 1
}

$frStart = $lootDBContent.IndexOf($frMatch.Value) + $frMatch.Value.Length

# Parse realm sections and player entries
$lines = $lootDBContent.Substring($frStart) -split "`n"
$currentRealm = ""
$currentPlayer = ""
$inEntry = $false
$braceDepth = 0
$entryFields = @{}
$totalEntries = 0

foreach ($line in $lines) {
    $trimmed = $line.Trim()

    # Detect realm header: ["Horde - Sanguino"] = {
    if ($trimmed -match '^\["([^"]+)"\]\s*=\s*\{' -and -not $inEntry) {
        $key = $Matches[1]
        # Realm keys look like "Horde - Sanguino", player keys like "PlayerName-Server"
        if ($key -match '^\w+ - \w') {
            $currentRealm = $key
            continue
        }
        # Player key
        if ($key -match '-') {
            $currentPlayer = $key
            continue
        }
    }

    # Detect start of loot entry block: bare { on a line
    if ($trimmed -eq '{' -and $currentPlayer -and -not $inEntry) {
        $inEntry = $true
        $braceDepth = 1
        $entryFields = @{}
        continue
    }

    if ($inEntry) {
        # Track nested braces (for color tables, wishes tables, etc.)
        $openBraces = ([regex]::Matches($trimmed, '\{')).Count
        $closeBraces = ([regex]::Matches($trimmed, '\}')).Count
        $braceDepth += $openBraces - $closeBraces

        if ($braceDepth -le 0) {
            # Entry complete - emit it
            if ($entryFields.ContainsKey('lootWon')) {
                $itemLink = $entryFields['lootWon']
                $g1 = if ($entryFields.ContainsKey('itemReplaced1')) { $entryFields['itemReplaced1'] } else { '' }
                $g2 = if ($entryFields.ContainsKey('itemReplaced2')) { $entryFields['itemReplaced2'] } else { '' }
                $entry = [PSCustomObject]@{
                    player        = $currentPlayer
                    date          = if ($entryFields.ContainsKey('date'))          { $entryFields['date'] }          else { '' }
                    time          = if ($entryFields.ContainsKey('time'))          { $entryFields['time'] }          else { '' }
                    id            = if ($entryFields.ContainsKey('id'))            { $entryFields['id'] }            else { '' }
                    item          = Clean-ItemLink $itemLink
                    itemID        = Extract-ItemIDFromLink $itemLink
                    itemString    = Extract-ItemStringFromLink $itemLink
                    response      = if ($entryFields.ContainsKey('response'))      { $entryFields['response'] }      else { '' }
                    votes         = if ($entryFields.ContainsKey('votes'))         { $entryFields['votes'] }         else { '0' }
                    playerClass   = if ($entryFields.ContainsKey('class'))         { $entryFields['class'] }         else { '' }
                    instance      = if ($entryFields.ContainsKey('instance'))      { $entryFields['instance'] }      else { '' }
                    boss          = if ($entryFields.ContainsKey('boss'))          { $entryFields['boss'] }          else { '' }
                    difficultyID  = if ($entryFields.ContainsKey('difficultyID'))  { $entryFields['difficultyID'] }  else { '' }
                    mapID         = if ($entryFields.ContainsKey('mapID'))         { $entryFields['mapID'] }         else { '' }
                    groupSize     = if ($entryFields.ContainsKey('groupSize'))     { $entryFields['groupSize'] }     else { '' }
                    gear1         = Clean-ItemLink $g1
                    gear2         = Clean-ItemLink $g2
                    responseID    = if ($entryFields.ContainsKey('responseID'))    { $entryFields['responseID'] }    else { '' }
                    isAwardReason = if ($entryFields.ContainsKey('isAwardReason')) { $entryFields['isAwardReason'] } else { 'false' }
                    note          = if ($entryFields.ContainsKey('note'))          { $entryFields['note'] }          else { '' }
                    owner         = if ($entryFields.ContainsKey('owner'))         { $entryFields['owner'] }         else { 'Unknown' }
                    typeCode      = if ($entryFields.ContainsKey('typeCode'))      { $entryFields['typeCode'] }      else { '' }
                    tierToken     = if ($entryFields.ContainsKey('tierToken'))     { $entryFields['tierToken'] }     else { '' }
                }
                $entries.Add($entry)
                $totalEntries++
            }
            $inEntry = $false
            $entryFields = @{}
            continue
        }

        # Only parse key-value at depth 1 (skip nested tables like color, wishes)
        if ($braceDepth -eq 1) {
            # Match: ["key"] = value,
            if ($trimmed -match '^\["(\w+)"\]\s*=\s*(.+?),?\s*$') {
                $fieldName = $Matches[1]
                $fieldValue = $Matches[2].Trim().TrimEnd(',')

                # Parse value types
                if ($fieldValue -match '^"(.*)"$') {
                    $fieldValue = $Matches[1]
                }
                elseif ($fieldValue -eq 'true') {
                    $fieldValue = 'true'
                }
                elseif ($fieldValue -eq 'false') {
                    $fieldValue = 'false'
                }
                # Skip tables (color, wishes, etc.)
                elseif ($fieldValue -match '\{') {
                    continue
                }

                $entryFields[$fieldName] = $fieldValue
            }
        }
    }

    # If we encounter the end of factionrealm, stop
    if ($trimmed -eq '},' -and -not $inEntry -and -not $currentPlayer) {
        break
    }
}

if ($entries.Count -eq 0) {
    Write-Warning "No se encontraron entradas de historial."
    exit 0
}

# --- Export to CSV ---
$entries | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Exportacion completada!" -ForegroundColor Green
