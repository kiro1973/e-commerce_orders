#!/usr/bin/env python3

import unittest
import json
import os
import tempfile
from orders_analyzer import read_orders, calculate_revenue


class TestOrdersAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def create_temp_jsonl(self, orders):
        filepath = os.path.join(self.temp_dir, "test.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            for order in orders:
                f.write(json.dumps(order) + '\n')
        return filepath
    
    def test_all_suspicious_orders(self):
        orders = [
            {"id": "s1", "marketplace": "amazon", "amount_cents": -1000, "created_at": "2024-11-01T10:00:00Z"},
            {"id": "s2", "marketplace": "", "amount_cents": 5000, "created_at": "2024-11-01T11:00:00Z"},
            {"id": "s3", "marketplace": "ebay", "amount_cents": -500, "created_at": "2024-11-01T13:00:00Z"}
        ]
        
        filepath = self.create_temp_jsonl(orders)
        data = read_orders(filepath)
        total, by_marketplace, suspicious = calculate_revenue(data)
        
        self.assertEqual(len(suspicious), 3)
        self.assertEqual(total, 50.00)
    
    def test_mixed_orders_with_date_filter(self):
        orders = [
            {"id": "m1", "marketplace": "amazon", "amount_cents": 1000, "created_at": "2024-10-15T10:00:00Z"},
            {"id": "m2", "marketplace": "amazon", "amount_cents": 2500, "created_at": "2024-11-01T10:00:00Z"},
            {"id": "m3", "marketplace": "", "amount_cents": 3000, "created_at": "2024-11-01T12:00:00Z"},
            {"id": "m4", "marketplace": "ebay", "amount_cents": -800, "created_at": "2024-11-01T13:00:00Z"},
        ]
        
        filepath = self.create_temp_jsonl(orders)
        
        data_no_filter = read_orders(filepath)
        total_no_filter, _, suspicious_no_filter = calculate_revenue(data_no_filter)
        
        self.assertEqual(len(data_no_filter), 4)
        self.assertEqual(total_no_filter, 65.00)
        self.assertEqual(len(suspicious_no_filter), 2)
        
        data_filtered = read_orders(filepath, from_date="2024-11-01")
        total_filtered, _, _ = calculate_revenue(data_filtered)
        
        self.assertEqual(len(data_filtered), 3)
        self.assertEqual(total_filtered, 55.00)


if __name__ == "__main__":
    unittest.main()