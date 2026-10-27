$TaskRepo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$env:PYTHONPATH = @('shared','backend','inventario','deteccion' | ForEach-Object { Join-Path $TaskRepo $_ }) -join [IO.Path]::PathSeparator
Write-Output 'PYTHONPATH configurado para esta sesión. No se cargaron credenciales.'
