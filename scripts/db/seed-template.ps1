# Seed a small template table for local development/testing
$DC = "docker"
$PROJECT = Split-Path -Leaf (Get-Location)

# Ensure db is up
& $DC 'compose' -p $PROJECT up -d db --remove-orphans | Out-Null
Start-Sleep -Seconds 2
$dbC = (& $DC 'compose' -p $PROJECT ps -q db).Trim()
if (-not $dbC) { Write-Error "db container not found"; exit 1 }

$PGUSER = $env:POSTGRES_USER; if (-not $PGUSER) { $PGUSER = 'postgres' }
$PGDB = $env:POSTGRES_DB; if (-not $PGDB) { $PGDB = 'appdb' }

# create template_items table if not exists and insert a sample row
& $DC 'exec' $dbC 'psql' '-U' $PGUSER '-d' $PGDB '-c' "CREATE TABLE IF NOT EXISTS templateitem (id serial primary key, title varchar(200) NOT NULL, body text, status varchar(20) NOT NULL DEFAULT 'DRAFT', created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now());"
# Insert with explicit timestamps to avoid relying on defaults that may be missing on older tables
& $DC 'exec' $dbC 'psql' '-U' $PGUSER '-d' $PGDB '-c' "INSERT INTO templateitem(title, body, status, created_at, updated_at) VALUES ('Hello template', 'This is a seeded template row', 'PUBLISHED', now(), now()) ON CONFLICT DO NOTHING;"

Write-Host "Seed complete."
