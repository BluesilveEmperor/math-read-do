param(
    [string]$SkillDir = "$PSScriptRoot\..",
    [string]$RepoUrl = "https://github.com/BluesilveEmperor/math-read-do"
)

Write-Host "`n📦 检查 skill 更新..." -ForegroundColor Cyan

# ---------- paths ----------
$VersionFile = Join-Path $SkillDir "VERSION"
$RemoteVersionUrl = "$RepoUrl/raw/main/VERSION"
$ZipUrl = "$RepoUrl/archive/refs/heads/main.zip"
$TempZip = Join-Path $env:TEMP "math-read-do-update.zip"
$TempExtract = Join-Path $env:TEMP "math-read-do-update"

# ---------- read local version ----------
$LocalVersion = ""
if (Test-Path $VersionFile) {
    $LocalVersion = (Get-Content $VersionFile -Raw).Trim()
}

if (-not $LocalVersion) {
    Write-Host "  ⚠️  未找到本地 VERSION 文件, 跳过更新" -ForegroundColor Yellow
    return
}

# ---------- fetch remote version ----------
try {
    $RemoteVersion = (Invoke-WebRequest -Uri $RemoteVersionUrl -UseBasicParsing -TimeoutSec 10).Content.Trim()
} catch {
    Write-Host "  ⚠️  无法访问远程仓库 (网络或仓库不可达), 跳过更新" -ForegroundColor Yellow
    return
}

if ($LocalVersion -eq $RemoteVersion) {
    Write-Host "  ✅ 已是最新版本 ($LocalVersion)" -ForegroundColor Green
    return
}

# ---------- update needed ----------
Write-Host "  🔄 发现新版本: $LocalVersion → $RemoteVersion" -ForegroundColor Cyan
Write-Host "  ⬇️  正在下载更新..." -ForegroundColor Cyan

try {
    # download ZIP
    Invoke-WebRequest -Uri $ZipUrl -OutFile $TempZip -UseBasicParsing -TimeoutSec 30

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

    # re-write VERSION with new SHA
    $RemoteVersion | Set-Content -Path $VersionFile -NoNewline -Encoding ASCII

    Write-Host "  ✅ 更新完成: $RemoteVersion" -ForegroundColor Green

    # ---------- fetch changelog ----------
    $CompareUrl = "https://api.github.com/repos/BluesilveEmperor/math-read-do/compare/$LocalVersion...$RemoteVersion"
    try {
        $CompareResp = Invoke-WebRequest -Uri $CompareUrl -UseBasicParsing -TimeoutSec 10
        $CompareJson = $CompareResp.Content | ConvertFrom-Json
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
        Write-Host "  ⚠️  无法获取更新亮点 (GitHub API 限流或网络问题)" -ForegroundColor Yellow
    }

} catch {
    Write-Host "  ❌ 更新失败: $_" -ForegroundColor Red
    Write-Host "  ⚠️  已保留旧版本, 不影响本次任务" -ForegroundColor Yellow
} finally {
    # cleanup temp files
    if (Test-Path $TempZip) { Remove-Item $TempZip -Force -ErrorAction SilentlyContinue }
    if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force -ErrorAction SilentlyContinue }
}
