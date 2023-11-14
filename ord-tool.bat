@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul



::*****************作者个人信息***************************
::       author : wusimpl                               ::
::         date : 2023.11.11                            ::
::       version: v0.9                                  ::
::       contact: https://twitter.com/wusimpl           ::
::********************************************************


::*******************************可改动区域*******************************************************
rem 比特币全节点数据目录
set BITCOIN_DATA_DIR=D:\bitcoin\blockdata

rem ord索引目录（index.redb所在目录）
set ORDDATA_DIR=C:\ordindex

rem 比特币节点cookie文件的路径（一般在比特币全节点根目录下）
rem set COOKIE_PATH=C:\Users\wusimpl\bitcoin_index_data\.cookie

rem ord命令行工具的目录（尾部请不要加\）
set ORD_CLI_DIR=D:\bitcoin\ord-0.10.0

rem 连接比特币节点的rpc url
rem set RPC_URL=--rpc-url http://localhost:8332
set RPC_URL=--rpc-url http://10.110.87.78:8332

rem 除了cookie的第二种认证方式，任选一种，另外一种留空就行
set AUTH=--bitcoin-rpc-pass 80308400 --bitcoin-rpc-user wusimpl
::**************************************************************************************************


::*************************必看的说明****************************

:: 第三个功能【显示地址】需要有python环境，没有python的自己安装

:: python下载地址：https://www.python.org/downloads/

::****************************************************************


set COOKIE=--cookie-file %COOKIE_PATH%
if NOT "%COOKIE_PATH%"=="" (
	set ORD_BASE_CMD=ord --bitcoin-data-dir %BITCOIN_DATA_DIR% --data-dir %ORDDATA_DIR% %RPC_URL% %COOKIE%
) else (
	set ORD_BASE_CMD=ord --bitcoin-data-dir %BITCOIN_DATA_DIR% --data-dir %ORDDATA_DIR% %RPC_URL% %AUTH%
)
echo %ORD_BASE_CMD%
:menu
rem cls
echo *************************************************************************
echo *                                                                       *
echo *                          Ord管理工具                                  *
echo *                                                                       *
echo *                                                                       *
echo *    [1] 创建钱包          [2] 导入钱包          [3] 显示地址           *
echo *                                                                       *
echo *    [4] mint BRC20铭文    [5] 查看铭文          [6] 发送铭文           *
echo *                                                                       *
echo *    [7] 查看待处理交易    [8] 查看钱包余额      [0] 退出               *
echo *                                                                       *
echo *    [9] 以文件方式mint Ordinals                                        * 
echo *                                                                       *
echo *                                                                       *
echo *************************************************************************
echo.
set /p choice=请输入选项数字:

if "%choice%"=="1" goto create_wallet
if "%choice%"=="2" goto import_wallet
if "%choice%"=="3" goto generate_address
if "%choice%"=="4" goto create_inscription
if "%choice%"=="5" goto view_inscriptions
if "%choice%"=="6" goto send_inscription
if "%choice%"=="7" goto view_transactions
if "%choice%"=="8" goto view_ord_balance
if "%choice%"=="9" goto mint_ordinals
if "%choice%"=="0" exit

echo 无效选项，请重新输入。
rem pause
goto menu


:create_wallet
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)
%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet create
pause
goto menu



:import_wallet
set /p seed_phrase=请输入BIP39种子短语:
set /p wallet_name=请为钱包命名:
%ORD_BASE_CMD% --wallet %wallet_name% wallet restore "%seed_phrase%"
pause
goto menu



:generate_address
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)
set json_address_full_path=%ORD_CLI_DIR%\address.json
%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet receive > %json_address_full_path%
type %json_address_full_path%
for /f "delims=" %%i in ('echo %btc_address% ^| python %ORD_CLI_DIR%\get_address.py %json_address_full_path%') do set ADDRESS=%%i

pip install qrcode > nul 2>&1
pip install pillow > nul 2>&1
pip install qrcode-terminal > nul 2>&1
python -c "import qrcode_terminal; qrcode_terminal.draw('%ADDRESS%')"
pause
goto menu



:create_inscription
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)

set /p tick=tick:
set /p amt=amount（留空则默认1000）:
if "%amt%"=="" (
	set amt=1000
)

set token_file={"p":"brc20","op":"mint","tick":"%tick%","amt":"%amt%"}
echo 铭文文件信息：%token_file%
echo %token_file% > token.txt

set /p repeat_mint=重复mint的数量（留空则默认只打1张）：
if "%repeat_mint%"=="" (
	set repeat_mint=1
)

call :fetch_fees
set /p fee_rate=请指定fee_rate:
if "%fee_rate%"=="" (
	set fee_rate=20
)
echo.
set ORD_CMD=%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet inscribe --file token.txt --fee-rate %fee_rate%
echo 执行命令：%ORD_CMD%
echo.
echo.

set counter=1
:mint_loop
if %counter% leq %repeat_mint% (
	echo 正在mint第%counter%张...
	set /a counter=%counter% + 1
	call %ORD_CMD%
	goto mint_loop
)

pause
rem del token.txt ;no need to delete this file actually
goto menu


:mint_ordinals
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)


set /p file_path=文件路径（最好是全路径）:

set /p repeat_mint=重复mint的数量（留空则默认只打1张）：
if "%repeat_mint%"=="" (
	set repeat_mint=1
)

call :fetch_fees
set /p fee_rate=请指定fee_rate:
if "%fee_rate%"=="" (
	set fee_rate=20
)
echo.
set ORD_CMD=%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet inscribe --file %file_path% --fee-rate %fee_rate%
echo 执行命令：%ORD_CMD%
echo.
echo.

set counter=1
:mint_loop
if %counter% leq %repeat_mint% (
	echo 正在mint第%counter%张...
	set /a counter=%counter% + 1
	call %ORD_CMD%
	goto mint_loop
)

pause
rem del token.txt ;no need to delete this file actually
goto menu


:view_inscriptions
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)
%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet inscriptions
pause
goto menu

:send_inscription
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)

set /p fee_rate=请指定fee_rate:
if "%fee_rate%"=="" (
	set fee_rate=20
)

set /p address=请输入接收地址:
call :fetch_fees
set /p inscription_id=请输入铭文ID:
%ORD_BASE_CMD% wallet send --fee-rate %fee_rate% %address% %inscription_id%
pause
goto menu

:view_transactions
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)
%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet transactions
pause
goto menu

:view_ord_balance
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)
echo **********************************
%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet balance
echo 提示：该余额不包含铭文中所携带的聪
echo **********************************

pause
goto menu


:view_sats_balance
set /p wallet_name=请输入钱包名称（留空则为ord）:
if "%wallet_name%"=="" (
	set wallet_name=ord
)
%ORD_BASE_CMD% --wallet %WALLET_NAME% wallet sats
pause
goto menu

:: 获取费率函数
:fetch_fees
echo 正在获取链上gas price...
for /f "delims=" %%a in ('curl -sSL "https://mempool.space/api/v1/fees/recommended"') do set fees=%%a
echo.
echo 当前链上费率(sats/vB)：%fees%
echo.
goto:eof

