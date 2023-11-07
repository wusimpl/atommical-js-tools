@echo off

chcp 65001 > nul


:: 版本 v1.0
:: 作者 wusmpl
:: 推特 twitter.com/wusimpl
:: 日期 2023/11/07


:mainMenu

echo ================================


echo     Atomicals 管理工具主菜单

echo ================================

echo 1. 帮助        2. 钱包 

echo 3. Atomicals   0. 退出

echo.

set /p choice=输入选项编号:

if "%choice%"=="0" exit

if "%choice%"=="1" goto helpOptions

if "%choice%"=="2" goto walletOperations

rem if "%choice%"=="3" goto addressOperations

if "%choice%"=="3" goto atomicalOperations

rem if "%choice%"=="5" goto realmOperations

goto mainMenu



:helpOptions

echo.

echo ================================

echo          帮助子菜单

echo ================================

echo 1. 输出版本号

echo 2. 显示命令帮助

echo 3. 获取electrumx服务器版本信息

echo 0. 返回主菜单

echo.


set /p choice=输入选项编号:



if "%choice%"=="1" call yarn cli --version && goto helpOptions

if "%choice%"=="2" call yarn cli --help  && goto helpOptions

if "%choice%"=="3" call yarn cli server-version  && goto helpOptions

if "%choice%"=="0" goto mainMenu

goto helpOptions




:walletOperations

echo.

echo ================================

echo        钱包操作子菜单

echo ================================

rem echo 1. 创建钱包

echo 1. 初始化主钱包/创建主钱包

echo 2. 使用助记词导出私钥

echo 3. 导入私钥地址（私钥钱包）

echo 4. 获取地址信息

echo 0. 返回主菜单

echo.



set /p choice=输入选项编号:

rem if "%choice%"=="1" call yarn cli wallet-create && goto walletOperations

if "%choice%"=="1" call yarn cli wallet-init && goto walletOperations

if "%choice%"=="2" goto decodeWallet

if "%choice%"=="3" goto importWallet

if "%choice%"=="4" goto getAddressInfo

if "%choice%"=="0" goto mainMenu

goto walletOperations





:atomicalOperations

echo ================================

echo       Atomical 操作子菜单

echo ================================

echo 1. 获取主钱包详细信息

echo 2. 获取被导入钱包详细信息

echo 3. 获取所有钱包的Atomicals数量

echo 4. 获取领域或子领域信息

echo 5. mint 领域

echo 6. mint NFT（atommap）

rem echo 2. 获取钱包余额和Atomcials存储情况

rem echo 3. 显示ticker代码分类的代币摘要

rem echo 4. 更新Atomical数据

echo 0. 返回主菜单

set /p choice=输入选项编号:

if "%choice%"=="1" call yarn cli wallets && goto atomicalOperations

rem if "%choice%"=="2" call yarn cli balances && goto atomicalOperations

if "%choice%"=="2" goto yarn cli wallets --balances && goto atomicalOperations

if "%choice%"=="3" goto getImportedAddressInfo

if "%choice%"=="4" goto resolveRealm

rem if "%choice%"=="3" goto summarySubrealms

if "%choice%"=="5" goto mintRealms
if "%choice%"=="6" goto mintNFT

rem if "%choice%"=="3" call yarn cli summary-tickers && goto atomicalOperations

rem if "%choice%"=="4" goto setAtomicalData

if "%choice%"=="0" goto mainMenu

goto atomicalOperations





:getImportedAddressInfo:
set /p WalletAlias=钱包别名:
yarn cli wallets --alias %WalletAlias%
goto atomicalOperations


:realmOperations
echo deleted


:summarySubrealms
call yarn cli summary-subrealms
goto realmOperations


:decodeWallet

echo 请输入助记词短语:

set /p phrase=助记词短语:

call yarn cli wallet-decode "%phrase%"

goto walletOperations



:importWallet

set /p wif=WIF私钥:

set /p alias=给钱包取一个别名:

call yarn cli wallet-import "%wif%" "%alias%"

goto walletOperations



:encodeScript

set /p addressOrAlias=地址/别名:

call yarn cli address-script "%addressOrAlias%"

goto addressOperations



:decodeScript

set /p script=脚本:

call yarn cli script-address "%script%"

goto addressOperations



:decodeCompact

set /p hex=十六进制输出点:

call yarn cli outpoint-compact "%hex%"

goto addressOperations



:encodeCompact

set /p compactId=紧凑ID:

call yarn cli compact-outpoint "%compactId%"

goto addressOperations



:getAddressInfo

set /p address=地址:

call yarn cli address "%address%"

goto walletOperations



:setAtomicalData

set /p atomicalIdAlias=Atomical ID/别名:

echo 请输入JSON文件名:

set /p jsonFilename=JSON文件名:

call yarn cli set "%atomicalIdAlias%" "%jsonFilename%"

goto atomicalOperations



:resolveRealm


set /p realm_or_subrealm=领域/子领域名称:

call yarn cli resolve "%realm_or_subrealm%"

goto atomicalOperations


:mintRealms

set /p realm=领域名称:
call :fetch_fees
set /p fee=请输入费率(想要快速上链就多给一些): %fee_rate%
set /a satsbyte=fee*1000/1700 + 1
call yarn cli mint-realm --satsbyte %satsbyte% %realm%
goto atomicalOperations


:mintNFT
set /p NFT_FILE_PATH=atommap svg 路径（最好使用全路径）:
set /p ATOMMAP_ID=atommap id:
call :fetch_fees
set /p fee=请输入费率(想要快速上链就多给一些): %fee_rate%
set /a satsbyte=fee*1000/1700 + 1
call yarn cli mint-nft %NFT_FILE_PATH% --satsbyte %satsbyte%  --satsoutput 546 --bitworkc ab%ATOMMAP_ID%
goto atomicalOperations



:fetch_fees
for /f "delims=" %%a in ('curl -sSL "https://mempool.space/api/v1/fees/recommended"') do set fee=%%a
echo %fee% > temp.json

del temp.json
echo ============================================================================================================

echo  当前费率（单位：sats/vB）: %fee%

echo ============================================================================================================
echo.


:end
endlocal

