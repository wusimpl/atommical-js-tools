#!/usr/bin/env python
# coding=utf-8
import re
import subprocess
import json
import os


'''
脚本作者:             wusimpl
日期:                2023.12.8
个人推特:             @wusimpl
atomicals-js 版本:   v0.1.58
ajs-tool 版本:       v1.7

注意: 开源脚本，风险自负！
'''

def sharp_print(s):
    length = len(s)
    # 创建一个由#组成的字符串，长度与输入字符串相同
    sharp_line = '#' * length
    # 打印结果
    print(sharp_line + '\n' + s + '\n' + sharp_line)

def run_command(command):
    print("执行命令："+command)
    return subprocess.run(command, stdout=subprocess.PIPE,shell=True,text=True)
    
def run_command_with_console_output(command):
    print("执行命令："+command)
    return subprocess.run(command, shell=True,text=True)

def main_menu():
    while True:
        print("=========================================")
        print("=                                       =")
        print("=         Atomicals 管理工具            =")
        print("=                                       =")
        print("=      1. 帮助         2. 钱包          =")
        print("=                                       =")
        print("=      3. Atomicals    0. 退出          =")
        print("=                                       =")
        print("=========================================")

        choice = input("输入选项编号: ")

        if choice == "0":
            exit()
        elif choice == "1":
            help_options()
        elif choice == "2":
            wallet_operations()
        elif choice == "3":
            atomical_operations()

def help_options():
    while True:
        print("======================================================")
        print("                    帮助子菜单")
        print("")
        print("")
        print("        1. CLI 版本号     2. 显示命令帮助")
        print("")
        print("        0. 返回主菜单     3. 获取electrumx服务器版本信息")
        print("")
        print("        作者：wusimpl     twitter：@wusimpl")
        print("======================================================")

        choice = input("输入选项编号: ")

        if choice == "1":
            run_command_with_console_output("yarn cli --version")
        elif choice == "2":
            run_command_with_console_output("yarn cli --help")
        elif choice == "3":
            run_command_with_console_output("yarn cli server-version")
        elif choice == "0":
            break

def wallet_operations():
    while True:
        print("============================================================")
        print("                     钱包操作子菜单")
        print("")
        print("")
        print("    1. 初始化主钱包/创建主钱包      2. 使用助记词导出私钥")
        print("")
        print("    3. 导入私钥地址（私钥钱包）     4. 获取地址信息")
        print("")
        print("    0. 返回主菜单")
        print("============================================================")

        choice = input("输入选项编号: ")

        if choice == "1":
            run_command_with_console_output("yarn cli wallet-init")
        elif choice == "2":
            decode_wallet()
        elif choice == "3":
            import_wallet()
        elif choice == "4":
            get_address_info()
        elif choice == "0":
            break

def decode_wallet():
    phrase = input("请输入助记词短语: ")
    run_command_with_console_output(f"yarn cli wallet-decode \"{phrase}\"")

def import_wallet():
    wif = input("WIF私钥: ")
    alias = input("给钱包取一个别名: ")
    run_command_with_console_output(f"yarn cli wallet-import \"{wif}\" \"{alias}\"")

def get_address_info():
    address = input("地址: ")
    run_command_with_console_output(f"yarn cli address \"{address}\"")

def atomical_operations():
    while True:
        print("================================================================================")
        print("                                 Atomicals 操作子菜单")
        print("")
        print("")
        print("     1. 获取主钱包详细信息             2. 获取被导入钱包详细信息")
        print("")
        print("     3. 获取领域或子领域信息           4. mint 领域（Realm）")
        print("")
        print("     5. mint NFT（mint-nft）           6. mint FT（ARC20 Token）")
        print("")
        print("     7. mint Container Item（dmint）   0. 返回主菜单")
        print("================================================================================")

        choice = input("输入选项编号: ")

        if choice == "1":
            run_command_with_console_output("yarn cli wallets")
        elif choice == "2":
            get_imported_address_info()
        elif choice == "3":
            resolve_realm()
        elif choice == "4":
            mint_realms()
        elif choice == "5":
            mint_nft()
        elif choice == "6":
            mint_dft()
        elif choice == "7":
            mint_container_items()
        elif choice == "0":
            break

def get_imported_address_info():
    wallet_alias = input("钱包别名: ")
    run_command_with_console_output(f"yarn cli wallets --alias {wallet_alias}")

def resolve_realm():
    realm_or_subrealm = input("领域/子领域名称:")
    run_command_with_console_output(f"yarn cli resolve \"{realm_or_subrealm}\"")

def mint_realms():
    while True:
        realm = input("领域名称: ")
        if realm:
            break
        print("领域名称不能为空！")

    sender = input("使用哪个钱包发送交易并接收零钱（留空则默认为funding address")
    receiver = input("atommical接收地址（留空则默认为primary address）：")

    while True:
        satsoutput = input("satsoutput（留空则默认为1000）：")
        if satsoutput:
            try:
                satsoutput = int(satsoutput)
                break
            except ValueError:
                print("请输入有效的数字！")
        else:
            satsoutput = 1000
            break

    fee_rate = input("请输入手续费率（单位：satsbyte，留空则默认40）：")
    if not fee_rate:
        fee_rate = "40"
    satsbyte = fee_rate

    mint_realm_cmd = f"yarn cli mint-realm --satsbyte {satsbyte} {realm}"
    if sender:
        mint_realm_cmd += f" --funding {sender}"
    if receiver:
        mint_realm_cmd += f" --initialowner {receiver}"
    if satsoutput:
        mint_realm_cmd += f" --satsoutput {satsoutput}"

    run_command_with_console_output(mint_realm_cmd)


def mint_nft():
    while True:
        nft_file_path = input("文件路径（最好使用全路径）: ")
        
        if nft_file_path:
            if os.path.exists(nft_file_path):
                break
            else:
                print("文件不存在！")
        else:
            print("不可为空！")

    while True:
        bitworkc = input("bitworkc: ")
        if bitworkc:
            break
        print("不能为空！")
    

    while True:
        satsoutput = input("satsoutput（留空则默认1000）: ")
        if satsoutput:
            try:
                satsoutput = int(satsoutput)
                break
            except ValueError:
                print("请输入有效的数字！")
        else:
            satsoutput = 1000
            break

    sender = input("使用哪个钱包发送交易并接收零钱？留空则默认为funding address: ")
    receiver = input("atommical接收地址（留空则默认为primary address）：")

    fee_rate = input("请输入手续费率（单位：satsbyte，留空则默认40）：")
    if not fee_rate:
        fee_rate = "40"
    satsbyte = fee_rate

    mint_nft_cmd = f"yarn cli mint-nft {nft_file_path} --bitworkc {bitworkc} --satsbyte {satsbyte}"
    if satsoutput:
        mint_nft_cmd += f" --satsoutput {satsoutput}"
    if sender:
        mint_nft_cmd += f" --funding {sender}"
    if receiver:
        mint_nft_cmd += f" --initialowner {receiver}"

    run_command_with_console_output(mint_nft_cmd)


def mint_dft():
    while True:
        ticker = input("ticker name: ")
        if ticker:
            break
        print("Ticker名称不能为空！")

    sender = input("使用哪个钱包发送交易并接收零钱（留空则默认为funding address）: ")
    receiver = input("atommical接收地址（留空则默认为primary address）：")
    
    while True:
        repeat_mint = input("重复mint的数量（留空则默认只打1张）：")
        if repeat_mint:
            try:
                repeat_mint = int(repeat_mint)
                break
            except ValueError:
                print("请输入有效的数字！")
        else:
            repeat_mint = 1
            break
    
    disable_chalk = input("是否禁用挖矿过程中每个哈希值的实时记录以提高挖矿性能（y：不禁用，留空：禁用）：")
    fee_rate = input("请输入手续费率（单位：satsbyte，留空则默认40）：")

    mint_dft_cmd = f"yarn cli mint-dft {ticker}"
    if sender:
        mint_dft_cmd += f" --funding {sender}"
    if receiver:
        mint_dft_cmd += f" --initialowner {receiver}"
    if fee_rate:
        mint_dft_cmd += f" --satsbyte {fee_rate}"
    else:
        mint_dft_cmd += f" --satsbyte 40"
    if disable_chalk:
        mint_dft_cmd += f" --disablechalk"

    for i in range(repeat_mint):
        print(f"正在mint第{i + 1}张...")
        run_command_with_console_output(mint_dft_cmd)


def mint_container_items():
    print("⚠️  请注意，此功能暂时不支持二次支付 ⚠️")
    while(True):
        container_name = input("container name: ")
        if container_name:
            break
    
    while(True):
        while(True):
            item_name = input("item 编号: ")
            if item_name:
                break
        print("正在查重...")
        result = run_command(f"yarn cli get-container-item \"{container_name}\" \"{item_name}\"")
        container_item_status_output = result.stdout
        
        start = container_item_status_output.find('{')
        end = container_item_status_output.rfind('}')

        if start != -1 and end != -1 and end > start:
            substring = container_item_status_output[start:end + 1]
            status_json=json.loads(substring)
            print(json.dumps(status_json,indent=2))
            if status_json['data']['status'] is not None:
                sharp_print(f"{item_name} 已经被mint，请重新选择 item name")
                continue
            else:
                sharp_print(f"{item_name} is ok to mint")
                break
        else:
            sharp_print("status json not found, exit.")
            exit()
        
    
    while(True):
        manifest_file_path = input("清单文件路径（json文件，最好使用全路径）：")
        if manifest_file_path:
            if os.path.exists(manifest_file_path):
                break
            else:
                print("文件不存在！")
        else:
            print("不可为空！")
    sender =        input("使用哪个钱包发送交易并接收零钱（留空则默认为funding address）: ")
    receiver =      input("atommical接收地址（留空则默认为primary address）：")
    fee_rate =      input("请输入手续费率（单位：sats/byte，留空则默认40）：")
    disable_chalk = input("是否禁用挖矿过程中每个哈希值的实时记录以提高挖矿性能（y：不禁用，留空：禁用）：")
    bitworkc =      input("bitworkc工作量证明字符串（留空则默认不使用，如果你不理解此项，请留空）：")

    dmint_cmd = f"yarn cli mint-item {container_name} {item_name} {manifest_file_path}"
    
    if sender:
        dmint_cmd += f" --funding {sender}"
    if receiver:
        dmint_cmd += f" --initialowner {receiver}"
    if fee_rate:
        dmint_cmd += f" --satsbyte {fee_rate}"
    else:
        dmint_cmd += f" --satsbyte 40"
    if disable_chalk:
        dmint_cmd += f" --disablechalk"
    if bitworkc:
        dmint_cmd += f" --bitworkc {bitworkc}"
        
    run_command_with_console_output(dmint_cmd)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n已强行终止脚本.")
