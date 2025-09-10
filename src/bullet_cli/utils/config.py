import json
import os
from typing import List, Dict, Any

class Config:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return {'watch_list': []}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
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
