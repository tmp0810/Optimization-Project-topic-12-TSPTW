$python = "C:\Users\teebow1e\AppData\Local\Programs\Python\Python311\python.exe"

if ($args.Count -eq 0) {
    Write-Host "Usage: .\run_tests.ps1 <PythonFileName.py>"
    exit
}

$pythonFile = Get-Item -Path $args[0] -ErrorAction Stop
$logFile = "$($pythonFile.BaseName.Replace(' ', ''))_log.log"
Out-File -FilePath $logFile -Force

foreach ($testFile in Get-ChildItem -Path "./test_case" -Filter "*.txt") {
    Write-Host "Running $($pythonFile.Name) on test file $($testFile.Name)..."

    $startTime = Get-Date

    # Run Python process and capture stdout and stderr inline
    $processOutput = & $python "`"$($pythonFile.FullName)`"" "`"$($testFile.FullName)`"" 2>&1

    $elapsedTime = ((Get-Date) - $startTime).TotalSeconds

    if (!$processOutput) {
        # Handle case where output is empty (e.g., timeout or error)
        $output = @(
            "$($pythonFile.Name) result for test $($testFile.Name):"
            "Execution terminated or produced no output."
            "Time elapsed: $elapsedTime seconds"
            "----------------------------------------"
        )
    } else {
        # Handle normal case
        $output = @(
            "$($pythonFile.Name) result for test $($testFile.Name):"
            $processOutput
            "Time elapsed: $elapsedTime seconds"
            "----------------------------------------"
        )
    }

    $output | Out-File -FilePath $logFile -Append
}
