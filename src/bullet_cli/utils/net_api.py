"""
网络API模块 - 使用腾讯股票API获取股票数据
"""
from ..tencent_stock import TencentStockAPI, Stock


def get_bullets_value(stock_code_list):
    """
    获取股票实时数据
    
    Args:
        stock_code_list: 股票代码列表，统一格式如 ['SH600000', 'SZ000001']
        
    Returns:
        股票数据列表，保持与旧API兼容的字典格式
        [{
            'f14': 股票名称,
            'f2': 现价*100 (整数),
            'f18': 昨收价*100 (整数)
        }]
    """
    stocks = TencentStockAPI.get_stocks(stock_code_list)
    
    # 转换为旧格式以保持兼容性
    result = []
    for stock in stocks:
        result.append({
            'f14': stock.name,
            'f2': int(stock.now * 100),  # 现价转为分
            'f18': int(stock.yesterday * 100),  # 昨收价转为分
        })
    
    return result


def search_bullets(name):
    """
    搜索股票
    
    Args:
        name: 搜索关键字
        
    Returns:
        股票列表，保持与旧API兼容的字典格式
        [{
            'Name': 股票名称,
            'Code': 股票代码(不含交易所前缀),
            'QuoteID': 统一格式代码(如SH600000)
        }]
    """
    stocks = TencentStockAPI.search_stocks(name)
    
    # 转换为旧格式以保持兼容性
    result = []
    for stock in stocks:
        # 从统一代码中提取交易所和代码
        # 如 SH600000 -> code=600000, QuoteID=SH600000
        code = stock.code
        if len(code) > 2:
            stock_code = code[2:]  # 去掉前缀如SH, SZ
        else:
            stock_code = code
            
        result.append({
            'Name': stock.name,
            'Code': stock_code,
            'QuoteID': stock.code,  # 保存统一格式代码
        })
    
    return result
