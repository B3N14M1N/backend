# Seeds Admin/User roles once
# Use 'docker' as the command and pass 'compose' as an argument so PowerShell tokenizes correctly.
$DC = "docker"
$PROJECT = Split-Path -Leaf (Get-Location)
& $DC 'compose' -p $PROJECT up -d db --remove-orphans | Out-Null
Start-Sleep -Seconds 2
$dbC = (& $DC 'compose' -p $PROJECT ps -q db).Trim()
if (-not $dbC) {
	Write-Error "Could not find 'db' container via docker compose. Is the compose project running?";
	exit 1
}

# Prefer host env vars if set; otherwise fall back to common defaults used in this repo's .env
$PGUSER = $env:POSTGRES_USER
if (-not $PGUSER) { $PGUSER = 'postgres' }
$PGDB = $env:POSTGRES_DB
if (-not $PGDB) { $PGDB = 'appdb' }

# Run psql inside the db container. Tokenize args so PowerShell doesn't try to run a single string command.
& $DC 'exec' $dbC 'psql' '-U' $PGUSER '-d' $PGDB '-c' "INSERT INTO roles(name) VALUES ('Admin') ON CONFLICT DO NOTHING;"
& $DC 'exec' $dbC 'psql' '-U' $PGUSER '-d' $PGDB '-c' "INSERT INTO roles(name) VALUES ('User') ON CONFLICT DO NOTHING;"
Write-Host "Roles seeded."
