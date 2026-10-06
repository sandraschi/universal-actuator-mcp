# Per-repo fleet start config for universal-actuator-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'universal-actuator-mcp'
    BackendPort  = 10929
    FrontendPort = 10982
    HealthPath   = '/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'universal_actuator_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10929' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
