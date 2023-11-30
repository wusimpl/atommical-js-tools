@echo off

chcp 65001 > nul


:: 版本 v1.6
:: 作者 wusmpl
:: 推特 twitter.com/wusimpl
:: 日期 2023/12/01


:mainMenu

echo =========================================
echo =                                       =
echo =         Atomicals 管理工具            =
echo =                                       =
echo =                                       =
echo =      1. 帮助         2. 钱包          =
echo =                                       =
echo =      3. Atomicals    0. 退出          =
echo =                                       =
echo =========================================

echo.

set /p choice=输入选项编号:

if "%choice%"=="0" exit

if "%choice%"=="1" goto helpOptions

if "%choice%"=="2" goto walletOperations

if "%choice%"=="3" goto atomicalOperations


goto mainMenu



:helpOptions

echo.

echo ======================================================
echo.
echo                    帮助子菜单
echo.
echo.
echo        1. 输出版本号   2. 显示命令帮助
echo.
echo        0. 返回主菜单   3. 获取electrumx服务器版本信息   
echo.
echo.
echo ======================================================


set /p choice=输入选项编号:



if "%choice%"=="1" call yarn cli --version && goto helpOptions

if "%choice%"=="2" call yarn cli --help  && goto helpOptions

if "%choice%"=="3" call yarn cli server-version  && goto helpOptions

if "%choice%"=="0" goto mainMenu

goto helpOptions




:walletOperations

echo.

echo =============================================================
echo. 
echo                     钱包操作子菜单
echo.
echo    1. 初始化主钱包/创建主钱包      2. 使用助记词导出私钥
echo.
echo    3. 导入私钥地址（私钥钱包）     4. 获取地址信息
echo.
echo    0. 返回主菜单
echo.
echo =============================================================




set /p choice=输入选项编号:

if "%choice%"=="1" call yarn cli wallet-init && goto walletOperations

if "%choice%"=="2" goto decodeWallet

if "%choice%"=="3" goto importWallet

if "%choice%"=="4" goto getAddressInfo

if "%choice%"=="0" goto mainMenu

goto walletOperations





:atomicalOperations

echo ================================================================================================
echo.
echo                                   Atomicals 操作子菜单
echo.
echo     1. 获取主钱包详细信息       2. 获取被导入钱包详细信息        3. 获取所有钱包的Atomicals数量
echo.
echo     4. 获取领域或子领域信息     5. mint 领域（Realm）            6. mint NFT（mint-nft）
echo.
echo     7. mint FT（ARC20 Token）   8. mint Container Item（dmint）  0. 返回主菜单
echo.
echo ================================================================================================




set /p choice=输入选项编号:

if "%choice%"=="1" call yarn cli wallets && goto atomicalOperations

rem if "%choice%"=="2" call yarn cli balances && goto atomicalOperations

if "%choice%"=="2" goto getImportedAddressInfo

if "%choice%"=="3" echo sorry, this function is deleted && goto atomicalOperations

if "%choice%"=="4" goto resolveRealm

rem if "%choice%"=="3" goto summarySubrealms

if "%choice%"=="5" goto mintRealms
if "%choice%"=="6" goto mintNFT
if "%choice%"=="7" goto mintDFT
if "%choice%"=="8" goto mintContainerItems

rem if "%choice%"=="3" call yarn cli summary-tickers && goto atomicalOperations

rem if "%choice%"=="4" goto setAtomicalData

if "%choice%"=="0" goto mainMenu

goto atomicalOperations





:getImportedAddressInfo:
set /p WalletAlias=钱包别名:
call yarn cli wallets --alias %WalletAlias%
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
set MINT_REALM_CMD=yarn cli mint-realm

set /p realm=领域名称:

echo 使用哪个钱包发送交易并接收零钱？

echo 零钱即UTXO被铭刻后未花费完的资金，留空则默认为funding address，否则请填写钱包别名.
set /p receiver=钱包别名：
if NOT "%sender%"=="" (
	set MINT_REALM_CMD=%MINT_REALM_CMD% --funding %sender%
)

set /p receiver=atommical接收地址（留空则默认为primary address）：
if NOT "%receiver%"=="" (
	set MINT_REALM_CMD=%MINT_REALM_CMD% --initialowner %receiver%
)

set /p satsoutput=将多少聪铭刻在将被mint的aotommical上（留空则默认为1000）：
if NOT "%satsoutput%"=="" (
	set MINT_REALM_CMD=%MINT_REALM_CMD% --satsoutput %satsoutput%
)

call :fetch_fees
set /p fee_rate=请输入费率(想要快速上链就多给一些，默认40 sats/vB): 
if "%fee_rate%"=="" (
	set fee_rate=40
)
set /a satsbyte=fee_rate*1000/1700 + 2

call %MINT_REALM_CMD% --satsbyte %satsbyte% %realm%

goto atomicalOperations


:mintNFT
set /p NFT_FILE_PATH=文件路径（最好使用全路径）:
set MINT_NFT_CMD=yarn cli mint-nft %NFT_FILE_PATH%

set /p bitworkc=bitworkc:
set MINT_NFT_CMD=%MINT_NFT_CMD% --bitworkc %bitworkc%

set /p satsoutput=satsoutput（留空则默认1000）:
if not "%satsoutput%"=="" (
	set MINT_NFT_CMD=%MINT_NFT_CMD% --satsoutput %satsoutput%
)


echo 使用哪个钱包发送交易并接收零钱？

echo 零钱即UTXO被铭刻后未花费完的资金，留空则默认为funding address。

set /p sender=钱包别名：
if NOT "%sender%"=="" (
	set MINT_NFT_CMD=%MINT_NFT_CMD% --funding %sender%
)

set /p receiver=atommical接收地址（留空则默认为primary address）：
if NOT "%receiver%"=="" (
	set MINT_NFT_CMD=%MINT_NFT_CMD% --initialowner %receiver%
)

call :fetch_fees
set /p fee_rate=请输入费率(想要快速上链就多给一些，默认40 sats/vB): 
if "%fee_rate%"=="" (
	set fee_rate=40
)
set /a satsbyte=(fee_rate*1000)/1700 + 2

set MINT_NFT_CMD=%MINT_NFT_CMD% --satsbyte %satsbyte%

start "mint NFT %NFT_FILE_PATH%" cmd /k %MINT_NFT_CMD%
goto atomicalOperations


:mintDFT
set MINT_DFT_CMD=yarn cli mint-dft

set /p ticker=ticker name：
set MINT_DFT_CMD=%MINT_DFT_CMD% %ticker%

echo 使用哪个钱包发送交易并接收零钱？

echo 零钱即UTXO被铭刻后未花费完的资金，留空则默认为funding address。

set /p sender=钱包别名：
if NOT "%sender%"=="" (
	set MINT_DFT_CMD=%MINT_DFT_CMD% --funding %sender%
)

set /p receiver=atommical接收地址（留空则默认为primary address）：
if NOT "%receiver%"=="" (
	set MINT_DFT_CMD=%MINT_DFT_CMD% --initialowner %receiver%
)

set /p repeat_mint=重复mint的数量（留空则默认只打1张）：
if "%repeat_mint%"=="" (
	set repeat_mint=1
)

call :fetch_fees
set /p fee_rate=请输入费率(想要快速上链就多给一些，默认40 sats/vB): 
if "%fee_rate%"=="" (
	set fee_rate=40
)
set /a satsbyte=fee_rate * 1000/1700 + 2
set MINT_DFT_CMD=%MINT_DFT_CMD% --satsbyte %satsbyte%


set counter=1
:mint_loop
if %counter% leq %repeat_mint% (
	echo 正在mint第%counter%张...
	set /a counter=%counter% + 1
	start "minting %ticker% %counter%" cmd /k %MINT_DFT_CMD%
	goto mint_loop
)

goto atomicalOperations


:mintContainerItems
set /p container_name=container name（以#开头）:
:entercontainername
set /p item_name=item name:

echo 正在查询数据...
call yarn cli get-container-item "%container_name%" "%item_name%"
echo ##################################
echo 请查看上方输出中 status 的值 
echo 为 null 则可以 mint
echo 为 pending 则已被 mint 但还未确认 
echo 为 verified 则已被 mint 且验证完成
echo ##################################
set /p statusValue=status的值是否为null（y or n）:
if not "%statusValue%"=="y" (
	echo ok，已经被mint，重新输入item name 
	goto :entercontainername
) else (
	echo ok, Let's move on. 
)

set /p manifest_file=清单文件路径（json文件，最好使用全路径）：

set DMINT_CMD=yarn cli mint-item "%container_name%" "%item_name%" "%manifest_file%"

echo 使用哪个钱包发送交易并接收零钱？

echo 零钱即UTXO被铭刻后未花费完的资金，留空则默认为funding address。

set /p sender=钱包别名：
if NOT "%sender%"=="" (
	set DMINT_CMD=%DMINT_CMD% --funding %sender%
)

set /p receiver=atommical接收地址（留空则默认为primary address）：
if NOT "%receiver%"=="" (
	set DMINT_CMD=%DMINT_CMD% --initialowner %receiver%
)

call :fetch_fees
set /p fee_rate=请输入费率(想要快速上链就多给一些，默认40 sats/vB): 
if "%fee_rate%"=="" (
	set fee_rate=40
)
set /a satsbyte=fee_rate * 1000/1700 + 2
set DMINT_CMD=%DMINT_CMD% --satsbyte %satsbyte%
echo 执行命令：%DMINT_CMD%
start "dminting %container_name% %item_name%... " cmd /k %DMINT_CMD%

goto atomicalOperations


:fetch_fees

echo 正在获取链上费率（有可能会失败）...

for /f "delims=" %%a in ('curl -sSL "https://mempool.space/api/v1/fees/recommended"') do set fee=%%a
echo %fee% > temp.json

del temp.json
echo ============================================================================================================

echo  当前费率（单位：sats/vB）: %fee%

echo ============================================================================================================
echo.

endlocal

