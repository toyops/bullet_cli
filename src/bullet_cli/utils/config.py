import json
import os
from typing import List, Dict, Any

class Config:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        self._migrate_watch_list()
        
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return {'watch_list': []}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _migrate_watch_list(self):
        """
        迁移旧格式的观察列表到新格式
        旧格式 QuoteID: 1.600000 (市场.代码)
        新格式 QuoteID: SH600000 (统一代码)
        """
        watch_list = self.get_watch_list()
        migrated = False
        
        for stock in watch_list:
            quote_id = stock.get('QuoteID', '')
            
            # 检查是否是旧格式 (包含点号)
            if '.' in quote_id:
                parts = quote_id.split('.')
                if len(parts) == 2:
                    market, code = parts
                    
                    # 转换市场代码
                    # 1 -> SH (上海), 0 -> SZ (深圳)
                    if market == '1':
                        new_quote_id = 'SH' + code
                    elif market == '0':
                        new_quote_id = 'SZ' + code
                    else:
                        # 未知市场，跳过
                        continue
                    
                    stock['QuoteID'] = new_quote_id
                    migrated = True
        
        # 如果有迁移，保存配置
        if migrated:
            self._save_config()
            print('已自动将观察列表迁移到新格式')
    
    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get_watch_list(self) -> List[Dict[str, str]]:
        return self.config.get('watch_list', [])
    
    def add_stock_to_watch_list(self, stock: Dict[str, str]):
        watch_list = self.get_watch_list()
        stock_code = stock['Code']
        stock_name = stock['Name']
        stock_id = f'{stock_name}({stock_code})'

        if stock_code not in [x['Code'] for x in watch_list]:
            watch_list.append(stock)
            self.config['watch_list'] = watch_list
            self._save_config()
            print(f'add {stock_id} successfully!')
        else:
            print(f'{stock_id} already exists!')
    
    def remove_stock_from_watch_list(self, stock: Dict[str, str]):
        watch_list = self.get_watch_list()
        stock_code = stock['Code']
        stock_name = stock['Name']
        stock_id = f'{stock_name}({stock_code})'

        if stock_code not in [x['Code'] for x in watch_list]:
            print(f'{stock_id} not in watch list!')
        else:
            # Find and remove the exact match
            watch_list = [x for x in watch_list if x['Code'] != stock_code]
            self.config['watch_list'] = watch_list
            self._save_config()
            print(f'remove {stock_id} successfully!')
