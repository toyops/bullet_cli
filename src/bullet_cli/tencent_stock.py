#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯股票数据接口 Python 实现

提供了获取腾讯股票实时数据的接口，包括：
- 获取单个股票数据
- 获取多个股票数据
- 搜索股票

作者：基于 TypeScript 版本改写
日期：2025-11-25
"""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Stock:
    """股票数据类"""
    code: str          # 股票代码（统一格式，如 SH510500）
    name: str          # 股票名称
    now: float         # 现价
    low: float         # 最低价
    high: float        # 最高价
    yesterday: float   # 昨日收盘价
    percent: float     # 涨跌幅


class TencentStockAPI:
    """腾讯股票数据API"""
    
    # 交易所代码映射
    EXCHANGE_MAP = {
        'SH': 'sh',  # 上海交易所
        'SZ': 'sz',  # 深圳交易所
        'HK': 'hk',  # 香港交易所
        'US': 'us',  # 美国交易所
    }
    
    # 反向映射
    REVERSE_EXCHANGE_MAP = {
        'sh': 'SH',
        'sz': 'SZ',
        'hk': 'HK',
        'us': 'US',
    }
    
    # 默认股票数据
    DEFAULT_STOCK = Stock(
        code="",
        name="",
        now=0.0,
        low=0.0,
        high=0.0,
        yesterday=0.0,
        percent=0.0
    )
    
    @staticmethod
    def _transform_code_to_tencent(code: str) -> str:
        """
        将统一股票代码转换为腾讯格式
        
        Args:
            code: 统一代码，如 SH000001, SZ399001, HKHSI, USDJI
            
        Returns:
            腾讯代码，如 sh000001, sz399001, hkHSI, usDJI
        """
        code = code.upper()
        
        for prefix, tencent_prefix in TencentStockAPI.EXCHANGE_MAP.items():
            if code.startswith(prefix):
                stock_code = code[len(prefix):]
                # 港股和美股需要保持代码大写
                if prefix in ['HK', 'US']:
                    return tencent_prefix + stock_code
                else:
                    return tencent_prefix + stock_code.lower()
        
        raise ValueError(f"不支持的股票代码格式: {code}")
    
    @staticmethod
    def _transform_code_from_tencent(code: str, exchange_type: str) -> str:
        """
        将腾讯股票代码转换为统一格式
        
        Args:
            code: 股票代码（不含交易所前缀）
            exchange_type: 交易所类型 (sh, sz, hk, us)
            
        Returns:
            统一代码，如 SH000001, SZ399001
        """
        if exchange_type in TencentStockAPI.REVERSE_EXCHANGE_MAP:
            prefix = TencentStockAPI.REVERSE_EXCHANGE_MAP[exchange_type]
            return prefix + code
        
        return code
    
    @staticmethod
    def _parse_stock_data(code: str, params: List[str]) -> Stock:
        """
        解析股票数据
        
        Args:
            code: 统一股票代码
            params: 数据参数列表（按~分隔）
            
        Returns:
            股票数据对象
        """
        try:
            name = params[1] if len(params) > 1 else ""
            now = float(params[3]) if len(params) > 3 and params[3] else 0.0
            yesterday = float(params[4]) if len(params) > 4 and params[4] else 0.0
            high = float(params[33]) if len(params) > 33 and params[33] else 0.0
            low = float(params[34]) if len(params) > 34 and params[34] else 0.0
            
            # 计算涨跌幅
            percent = (now / yesterday - 1) if yesterday != 0 else 0.0
            
            return Stock(
                code=code.upper(),
                name=name,
                now=now,
                low=low,
                high=high,
                yesterday=yesterday,
                percent=percent
            )
        except (IndexError, ValueError) as e:
            print(f"解析股票数据出错: {e}")
            return Stock(
                code=code.upper(),
                name="",
                now=0.0,
                low=0.0,
                high=0.0,
                yesterday=0.0,
                percent=0.0
            )
    
    @staticmethod
    def get_stock(code: str) -> Stock:
        """
        获取单个股票的实时数据
        
        Args:
            code: 股票代码（统一格式），如 SH000001, SZ399001, HKHSI, USDJI
            
        Returns:
            股票数据对象
            
        示例:
            >>> stock = TencentStockAPI.get_stock("SH510500")
            >>> print(f"{stock.name}: {stock.now}")
        """
        try:
            # 转换代码
            tencent_code = TencentStockAPI._transform_code_to_tencent(code)
            
            # 请求数据
            url = f"https://qt.gtimg.cn/q={tencent_code}"
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'  # 腾讯接口使用GBK编码
            
            # 解析数据
            body = response.text
            rows = body.split(';\n')
            
            if not rows or not rows[0]:
                return Stock(code=code, name="", now=0.0, low=0.0, high=0.0, yesterday=0.0, percent=0.0)
            
            row = rows[0]
            
            # 检查是否包含有效数据
            if tencent_code not in row:
                return Stock(code=code, name="", now=0.0, low=0.0, high=0.0, yesterday=0.0, percent=0.0)
            
            # 提取数据
            # 格式: v_sh000001="1~股票名称~..."
            if '=' not in row:
                return Stock(code=code, name="", now=0.0, low=0.0, high=0.0, yesterday=0.0, percent=0.0)
            
            _, params_str = row.split('=', 1)
            params_str = params_str.strip().strip('"')
            params = params_str.split('~')
            
            return TencentStockAPI._parse_stock_data(code, params)
            
        except Exception as e:
            print(f"获取股票数据失败 ({code}): {e}")
            return Stock(code=code, name="", now=0.0, low=0.0, high=0.0, yesterday=0.0, percent=0.0)
    
    @staticmethod
    def get_stocks(codes: List[str]) -> List[Stock]:
        """
        获取多个股票的实时数据
        
        Args:
            codes: 股票代码列表（统一格式）
            
        Returns:
            股票数据列表
            
        示例:
            >>> stocks = TencentStockAPI.get_stocks(["SH510500", "SZ399001"])
            >>> for stock in stocks:
            >>>     print(f"{stock.code}: {stock.name} - {stock.now}")
        """
        if not codes:
            return []
        
        # 去重和过滤空值
        codes = list(set(filter(None, codes)))
        
        if not codes:
            return []
        
        try:
            # 批量转换代码
            tencent_codes = [TencentStockAPI._transform_code_to_tencent(code) for code in codes]
            
            # 请求数据
            url = f"https://qt.gtimg.cn/q={','.join(tencent_codes)}"
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'
            
            # 解析数据
            body = response.text
            rows = body.split(';\n')
            
            results = []
            for i, code in enumerate(codes):
                tencent_code = tencent_codes[i]
                
                # 查找对应的数据行
                matching_row = None
                for row in rows:
                    if tencent_code in row:
                        matching_row = row
                        break
                
                if not matching_row or '=' not in matching_row:
                    results.append(Stock(code=code, name="", now=0.0, low=0.0, high=0.0, yesterday=0.0, percent=0.0))
                    continue
                
                # 提取数据
                _, params_str = matching_row.split('=', 1)
                params_str = params_str.strip().strip('"')
                params = params_str.split('~')
                
                results.append(TencentStockAPI._parse_stock_data(code, params))
            
            return results
            
        except Exception as e:
            print(f"批量获取股票数据失败: {e}")
            return [Stock(code=code, name="", now=0.0, low=0.0, high=0.0, yesterday=0.0, percent=0.0) for code in codes]
    
    @staticmethod
    def search_stocks(keyword: str) -> List[Stock]:
        """
        搜索股票
        
        Args:
            keyword: 搜索关键字（股票代码或名称）
            
        Returns:
            匹配的股票数据列表
            
        示例:
            >>> stocks = TencentStockAPI.search_stocks("500ETF")
            >>> for stock in stocks:
            >>>     print(f"{stock.code}: {stock.name}")
        """
        try:
            # 请求搜索接口
            url = f"https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={requests.utils.quote(keyword)}"
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'
            
            # 解析搜索结果
            body = response.text
            body = body.replace('v_hint="', '').replace('"', '')
            rows = body.split('^')
            
            # 提取股票代码
            codes = []
            for row in rows:
                if '~' not in row:
                    continue
                
                parts = row.split('~')
                if len(parts) < 2:
                    continue
                
                exchange_type = parts[0]
                stock_code = parts[1]
                
                # 转换为统一格式
                if exchange_type == 'sz':
                    codes.append('SZ' + stock_code)
                elif exchange_type == 'sh':
                    codes.append('SH' + stock_code)
                elif exchange_type == 'hk':
                    codes.append('HK' + stock_code)
                elif exchange_type == 'us':
                    # 美股代码可能包含.，只取点之前的部分
                    stock_code = stock_code.split('.')[0].upper()
                    codes.append('US' + stock_code)
            
            # 去重并获取详细数据
            codes = list(set(filter(None, codes)))
            return TencentStockAPI.get_stocks(codes)
            
        except Exception as e:
            print(f"搜索股票失败 ({keyword}): {e}")
            return []


# 示例用法
if __name__ == "__main__":
    print("=== 腾讯股票数据接口 Python 实现 ===\n")
    
    # 1. 获取单个股票数据
    print("1. 获取单个股票数据（上证指数）")
    stock = TencentStockAPI.get_stock("SH000001")
    print(f"代码: {stock.code}")
    print(f"名称: {stock.name}")
    print(f"现价: {stock.now}")
    print(f"涨跌幅: {stock.percent:.2%}")
    print(f"最高: {stock.high}, 最低: {stock.low}")
    print(f"昨收: {stock.yesterday}\n")
    
    # 2. 获取多个股票数据
    print("2. 获取多个股票数据")
    stocks = TencentStockAPI.get_stocks(["SH000001", "SZ399001", "SZ399006"])
    for s in stocks:
        print(f"{s.code} {s.name}: {s.now} ({s.percent:+.2%})")
    print()
    
    # 3. 搜索股票
    print("3. 搜索股票（关键字：平安）")
    results = TencentStockAPI.search_stocks("平安")
    for s in results[:5]:  # 只显示前5个结果
        print(f"{s.code} {s.name}: {s.now}")
