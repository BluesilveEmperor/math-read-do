<#
.SYNOPSIS
    math-read-do (main) Auto-Update Script (PowerShell)
    自动检查远程仓库是否有更新，若有则同步到本地

.DESCRIPTION
    特性:
      - TTL 缓存 (24h)，缓存命中时跳过网络请求
      - -Force  跳过缓存，立即联网检查
      - -Background  后台执行同步，不阻塞主流程
      - 网络操作加超时 (Invoke-WebRequest -TimeoutSec)
      - 增量下载：比对 VERSION 后用 GitHub compare API 仅拉取变更文件（清单过大或异常时回退整仓 ZIP）
#>
param(
    [string]$SkillDir = "$PSScriptRoot\..",
    [string]$RepoUrl = "https://github.com/BluesilveEmperor/math-read-do",
    [switch]$Force,
    [switch]$Background
)

Write-Host "`n📦 检查 skill 更新..." -ForegroundColor Cyan

# ---------- paths ----------
$VersionFile = Join-Path $SkillDir "VERSION"
$RemoteVersionUrl = "$RepoUrl/raw/main/VERSION"
$ZipUrl = "$RepoUrl/archive/refs/heads/main.zip"
$TempZip = Join-Path $env:TEMP "math-read-do-update.zip"
$TempExtract = Join-Path $env:TEMP "math-read-do-update"

# ---------- TTL 缓存配置 ----------
$CacheDir = Join-Path $SkillDir ".cache"
$CacheFile = Join-Path $CacheDir "update_cache.json"
$TtlSeconds = 86400  # 24 小时

# ---------- 缓存读取 ----------
function Test-CacheValid {
    if ($Force) { return $false }
    if (-not (Test-Path $CacheFile)) { return $false }
    try {
        $cache = Get-Content $CacheFile -Raw | ConvertFrom-Json
        $age = (Get-Date) - ([datetime]$cache.last_check)
        return ($age.TotalSeconds -lt $TtlSeconds)
    } catch {
        return $false
    }
}

function Write-Cache {
    param([string]$RemoteVersion)
    if (-not (Test-Path $CacheDir)) { New-Item -Path $CacheDir -ItemType Directory -Force | Out-Null }
    $cacheObj = @{
        last_check    = (Get-Date).ToUniversalTime().ToString("o")
        branch        = "main"
        remote_version = $RemoteVersion
    }
    $cacheObj | ConvertTo-Json | Set-Content -Path $CacheFile -Encoding UTF8
}

# ---------- 缓存检查 ----------
if (Test-CacheValid) {
    Write-Host "  ✅ 缓存有效（24h 内已检查），跳过网络请求" -ForegroundColor Green
    Write-Host "  提示: 使用 -Force 立即联网检查" -ForegroundColor Cyan
    return
}

# ---------- 后台模式 ----------
if ($Background) {
    Write-Host "  🔄 后台启动更新检查..." -ForegroundColor Yellow
    Start-Process -FilePath "powershell" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -SkillDir `"$SkillDir`" -Force" -WindowStyle Hidden
    return
}

# ---------- read local version ----------
$LocalVersion = ""
if (Test-Path $VersionFile) {
    $LocalVersion = (Get-Content $VersionFile -Raw).Trim()
}

if (-not $LocalVersion) {
    Write-Host "  ⚠️  未找到本地 VERSION 文件, 跳过更新" -ForegroundColor Yellow
    return
}

# ---------- fetch remote version（超时 10s）----------
try {
    $RemoteVersion = (Invoke-WebRequest -Uri $RemoteVersionUrl -UseBasicParsing -TimeoutSec 10).Content.Trim()
} catch {
    Write-Host "  ⚠️  无法访问远程仓库 (网络或仓库不可达, 超时 10s), 跳过更新" -ForegroundColor Yellow
    Write-Cache -RemoteVersion "unknown"
    return
}

# ---------- 更新缓存 ----------
Write-Cache -RemoteVersion $RemoteVersion

if ($LocalVersion -eq $RemoteVersion) {
    Write-Host "  ✅ 已是最新版本 ($LocalVersion)" -ForegroundColor Green
    return
}

# ---------- update needed (incremental) ----------
Write-Host "  🔄 发现新版本: $LocalVersion → $RemoteVersion" -ForegroundColor Cyan
Write-Host "  ⬇️  正在增量下载变更文件..." -ForegroundColor Cyan

try {
    # 用 GitHub compare API 获取两版本之间的文件变更清单（超时 15s）
    $CompareUrl = "https://api.github.com/repos/BluesilveEmperor/math-read-do/compare/$LocalVersion...$RemoteVersion"
    $CompareResp = Invoke-WebRequest -Uri $CompareUrl -UseBasicParsing -TimeoutSec 15
    $CompareJson = $CompareResp.Content | ConvertFrom-Json

    $ChangedFiles = @($CompareJson.files)
    $IsTruncated = [bool]$CompareJson.truncated

    # 降级：compare 结果被截断或无 files → 回退整仓 ZIP 下载
    if ($IsTruncated -or $ChangedFiles.Count -eq 0) {
        Write-Host "  ⚠️  变更清单过大或为空 (truncated=$IsTruncated), 回退整仓 ZIP 下载" -ForegroundColor Yellow
        # download ZIP（超时 60s）
        Invoke-WebRequest -Uri $ZipUrl -OutFile $TempZip -UseBasicParsing -TimeoutSec 60

        # clean & extract
        if (Test-Path $TempExtract) { Remove-Item -Path $TempExtract -Recurse -Force }
        Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force

        # find the extracted root (repo name may include branch name)
        $ExtractedDirs = Get-ChildItem -Path $TempExtract -Directory
        if ($ExtractedDirs.Count -eq 0) {
            throw "ZIP 解压后未找到目录"
        }
        $ExtractedRoot = $ExtractedDirs[0].FullName

        # copy all files (except VERSION to avoid mid-update corruption)
        Copy-Item -Path "$ExtractedRoot\*" -Destination $SkillDir -Recurse -Force -ErrorAction Stop
    } else {
        # 增量：逐个下载变更文件（added/modified/changed/renamed 下载，removed 删除）
        $added = 0; $modified = 0; $removed = 0
        foreach ($f in $ChangedFiles) {
            $relPath = $f.filename
            $status = $f.status
            $destPath = Join-Path $SkillDir $relPath

            if ($status -eq "removed") {
                if (Test-Path $destPath) { Remove-Item -Path $destPath -Force -ErrorAction SilentlyContinue }
                $removed++
            } else {
                # added / modified / changed / renamed
                $parentDir = Split-Path -Parent $destPath
                if (-not (Test-Path $parentDir)) { New-Item -Path $parentDir -ItemType Directory -Force | Out-Null }
                # 下载单个文件 raw 内容（超时 20s）
                Invoke-WebRequest -Uri $f.raw_url -OutFile $destPath -UseBasicParsing -TimeoutSec 20
                if ($status -eq "added") { $added++ } else { $modified++ }
            }
        }
        Write-Host "  📊 增量结果: 新增 $added, 修改 $modified, 删除 $removed" -ForegroundColor Cyan
    }

    # re-write VERSION with new SHA
    $RemoteVersion | Set-Content -Path $VersionFile -NoNewline -Encoding ASCII

    Write-Host "  ✅ 更新完成: $RemoteVersion" -ForegroundColor Green

    # ---------- changelog（来自 compare 结果）----------
    $Commits = $CompareJson.commits
    if ($Commits -and $Commits.Count -gt 0) {
        Write-Host "`n  📋 更新亮点:" -ForegroundColor Cyan
        foreach ($c in $Commits) {
            $shortSha = $c.sha.Substring(0, 7)
            $msg = $c.commit.message -replace "`n.*", ""
            Write-Host "    • [$shortSha] $msg" -ForegroundColor White
        }
    }

} catch {
    Write-Host "  ❌ 更新失败: $_" -ForegroundColor Red
    Write-Host "  ⚠️  已保留旧版本, 不影响本次任务" -ForegroundColor Yellow
} finally {
    # cleanup temp files
    if (Test-Path $TempZip) { Remove-Item $TempZip -Force -ErrorAction SilentlyContinue }
    if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue }
}