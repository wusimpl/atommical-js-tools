@echo off

chcp 65001 > nul



:mainMenu



echo ================================


echo     Atomicals 管理工具主菜单

echo ================================

echo 1. 帮助        2. 钱包     3. 地址

echo 4. Atomicals               0. 退出

echo.


set /p choice=输入选项编号:



if "%choice%"=="0" exit

if "%choice%"=="1" goto commonCommands

if "%choice%"=="2" goto walletOperations

if "%choice%"=="3" goto addressOperations

if "%choice%"=="4" goto atomicalOperations

rem if "%choice%"=="5" goto realmOperations

goto mainMenu



:commonCommands



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



if "%choice%"=="1" goto checkVersion

if "%choice%"=="2" call yarn cli --help  && goto commonCommands

if "%choice%"=="3" call yarn cli server-version  && goto commonCommands

if "%choice%"=="0" goto mainMenu

goto commonCommands

:checkVersion
call yarn cli --version
goto commonCommands


:walletOperations



echo.

echo ================================

echo        钱包操作子菜单

echo ================================

rem echo 1. 创建钱包

echo 2. 初始化钱包

echo 3. 导出钱包私钥

echo 4. 导入钱包

echo 0. 返回主菜单

echo.



set /p choice=输入选项编号:



rem if "%choice%"=="1" call yarn cli wallet-create && goto walletOperations

if "%choice%"=="2" call yarn cli wallet-init && goto walletOperations

if "%choice%"=="3" goto decodeWallet

if "%choice%"=="4" goto importWallet

if "%choice%"=="0" goto mainMenu

goto walletOperations



:addressOperations



echo.
echo ================================

echo        地址操作子菜单

echo ================================


echo 5. 获取地址信息

echo 0. 返回主菜单

echo.



set /p choice=输入选项编号:



rem if "%choice%"=="1" goto encodeScript

rem if "%choice%"=="2" goto decodeScript

rem if "%choice%"=="3" goto decodeCompact

rem if "%choice%"=="4" goto encodeCompact

if "%choice%"=="5" goto getAddressInfo

if "%choice%"=="0" goto mainMenu

goto addressOperations



:atomicalOperations



echo.
echo ================================

echo       Atomical 操作子菜单

echo ================================


echo 1. 获取所有钱包的详细信息

echo 2. 解析领域或子领域

echo 3. 显示子领域摘要

echo 4. mint 领域
echo 5. mint NFT

rem echo 2. 获取钱包余额和Atomcials存储情况

rem echo 3. 显示ticker代码分类的代币摘要

rem echo 4. 更新Atomical数据

echo 0. 返回主菜单

echo.



set /p choice=输入选项编号:



if "%choice%"=="1" call yarn cli wallets && goto atomicalOperations

rem if "%choice%"=="2" call yarn cli balances && goto atomicalOperations

if "%choice%"=="2" goto resolveRealm

if "%choice%"=="3" goto summarySubrealms

if "%choice%"=="4" goto mintRealms
if "%choice%"=="5" goto mintNFT

rem if "%choice%"=="3" call yarn cli summary-tickers && goto atomicalOperations

rem if "%choice%"=="4" goto setAtomicalData

if "%choice%"=="0" goto mainMenu

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

goto addressOperations



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
set /p satsbyte=矿工费率（通常是sat/vB除以1.7，想要快速上链就多给一些）:
call yarn cli mint-realm --satsbyte %satsbyte% %realm%
goto atomicalOperations


:mintNFT
set /p NFT_FILE_PATH=atommap svg 路径（最好使用全路径）:
set /p ATOMMAP_ID=atommap id:
set /p satsbyte=矿工费率（通常是sat/vB除以1.7，想要快速上链就多给一些）:
call yarn cli mint-nft %NFT_FILE_PATH% --satsbyte %satsbyte%  --satsoutput 546 --bitworkc ab%ATOMMAP_ID%
goto atomicalOperations







:end
endlocal

