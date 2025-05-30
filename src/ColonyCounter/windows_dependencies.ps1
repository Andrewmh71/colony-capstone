$RequiredJavaHome = "C:\Program Files\Microsoft\jdk-11.0.27-hotspot"
$RequiredJavaPath = "$RequiredJavaHome\bin"
$RequiredPythonVersion = "3.9"
$RequiredPythonInstallDir = "C:\Program Files\Python39"
$RequiredPythonScriptsPath = "$RequiredPythonInstallDir\Scripts"
$RequiredMavenDir = "C:\Program Files\Apache\Maven"
$RequiredMavenBin = "$RequiredMavenDir\bin"

function Append-ToPath {
    param(
        [string[]]$PathsToAdd,
        [EnvironmentVariableTarget]$Target = [EnvironmentVariableTarget]::Machine
    )

    $currentPath = [Environment]::GetEnvironmentVariable("Path", $Target)
    $pathEntries = if ([string]::IsNullOrEmpty($currentPath)) { @() } else { $currentPath -split ';' }

    # Normalize paths (remove trailing slashes)
    $pathEntries = $pathEntries | ForEach-Object { $_.TrimEnd('\') } | Where-Object { $_ -ne '' }
    $pathsToAddNorm = $PathsToAdd | ForEach-Object { $_.TrimEnd('\') }

    # Add only those paths not already present
    $newEntries = $pathsToAddNorm | Where-Object { $pathEntries -notcontains $_ }

    if ($newEntries.Count -eq 0) {
        Write-Host "All specified paths are already present in PATH."
        return
    }

    $updatedEntries = $pathEntries + $newEntries
    $updatedEntries = $updatedEntries | Sort-Object -Unique

    $newPath = ($updatedEntries -join ';')

    [Environment]::SetEnvironmentVariable("Path", $newPath, $Target)

    Write-Host "Updated PATH environment variable with new entries."
}

function Check-Python39 {
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -like "*$RequiredPythonVersion*") {
            Write-Host "Python $RequiredPythonVersion found."
            return $true
        } else {
            Write-Warning "Python $RequiredPythonVersion not found. Current version: $pythonVersion"
            return $false
        }
    } catch {
        Write-Warning "Python is not installed."
        return $false
    }
}

function Add-PythonToPath {
    Append-ToPath -PathsToAdd @($RequiredPythonInstallDir, $RequiredPythonScriptsPath)
}

function Check-JavaHome {
    $currentJavaHome = [Environment]::GetEnvironmentVariable("JAVA_HOME", [EnvironmentVariableTarget]::Machine)
    if ($currentJavaHome -eq $RequiredJavaHome) {
        Write-Host "JAVA_HOME is correctly set."
        return $true
    } else {
        Write-Warning "JAVA_HOME not set correctly."
        return $false
    }
}

function Check-JavaPath {
    $envPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
    if ($envPath -match [regex]::Escape($RequiredJavaPath)) {
        Write-Host "Java path is in PATH."
        return $true
    } else {
        Write-Warning "Java path is missing from PATH."
        return $false
    }
}

function Check-Maven {
    if (Test-Path "$RequiredMavenBin\mvn.cmd") {
        Write-Host "Maven found."
        return $true
    } else {
        Write-Warning "Maven not found."
        return $false
    }
}

function Set-JavaHome {
    Write-Host "Setting JAVA_HOME and updating PATH..."
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $RequiredJavaHome, [EnvironmentVariableTarget]::Machine)
    Append-ToPath -PathsToAdd @($RequiredJavaPath)
}

function Add-MavenToPath {
    Append-ToPath -PathsToAdd @($RequiredMavenBin)
}


function Install-Python39 {
    Write-Host "Installing Python 3.9..."
    $installer = "$env:TEMP\python-3.9.6-amd64.exe"

    try {
        Invoke-WebRequest "https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe" -OutFile $installer -UseBasicParsing -ErrorAction Stop
        $process = Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -PassThru

        if ($process.ExitCode -eq 0) {
            Write-Host "Python 3.9 installation completed successfully."
        } else {
            Write-Warning "Python installer exited with code $($process.ExitCode)."
        }
    } catch {
        Write-Warning "Failed to install Python: $_"
    } finally {
        if (Test-Path $installer) { Remove-Item $installer -Force }
    }
}

function Install-Maven {
    Write-Host "Installing Maven..."
    $mavenZip = "$env:TEMP\maven.zip"

    try {
        Invoke-WebRequest "https://downloads.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.zip" -OutFile $mavenZip -ErrorAction Stop
        Expand-Archive $mavenZip -DestinationPath "C:\Program Files\Apache" -Force

        $extractedFolder = "C:\Program Files\Apache\apache-maven-3.9.6"
        if (Test-Path $RequiredMavenDir) {
            Remove-Item $RequiredMavenDir -Recurse -Force
        }
        Rename-Item -Path $extractedFolder -NewName "Maven"

        Add-MavenToPath
    } catch {
        Write-Warning "Failed to install Maven: $_"
    } finally {
        if (Test-Path $mavenZip) { Remove-Item $mavenZip -Force }
    }
}

function Install-Java {
    Write-Host "Installing Microsoft OpenJDK 11..."
    $javaInstallerUrl = "https://aka.ms/download-jdk/microsoft-jdk-11.0.27-windows-x64.msi"
    $installerPath = "$env:TEMP\Microsoft_OpenJDK11.msi"

    try {
        Invoke-WebRequest -Uri $javaInstallerUrl -OutFile $installerPath -UseBasicParsing -ErrorAction Stop
        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait -PassThru

        if ($process.ExitCode -eq 0) {
            Write-Host "Microsoft OpenJDK 11 installation completed successfully."
        } else {
            Write-Warning "Java installer exited with code $($process.ExitCode)."
        }
    } catch {
        Write-Warning "Failed to install Java: $_"
    } finally {
        if (Test-Path $installerPath) { Remove-Item $installerPath -Force }
    }
}

function Install-PythonPackages {
    $packages = @(
        "pyimagej",
        "PySide6",
        "opencv-python",
        "imagej",
        "scikit-learn",
        "scikit-image",
        "pillow-heif",
        "matplotlib",
        "pywin32",
        "openpyxl"
    )

    Write-Host "Installing required Python packages..."

    foreach ($package in $packages) {
        Write-Host "Installing $package ..."
        $installResult = & python -m pip install $package
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$package installed successfully."
        } else {
            Write-Warning "Failed to install $package."
        }
    }
}

# Main logic:

if (-not (Check-Python39)) {
    Install-Python39
    Add-PythonToPath
} else {
    Add-PythonToPath
}

if (-not (Test-Path $RequiredJavaHome)) {
    Install-Java
}

if (-not (Check-JavaHome) -or -not (Check-JavaPath)) {
    Set-JavaHome
}

if (-not (Check-Maven)) {
    Install-Maven
} else {
    Add-MavenToPath
}
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)

if ((Check-Python39)){
Install-PythonPackages

}

Write-Host "`n All done. Please restart your PowerShell session or system for changes to take effect."