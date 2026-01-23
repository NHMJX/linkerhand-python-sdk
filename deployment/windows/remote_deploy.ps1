# LinkerHand HTTP API 远程部署脚本
# 使用此脚本可以远程部署LinkerHand HTTP API到多台Windows机器

param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName,

    [Parameter(Mandatory=$true)]
    [string]$PackagePath,

    [string]$InstallPath = "C:\LinkerHand_Deployment",

    [switch]$Force,

    [switch]$SkipValidation
)

# 导入必要的模块
Import-Module ActiveDirectory -ErrorAction SilentlyContinue

# 配置
$ErrorActionPreference = "Stop"
$ScriptName = "LinkerHand Remote Deployer"
$LogFile = "remote_deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Write-Success { param([string]$Message) Write-Log $Message "SUCCESS" }
function Write-Warning { param([string]$Message) Write-Log $Message "WARNING" }
function Write-Error { param([string]$Message) Write-Log $Message "ERROR" }

# 检查管理员权限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查远程连接
function Test-RemoteConnection {
    param([string]$Computer)

    Write-Log "检查远程连接到 $Computer..."

    try {
        $result = Test-Connection -ComputerName $Computer -Count 1 -Quiet
        if (-not $result) {
            throw "无法连接到 $Computer"
        }

        # 检查WMI访问
        $wmi = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $Computer -ErrorAction Stop
        Write-Success "远程连接正常 - $($wmi.Caption)"

        return $true
    }
    catch {
        Write-Error "远程连接失败: $($_.Exception.Message)"
        return $false
    }
}

# 检查目标机器兼容性
function Test-TargetCompatibility {
    param([string]$Computer)

    Write-Log "检查目标机器兼容性..."

    try {
        $os = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $Computer

        # 检查Windows版本 (需要Win10+ 或 Server 2016+)
        $version = [version]$os.Version
        $minVersion = [version]"10.0.14393"  # Windows 10 Anniversary Update / Server 2016

        if ($version -lt $minVersion) {
            Write-Warning "操作系统版本可能不兼容: $($os.Caption)"
            if (-not $Force) {
                throw "目标机器操作系统版本过低，请使用 -Force 参数强制继续"
            }
        }

        # 检查架构
        $arch = Get-WmiObject -Class Win32_Processor -ComputerName $Computer | Select-Object -First 1
        if ($arch.AddressWidth -ne 64) {
            throw "需要64位操作系统"
        }

        Write-Success "兼容性检查通过"
        return $true
    }
    catch {
        Write-Error "兼容性检查失败: $($_.Exception.Message)"
        return $false
    }
}

# 复制部署包
function Copy-DeploymentPackage {
    param([string]$SourcePath, [string]$Destination, [string]$Computer)

    Write-Log "复制部署包到远程机器..."

    try {
        $remotePath = "\\$Computer\$($Destination.Replace(':', '$'))"

        # 确保远程目录存在
        $remoteDir = Split-Path $remotePath -Parent
        if (-not (Test-Path $remoteDir)) {
            New-Item -ItemType Directory -Path $remoteDir -Force | Out-Null
        }

        # 复制文件
        Copy-Item -Path $SourcePath -Destination $remotePath -Force
        Write-Success "部署包复制完成: $remotePath"

        return $remotePath
    }
    catch {
        Write-Error "复制部署包失败: $($_.Exception.Message)"
        return $null
    }
}

# 远程安装
function Install-RemoteService {
    param([string]$Computer, [string]$RemotePackagePath, [string]$InstallPath)

    Write-Log "在远程机器上安装服务..."

    try {
        $scriptBlock = {
            param($PackagePath, $InstallPath, $Force)

            # 设置错误处理
            $ErrorActionPreference = "Stop"

            # 创建安装目录
            if (-not (Test-Path $InstallPath)) {
                New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
            }

            # 解压部署包
            Expand-Archive -Path $PackagePath -DestinationPath $InstallPath -Force

            # 设置工作目录
            Set-Location $InstallPath

            # 检查Python
            $pythonInstalled = $false
            try {
                $pythonVersion = python --version 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $pythonInstalled = $true
                }
            }
            catch {}

            if (-not $pythonInstalled) {
                throw "Python未安装，请先安装Python 3.8+"
            }

            # 安装依赖
            $result = Start-Process -FilePath "pip" -ArgumentList "install -r requirements.txt --quiet" -Wait -NoNewWindow -PassThru
            if ($result.ExitCode -ne 0) {
                throw "Python依赖安装失败"
            }

            # 运行安装脚本
            $installProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c install.bat" -Wait -NoNewWindow -PassThru
            $installProcess.WaitForExit()

            if ($installProcess.ExitCode -eq 0) {
                return @{Success = $true; Message = "安装成功"}
            }
            else {
                return @{Success = $false; Message = "安装脚本执行失败"}
            }
        }

        $result = Invoke-Command -ComputerName $Computer -ScriptBlock $scriptBlock -ArgumentList $RemotePackagePath, $InstallPath, $Force

        if ($result.Success) {
            Write-Success $result.Message
            return $true
        }
        else {
            Write-Error $result.Message
            return $false
        }
    }
    catch {
        Write-Error "远程安装失败: $($_.Exception.Message)"
        return $false
    }
}

# 验证安装
function Test-RemoteInstallation {
    param([string]$Computer)

    if ($SkipValidation) {
        Write-Log "跳过安装验证"
        return $true
    }

    Write-Log "验证远程安装..."

    try {
        $scriptBlock = {
            # 检查服务
            $service = Get-Service -Name "LinkerHandHTTPAPI" -ErrorAction SilentlyContinue
            if (-not $service) {
                return @{Valid = $false; Message = "服务未找到"}
            }

            # 检查服务状态
            if ($service.Status -ne "Running") {
                return @{Valid = $false; Message = "服务未运行"}
            }

            # 测试API连接
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    return @{Valid = $true; Message = "安装验证成功"}
                }
                else {
                    return @{Valid = $false; Message = "API响应异常"}
                }
            }
            catch {
                return @{Valid = $false; Message = "API连接失败"}
            }
        }

        $result = Invoke-Command -ComputerName $Computer -ScriptBlock $scriptBlock

        if ($result.Valid) {
            Write-Success $result.Message
            return $true
        }
        else {
            Write-Warning $result.Message
            return $false
        }
    }
    catch {
        Write-Error "验证失败: $($_.Exception.Message)"
        return $false
    }
}

# 批量部署函数
function Invoke-BatchDeployment {
    param([array]$Computers, [string]$PackagePath)

    Write-Log "开始批量部署到 $($Computers.Count) 台机器..."

    $results = @()

    foreach ($computer in $Computers) {
        Write-Log "部署到: $computer"
        Write-Log ("-" * 50)

        $result = @{
            Computer = $computer
            Success = $false
            Message = ""
            Details = @()
        }

        try {
            # 检查连接
            if (-not (Test-RemoteConnection $computer)) {
                $result.Message = "连接失败"
                $results += $result
                continue
            }
            $result.Details += "连接正常"

            # 检查兼容性
            if (-not (Test-TargetCompatibility $computer)) {
                $result.Message = "兼容性检查失败"
                $results += $result
                continue
            }
            $result.Details += "兼容性检查通过"

            # 复制包
            $remotePath = Copy-DeploymentPackage $PackagePath $InstallPath $computer
            if (-not $remotePath) {
                $result.Message = "复制失败"
                $results += $result
                continue
            }
            $result.Details += "部署包复制成功"

            # 安装服务
            if (-not (Install-RemoteService $computer $remotePath $InstallPath)) {
                $result.Message = "安装失败"
                $results += $result
                continue
            }
            $result.Details += "服务安装成功"

            # 验证安装
            if (Test-RemoteInstallation $computer) {
                $result.Success = $true
                $result.Message = "部署成功"
                $result.Details += "验证通过"
            }
            else {
                $result.Message = "验证失败"
            }

        }
        catch {
            $result.Message = "部署异常: $($_.Exception.Message)"
        }

        $results += $result
        Write-Log "结果: $($result.Message)"
        Write-Log ""
    }

    # 显示汇总结果
    Write-Log "批量部署完成"
    Write-Log ("=" * 50)

    $successCount = ($results | Where-Object { $_.Success }).Count
    $totalCount = $results.Count

    Write-Log "部署统计: $successCount/$totalCount 成功"

    # 显示详细结果
    foreach ($result in $results) {
        $status = if ($result.Success) { "✓" } else { "✗" }
        Write-Log ("$status $($result.Computer): $($result.Message)")
    }

    return $results
}

# 主函数
function Invoke-Main {
    Write-Log "开始 $ScriptName"
    Write-Log ("=" * 50)

    # 检查管理员权限
    if (-not (Test-Administrator)) {
        Write-Error "需要管理员权限运行此脚本"
        exit 1
    }

    # 检查参数
    if (-not (Test-Path $PackagePath)) {
        Write-Error "部署包不存在: $PackagePath"
        exit 1
    }

    # 处理批量部署
    if ($ComputerName -match ",") {
        $computers = $ComputerName -split "," | ForEach-Object { $_.Trim() }
        $results = Invoke-BatchDeployment $computers $PackagePath

        # 导出结果
        $results | Export-Csv -Path "deployment_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation
        Write-Log "结果已导出到CSV文件"
    }
    else {
        # 单机部署
        Write-Log "单机部署到: $ComputerName"

        # 检查连接
        if (-not (Test-RemoteConnection $ComputerName)) { exit 1 }

        # 检查兼容性
        if (-not (Test-TargetCompatibility $ComputerName)) { exit 1 }

        # 复制包
        $remotePath = Copy-DeploymentPackage $PackagePath $InstallPath $ComputerName
        if (-not $remotePath) { exit 1 }

        # 安装服务
        if (-not (Install-RemoteService $ComputerName $remotePath $InstallPath)) { exit 1 }

        # 验证安装
        if (-not (Test-RemoteInstallation $ComputerName)) { exit 1 }

        Write-Success "部署完成！"
        Write-Log "目标机器: http://$ComputerName`:8000"
    }

    Write-Log "脚本执行完成"
}

# 执行主函数
try {
    Invoke-Main
}
catch {
    Write-Error "脚本执行失败: $($_.Exception.Message)"
    Write-Error $_.ScriptStackTrace
    exit 1
}