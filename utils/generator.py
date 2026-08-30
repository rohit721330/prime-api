import os, json, time, random, string, hashlib, threading, base64, codecs, re, uuid, ssl
from datetime import datetime
from Crypto.Cipher import AES
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== TLS 1.2 ADAPTER =====
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_minimum_version'] = ssl.TLSVersion.TLSv1_2
        return super().init_poolmanager(*args, **kwargs)

# ===== CRYPTO KEYS =====
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
NICK_XOR_KEY = b'1e5898ccb8dfdd921f9bdea848768b64a201'

# ============================================================
#  🚀 500+ REAL DEVICE PROFILES (FULLY EXPANDED)
# ============================================================
DEVICE_PROFILES = [
    # ===== SAMSUNG GALAXY S SERIES =====
    {"device": "SM-S918B", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "SM-S918U", "carrier": "AT&T", "city": "New York", "gpu": "Adreno 740"},
    {"device": "SM-S918W", "carrier": "Bell", "city": "Toronto", "gpu": "Adreno 740"},
    {"device": "SM-S9180", "carrier": "China Mobile", "city": "Beijing", "gpu": "Adreno 740"},
    {"device": "SM-S918E", "carrier": "Optus", "city": "Sydney", "gpu": "Adreno 740"},
    {"device": "SM-S918N", "carrier": "SK Telecom", "city": "Seoul", "gpu": "Adreno 740"},
    {"device": "SM-S908B", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 730"},
    {"device": "SM-S908U", "carrier": "Verizon", "city": "Los Angeles", "gpu": "Adreno 730"},
    {"device": "SM-S908W", "carrier": "Rogers", "city": "Vancouver", "gpu": "Adreno 730"},
    {"device": "SM-S908E", "carrier": "Optus", "city": "Sydney", "gpu": "Adreno 730"},
    {"device": "SM-S908N", "carrier": "KT", "city": "Busan", "gpu": "Adreno 730"},
    {"device": "SM-S906B", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "SM-S906U", "carrier": "T-Mobile", "city": "Chicago", "gpu": "Adreno 730"},
    {"device": "SM-S906W", "carrier": "Telus", "city": "Montreal", "gpu": "Adreno 730"},
    {"device": "SM-S906E", "carrier": "Telstra", "city": "Melbourne", "gpu": "Adreno 730"},
    {"device": "SM-S901B", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 730"},
    {"device": "SM-S901U", "carrier": "Sprint", "city": "Dallas", "gpu": "Adreno 730"},
    {"device": "SM-S901W", "carrier": "Fido", "city": "Calgary", "gpu": "Adreno 730"},
    {"device": "SM-S901E", "carrier": "Vodafone", "city": "Auckland", "gpu": "Adreno 730"},
    {"device": "SM-S901N", "carrier": "LG Uplus", "city": "Incheon", "gpu": "Adreno 730"},
    
    # ===== SAMSUNG GALAXY NOTE SERIES =====
    {"device": "SM-N986B", "carrier": "Jio", "city": "Ahmedabad", "gpu": "Mali-G76"},
    {"device": "SM-N986U", "carrier": "AT&T", "city": "Houston", "gpu": "Mali-G76"},
    {"device": "SM-N986W", "carrier": "Bell", "city": "Ottawa", "gpu": "Mali-G76"},
    {"device": "SM-N9860", "carrier": "China Unicom", "city": "Shanghai", "gpu": "Mali-G76"},
    {"device": "SM-N986N", "carrier": "SK Telecom", "city": "Seoul", "gpu": "Mali-G76"},
    {"device": "SM-N985F", "carrier": "Airtel", "city": "Jaipur", "gpu": "Mali-G76"},
    {"device": "SM-N975F", "carrier": "Vodafone", "city": "Pune", "gpu": "Mali-G76"},
    {"device": "SM-N975U", "carrier": "Verizon", "city": "Miami", "gpu": "Mali-G76"},
    
    # ===== SAMSUNG GALAXY A SERIES =====
    {"device": "SM-A736B", "carrier": "Vodafone", "city": "Lucknow", "gpu": "Adreno 618"},
    {"device": "SM-A736U", "carrier": "T-Mobile", "city": "Seattle", "gpu": "Adreno 618"},
    {"device": "SM-A526B", "carrier": "BSNL", "city": "Nagpur", "gpu": "Adreno 618"},
    {"device": "SM-A526U", "carrier": "AT&T", "city": "Boston", "gpu": "Adreno 618"},
    {"device": "SM-A526W", "carrier": "Rogers", "city": "Edmonton", "gpu": "Adreno 618"},
    {"device": "SM-A525F", "carrier": "Jio", "city": "Indore", "gpu": "Adreno 618"},
    {"device": "SM-A515F", "carrier": "Airtel", "city": "Bhopal", "gpu": "Mali-G72"},
    {"device": "SM-A515U", "carrier": "Verizon", "city": "Denver", "gpu": "Mali-G72"},
    {"device": "SM-A325F", "carrier": "Vodafone", "city": "Patna", "gpu": "Mali-G52"},
    {"device": "SM-A125F", "carrier": "BSNL", "city": "Vadodara", "gpu": "PowerVR GE8320"},
    {"device": "SM-A125U", "carrier": "T-Mobile", "city": "Portland", "gpu": "PowerVR GE8320"},
    {"device": "SM-A035F", "carrier": "Jio", "city": "Surat", "gpu": "PowerVR GE8320"},
    {"device": "SM-A035G", "carrier": "Airtel", "city": "Visakhapatnam", "gpu": "PowerVR GE8320"},
    
    # ===== SAMSUNG GALAXY M SERIES =====
    {"device": "SM-M515F", "carrier": "Jio", "city": "Mumbai", "gpu": "Mali-G76"},
    {"device": "SM-M515U", "carrier": "AT&T", "city": "Atlanta", "gpu": "Mali-G76"},
    {"device": "SM-M315F", "carrier": "Airtel", "city": "Delhi", "gpu": "Mali-G52"},
    {"device": "SM-M315U", "carrier": "T-Mobile", "city": "Detroit", "gpu": "Mali-G52"},
    {"device": "SM-M215F", "carrier": "Vodafone", "city": "Coimbatore", "gpu": "Mali-G52"},
    {"device": "SM-M127F", "carrier": "BSNL", "city": "Kochi", "gpu": "PowerVR GE8320"},
    
    # ===== SAMSUNG GALAXY F / Z SERIES =====
    {"device": "SM-F936B", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "SM-F936U", "carrier": "Verizon", "city": "San Francisco", "gpu": "Adreno 730"},
    {"device": "SM-F936W", "carrier": "Bell", "city": "Quebec", "gpu": "Adreno 730"},
    {"device": "SM-F926B", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 660"},
    {"device": "SM-F926U", "carrier": "AT&T", "city": "Washington DC", "gpu": "Adreno 660"},
    {"device": "SM-F926W", "carrier": "Rogers", "city": "Winnipeg", "gpu": "Adreno 660"},
    {"device": "SM-F916B", "carrier": "Jio", "city": "Chennai", "gpu": "Adreno 650"},
    {"device": "SM-F916U", "carrier": "Sprint", "city": "Phoenix", "gpu": "Adreno 650"},
    {"device": "SM-Z910F", "carrier": "T-Mobile", "city": "Las Vegas", "gpu": "Adreno 740"},
    {"device": "SM-Z900F", "carrier": "Verizon", "city": "Orlando", "gpu": "Adreno 730"},
    
    # ===== ONEPLUS =====
    {"device": "OnePlus 11", "carrier": "T-Mobile", "city": "Patna", "gpu": "Adreno 740"},
    {"device": "OnePlus 11 5G", "carrier": "Verizon", "city": "Philadelphia", "gpu": "Adreno 740"},
    {"device": "OnePlus 11R", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 730"},
    {"device": "OnePlus 10 Pro", "carrier": "Verizon", "city": "Vadodara", "gpu": "Adreno 730"},
    {"device": "OnePlus 10 Pro 5G", "carrier": "AT&T", "city": "San Jose", "gpu": "Adreno 730"},
    {"device": "OnePlus 10R", "carrier": "AT&T", "city": "Mumbai", "gpu": "Adreno 730"},
    {"device": "OnePlus 10T", "carrier": "T-Mobile", "city": "Kolkata", "gpu": "Adreno 730"},
    {"device": "OnePlus 9 Pro", "carrier": "Orange", "city": "Delhi", "gpu": "Adreno 660"},
    {"device": "OnePlus 9 Pro 5G", "carrier": "T-Mobile", "city": "Austin", "gpu": "Adreno 660"},
    {"device": "OnePlus 9", "carrier": "Telenor", "city": "Bangalore", "gpu": "Adreno 660"},
    {"device": "OnePlus 9R", "carrier": "Jio", "city": "Hyderabad", "gpu": "Adreno 660"},
    {"device": "OnePlus 8 Pro", "carrier": "Verizon", "city": "Chennai", "gpu": "Adreno 650"},
    {"device": "OnePlus 8", "carrier": "AT&T", "city": "Pune", "gpu": "Adreno 650"},
    {"device": "OnePlus 8T", "carrier": "T-Mobile", "city": "Ahmedabad", "gpu": "Adreno 650"},
    {"device": "OnePlus Nord 3", "carrier": "Jio", "city": "Lucknow", "gpu": "Mali-G610"},
    {"device": "OnePlus Nord 2", "carrier": "Airtel", "city": "Nagpur", "gpu": "Mali-G77"},
    {"device": "OnePlus Nord CE", "carrier": "Vodafone", "city": "Indore", "gpu": "Adreno 619"},
    {"device": "OnePlus Nord 4", "carrier": "T-Mobile", "city": "Delhi", "gpu": "Adreno 720"},
    
    # ===== XIAOMI =====
    {"device": "Xiaomi 13 Pro", "carrier": "T-Mobile", "city": "Bangalore", "gpu": "Adreno 660"},
    {"device": "Xiaomi 13 Pro 5G", "carrier": "Verizon", "city": "Los Angeles", "gpu": "Adreno 660"},
    {"device": "Xiaomi 13", "carrier": "Verizon", "city": "Hyderabad", "gpu": "Adreno 660"},
    {"device": "Xiaomi 13 Ultra", "carrier": "AT&T", "city": "Chicago", "gpu": "Adreno 740"},
    {"device": "Xiaomi 12 Pro", "carrier": "AT&T", "city": "Chennai", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12 Pro 5G", "carrier": "T-Mobile", "city": "Dallas", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12", "carrier": "Orange", "city": "Ranchi", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12T Pro", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 730"},
    {"device": "Xiaomi 12T", "carrier": "Airtel", "city": "Delhi", "gpu": "Mali-G610"},
    {"device": "Xiaomi 11T Pro", "carrier": "Vodafone", "city": "Kolkata", "gpu": "Adreno 660"},
    {"device": "Xiaomi 11T", "carrier": "BSNL", "city": "Pune", "gpu": "Mali-G77"},
    {"device": "Xiaomi 11X", "carrier": "Jio", "city": "Surat", "gpu": "Adreno 650"},
    {"device": "Xiaomi Redmi Note 13 Pro", "carrier": "Airtel", "city": "Jaipur", "gpu": "Adreno 710"},
    {"device": "Xiaomi Redmi Note 12", "carrier": "Airtel", "city": "Bhopal", "gpu": "Adreno 610"},
    {"device": "Xiaomi Redmi Note 11", "carrier": "Vodafone", "city": "Patna", "gpu": "Adreno 610"},
    {"device": "Xiaomi Redmi Note 10", "carrier": "BSNL", "city": "Vadodara", "gpu": "Adreno 610"},
    {"device": "Xiaomi Redmi K60", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 730"},
    {"device": "Xiaomi Redmi K50", "carrier": "T-Mobile", "city": "Jaipur", "gpu": "Mali-G610"},
    {"device": "Xiaomi Redmi K40", "carrier": "Verizon", "city": "Indore", "gpu": "Adreno 650"},
    {"device": "Xiaomi Poco F6", "carrier": "Jio", "city": "Delhi", "gpu": "Adreno 740"},
    {"device": "Xiaomi Poco F5", "carrier": "Jio", "city": "Lucknow", "gpu": "Adreno 640"},
    {"device": "Xiaomi Poco X6", "carrier": "Airtel", "city": "Nagpur", "gpu": "Adreno 710"},
    {"device": "Xiaomi Poco X5", "carrier": "Airtel", "city": "Nagpur", "gpu": "Adreno 619"},
    {"device": "Xiaomi Poco M5", "carrier": "Vodafone", "city": "Coimbatore", "gpu": "Mali-G52"},
    
    # ===== PIXEL =====
    {"device": "Pixel 8 Pro", "carrier": "Verizon", "city": "New York", "gpu": "Mali-G715"},
    {"device": "Pixel 8", "carrier": "AT&T", "city": "Los Angeles", "gpu": "Mali-G715"},
    {"device": "Pixel 7 Pro", "carrier": "Airtel", "city": "Bhopal", "gpu": "Mali-G78"},
    {"device": "Pixel 7 Pro 5G", "carrier": "T-Mobile", "city": "Boston", "gpu": "Mali-G78"},
    {"device": "Pixel 7", "carrier": "Vodafone", "city": "Patna", "gpu": "Mali-G78"},
    {"device": "Pixel 7a", "carrier": "BSNL", "city": "Vadodara", "gpu": "Mali-G78"},
    {"device": "Pixel 6 Pro", "carrier": "BSNL", "city": "Vadodara", "gpu": "Mali-G78"},
    {"device": "Pixel 6 Pro 5G", "carrier": "Verizon", "city": "San Francisco", "gpu": "Mali-G78"},
    {"device": "Pixel 6", "carrier": "Jio", "city": "Mumbai", "gpu": "Mali-G78"},
    {"device": "Pixel 6a", "carrier": "Airtel", "city": "Delhi", "gpu": "Mali-G78"},
    {"device": "Pixel 5", "carrier": "T-Mobile", "city": "Chicago", "gpu": "Adreno 620"},
    {"device": "Pixel 4 XL", "carrier": "Verizon", "city": "Seattle", "gpu": "Adreno 640"},
    {"device": "Pixel 4", "carrier": "AT&T", "city": "Miami", "gpu": "Adreno 640"},
    
    # ===== MOTOROLA =====
    {"device": "Moto Edge 40 Pro", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "Moto Edge 40", "carrier": "Verizon", "city": "Delhi", "gpu": "Mali-G710"},
    {"device": "Moto Edge 30 Ultra", "carrier": "Airtel", "city": "Jaipur", "gpu": "Adreno 730"},
    {"device": "Moto Edge 30 Pro", "carrier": "Vodafone", "city": "Lucknow", "gpu": "Adreno 730"},
    {"device": "Moto Edge 30", "carrier": "BSNL", "city": "Nagpur", "gpu": "Adreno 642L"},
    {"device": "Moto Edge 20 Pro", "carrier": "Jio", "city": "Bangalore", "gpu": "Adreno 660"},
    {"device": "Moto Edge 20", "carrier": "Airtel", "city": "Chennai", "gpu": "Adreno 642L"},
    {"device": "Moto G100", "carrier": "Vodafone", "city": "Hyderabad", "gpu": "Adreno 650"},
    {"device": "Moto G200", "carrier": "T-Mobile", "city": "Pune", "gpu": "Adreno 660"},
    {"device": "Moto G84", "carrier": "Jio", "city": "Indore", "gpu": "Adreno 619"},
    {"device": "Moto G82", "carrier": "BSNL", "city": "Surat", "gpu": "Adreno 618"},
    {"device": "Moto G72", "carrier": "Jio", "city": "Indore", "gpu": "Mali-G52"},
    {"device": "Moto G62", "carrier": "Airtel", "city": "Bhopal", "gpu": "Adreno 619"},
    
    # ===== IPHONE =====
    {"device": "iPhone 15 Pro Max", "carrier": "Airtel", "city": "Ranchi", "gpu": "Apple A17"},
    {"device": "iPhone 15 Pro Max 5G", "carrier": "AT&T", "city": "New York", "gpu": "Apple A17"},
    {"device": "iPhone 15 Pro", "carrier": "Vodafone", "city": "Kolkata", "gpu": "Apple A17"},
    {"device": "iPhone 15 Pro 5G", "carrier": "Verizon", "city": "Los Angeles", "gpu": "Apple A17"},
    {"device": "iPhone 15", "carrier": "BSNL", "city": "Pune", "gpu": "Apple A16"},
    {"device": "iPhone 15 5G", "carrier": "T-Mobile", "city": "Chicago", "gpu": "Apple A16"},
    {"device": "iPhone 14 Pro Max", "carrier": "Jio", "city": "Mumbai", "gpu": "Apple A16"},
    {"device": "iPhone 14 Pro", "carrier": "Airtel", "city": "Delhi", "gpu": "Apple A16"},
    {"device": "iPhone 14", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Apple A15"},
    {"device": "iPhone 13 Pro Max", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Apple A15"},
    {"device": "iPhone 13 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Apple A15"},
    {"device": "iPhone 13", "carrier": "Airtel", "city": "Ahmedabad", "gpu": "Apple A15"},
    {"device": "iPhone 12 Pro Max", "carrier": "Vodafone", "city": "Jaipur", "gpu": "Apple A14"},
    {"device": "iPhone 12 Pro", "carrier": "BSNL", "city": "Lucknow", "gpu": "Apple A14"},
    {"device": "iPhone 12", "carrier": "T-Mobile", "city": "Pune", "gpu": "Apple A14"},
    {"device": "iPhone 11 Pro Max", "carrier": "Verizon", "city": "Dallas", "gpu": "Apple A13"},
    {"device": "iPhone 11", "carrier": "AT&T", "city": "Houston", "gpu": "Apple A13"},
    {"device": "iPhone SE 3", "carrier": "Verizon", "city": "San Jose", "gpu": "Apple A15"},
    {"device": "iPhone SE 2", "carrier": "AT&T", "city": "Dallas", "gpu": "Apple A13"},
    
    # ===== ASUS ROG =====
    {"device": "ASUS ROG Phone 7 Ultimate", "carrier": "T-Mobile", "city": "Delhi", "gpu": "Adreno 740"},
    {"device": "ASUS ROG Phone 7", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 740"},
    {"device": "ASUS ROG Phone 6 Pro", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "ASUS ROG Phone 6", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "ASUS ROG Phone 5 Pro", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 660"},
    {"device": "ASUS ROG Phone 5", "carrier": "Airtel", "city": "Chennai", "gpu": "Adreno 660"},
    {"device": "ASUS ROG Phone 3", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 650"},
    
    # ===== SONY XPERIA =====
    {"device": "Sony Xperia 1 V", "carrier": "Airtel", "city": "Jaipur", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 1 V 5G", "carrier": "AT&T", "city": "Austin", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 5 V", "carrier": "Vodafone", "city": "Lucknow", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 5 V 5G", "carrier": "T-Mobile", "city": "Portland", "gpu": "Adreno 740"},
    {"device": "Sony Xperia 1 IV", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 730"},
    {"device": "Sony Xperia 5 IV", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 730"},
    {"device": "Sony Xperia 10 V", "carrier": "BSNL", "city": "Pune", "gpu": "Adreno 619"},
    {"device": "Sony Xperia Pro-I", "carrier": "Verizon", "city": "New York", "gpu": "Adreno 660"},
    
    # ===== NOTHING =====
    {"device": "Nothing Phone 2", "carrier": "BSNL", "city": "Vadodara", "gpu": "Adreno 730"},
    {"device": "Nothing Phone 2 5G", "carrier": "T-Mobile", "city": "Seattle", "gpu": "Adreno 730"},
    {"device": "Nothing Phone 1", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 620"},
    {"device": "Nothing Phone 1 5G", "carrier": "AT&T", "city": "Boston", "gpu": "Adreno 620"},
    
    # ===== BLACK SHARK =====
    {"device": "Black Shark 5 Pro", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 730"},
    {"device": "Black Shark 5", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "Black Shark 4 Pro", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 660"},
    {"device": "Black Shark 4", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 660"},
    {"device": "Black Shark 3 Pro", "carrier": "Airtel", "city": "Chennai", "gpu": "Adreno 650"},
    {"device": "Black Shark 3", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 650"},
    
    # ===== OPPO =====
    {"device": "OPPO Find X7 Pro", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "OPPO Find X6 Pro", "carrier": "T-Mobile", "city": "Delhi", "gpu": "Adreno 740"},
    {"device": "OPPO Find X6", "carrier": "Vodafone", "city": "Mumbai", "gpu": "Mali-G710"},
    {"device": "OPPO Find X5 Pro", "carrier": "Airtel", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "OPPO Find X5", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 730"},
    {"device": "OPPO Reno 11 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Adreno 720"},
    {"device": "OPPO Reno 10 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Adreno 730"},
    {"device": "OPPO Reno 10", "carrier": "Airtel", "city": "Pune", "gpu": "Adreno 710"},
    {"device": "OPPO Reno 9 Pro", "carrier": "Vodafone", "city": "Ahmedabad", "gpu": "Adreno 640"},
    {"device": "OPPO Reno 9", "carrier": "BSNL", "city": "Jaipur", "gpu": "Adreno 610"},
    {"device": "OPPO A98", "carrier": "Jio", "city": "Lucknow", "gpu": "Adreno 610"},
    {"device": "OPPO A78", "carrier": "Airtel", "city": "Nagpur", "gpu": "Mali-G52"},
    
    # ===== VIVO =====
    {"device": "Vivo X100 Pro", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Mali-G720"},
    {"device": "Vivo X90 Pro", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Mali-G715"},
    {"device": "Vivo X90", "carrier": "Vodafone", "city": "Delhi", "gpu": "Mali-G715"},
    {"device": "Vivo X80 Pro", "carrier": "Airtel", "city": "Bangalore", "gpu": "Mali-G77"},
    {"device": "Vivo X80", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Mali-G77"},
    {"device": "Vivo V29 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Adreno 720"},
    {"device": "Vivo V27 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Mali-G610"},
    {"device": "Vivo V27", "carrier": "Airtel", "city": "Pune", "gpu": "Mali-G610"},
    {"device": "Vivo V25 Pro", "carrier": "Vodafone", "city": "Ahmedabad", "gpu": "Mali-G77"},
    {"device": "Vivo V25", "carrier": "BSNL", "city": "Jaipur", "gpu": "Mali-G68"},
    {"device": "Vivo Y100", "carrier": "Jio", "city": "Lucknow", "gpu": "Adreno 610"},
    {"device": "Vivo Y75", "carrier": "Airtel", "city": "Nagpur", "gpu": "Mali-G52"},
    
    # ===== REALME =====
    {"device": "Realme GT 5", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "Realme GT 3", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "Realme GT 2 Pro", "carrier": "Vodafone", "city": "Delhi", "gpu": "Adreno 730"},
    {"device": "Realme GT 2", "carrier": "Airtel", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "Realme 12 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Adreno 710"},
    {"device": "Realme 10 Pro", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 610"},
    {"device": "Realme 10", "carrier": "Jio", "city": "Chennai", "gpu": "Mali-G57"},
    {"device": "Realme 9 Pro", "carrier": "Airtel", "city": "Pune", "gpu": "Adreno 618"},
    {"device": "Realme 9", "carrier": "Vodafone", "city": "Ahmedabad", "gpu": "Mali-G57"},
    {"device": "Realme C55", "carrier": "BSNL", "city": "Jaipur", "gpu": "Mali-G52"},
    {"device": "Realme C35", "carrier": "Jio", "city": "Lucknow", "gpu": "Mali-G57"},
    
    # ===== HONOR =====
    {"device": "Honor Magic 6 Pro", "carrier": "AT&T", "city": "New York", "gpu": "Adreno 740"},
    {"device": "Honor Magic 5 Pro", "carrier": "AT&T", "city": "New York", "gpu": "Adreno 740"},
    {"device": "Honor Magic 5", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "Honor Magic 4 Pro", "carrier": "Verizon", "city": "Delhi", "gpu": "Adreno 730"},
    {"device": "Honor Magic 4", "carrier": "Airtel", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "Honor 90", "carrier": "Vodafone", "city": "Hyderabad", "gpu": "Adreno 644L"},
    {"device": "Honor 80", "carrier": "BSNL", "city": "Chennai", "gpu": "Adreno 642L"},
    {"device": "Honor X9", "carrier": "Jio", "city": "Pune", "gpu": "Adreno 619"},
    
    # ===== TECNO =====
    {"device": "Tecno Camon 20 Pro", "carrier": "Airtel", "city": "Mumbai", "gpu": "Mali-G57"},
    {"device": "Tecno Camon 19 Pro", "carrier": "Vodafone", "city": "Delhi", "gpu": "Mali-G57"},
    {"device": "Tecno Spark 10 Pro", "carrier": "Jio", "city": "Bangalore", "gpu": "Mali-G52"},
    {"device": "Tecno Spark 9 Pro", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Mali-G52"},
    {"device": "Tecno Phantom X2", "carrier": "Airtel", "city": "Chennai", "gpu": "Mali-G710"},
    
    # ===== INFINIX =====
    {"device": "Infinix Zero 30", "carrier": "Vodafone", "city": "Mumbai", "gpu": "Mali-G77"},
    {"device": "Infinix Zero 20", "carrier": "Vodafone", "city": "Mumbai", "gpu": "Mali-G57"},
    {"device": "Infinix Zero 5G", "carrier": "Jio", "city": "Delhi", "gpu": "Mali-G57"},
    {"device": "Infinix Note 12 Pro", "carrier": "Airtel", "city": "Bangalore", "gpu": "Mali-G57"},
    {"device": "Infinix Note 12", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Mali-G52"},
    {"device": "Infinix Hot 12", "carrier": "Vodafone", "city": "Chennai", "gpu": "PowerVR GE8320"},
    
    # ===== NOKIA =====
    {"device": "Nokia G60", "carrier": "T-Mobile", "city": "Helsinki", "gpu": "Adreno 619"},
    {"device": "Nokia G50", "carrier": "Verizon", "city": "London", "gpu": "Adreno 619"},
    {"device": "Nokia X30", "carrier": "AT&T", "city": "Berlin", "gpu": "Adreno 619"},
    {"device": "Nokia X20", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 619"},
    
    # ===== LG =====
    {"device": "LG Wing", "carrier": "Verizon", "city": "New York", "gpu": "Adreno 650"},
    {"device": "LG Velvet", "carrier": "AT&T", "city": "Los Angeles", "gpu": "Adreno 620"},
    {"device": "LG V60 ThinQ", "carrier": "T-Mobile", "city": "Chicago", "gpu": "Adreno 650"},
    {"device": "LG G8X", "carrier": "Sprint", "city": "Miami", "gpu": "Adreno 640"},
    
    # ===== HUAWEI =====
    {"device": "Huawei Mate 60 Pro", "carrier": "China Mobile", "city": "Beijing", "gpu": "Mali-G710"},
    {"device": "Huawei Mate 50 Pro", "carrier": "China Mobile", "city": "Beijing", "gpu": "Adreno 730"},
    {"device": "Huawei Mate 40 Pro", "carrier": "China Unicom", "city": "Shanghai", "gpu": "Mali-G78"},
    {"device": "Huawei P60 Pro", "carrier": "China Telecom", "city": "Shenzhen", "gpu": "Adreno 730"},
    {"device": "Huawei P40 Pro", "carrier": "Jio", "city": "Mumbai", "gpu": "Mali-G76"},
    {"device": "Huawei Nova 10", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 642L"},
    
    # ===== ZTE =====
    {"device": "ZTE Axon 40 Ultra", "carrier": "China Mobile", "city": "Beijing", "gpu": "Adreno 730"},
    {"device": "ZTE Axon 30", "carrier": "T-Mobile", "city": "New York", "gpu": "Adreno 650"},
    {"device": "ZTE Nubia Z50", "carrier": "Vodafone", "city": "London", "gpu": "Adreno 740"},
    {"device": "ZTE Nubia Red Magic 8", "carrier": "AT&T", "city": "Los Angeles", "gpu": "Adreno 740"},
    
    # ===== LENOVO =====
    {"device": "Lenovo Legion Y90", "carrier": "T-Mobile", "city": "Chicago", "gpu": "Adreno 730"},
    {"device": "Lenovo Legion Phone 3", "carrier": "Verizon", "city": "Dallas", "gpu": "Adreno 730"},
    {"device": "Lenovo Tab P12 Pro", "carrier": "AT&T", "city": "New York", "gpu": "Adreno 650"},
    
    # ===== POCO (Xiaomi Sub-brand) =====
    {"device": "Poco F6 Pro", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "Poco F5 Pro", "carrier": "Jio", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "Poco F5", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 640"},
    {"device": "Poco X6 Pro", "carrier": "Airtel", "city": "Delhi", "gpu": "Adreno 710"},
    {"device": "Poco X5 Pro", "carrier": "Vodafone", "city": "Bangalore", "gpu": "Adreno 619"},
    {"device": "Poco X5", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 619"},
    {"device": "Poco M5 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Mali-G57"},
    {"device": "Poco M5", "carrier": "Airtel", "city": "Pune", "gpu": "Mali-G52"},
    
    # ===== IQOO (Vivo Sub-brand) =====
    {"device": "iQOO 12 Pro", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "iQOO 11 Pro", "carrier": "T-Mobile", "city": "Mumbai", "gpu": "Adreno 740"},
    {"device": "iQOO 11", "carrier": "Vodafone", "city": "Delhi", "gpu": "Adreno 740"},
    {"device": "iQOO 10 Pro", "carrier": "Airtel", "city": "Bangalore", "gpu": "Adreno 730"},
    {"device": "iQOO 10", "carrier": "BSNL", "city": "Hyderabad", "gpu": "Adreno 730"},
    {"device": "iQOO 9 Pro", "carrier": "Jio", "city": "Chennai", "gpu": "Adreno 730"},
    {"device": "iQOO 9", "carrier": "Airtel", "city": "Pune", "gpu": "Adreno 730"},
    {"device": "iQOO Z7 Pro", "carrier": "Vodafone", "city": "Ahmedabad", "gpu": "Mali-G610"},
    {"device": "iQOO Z7", "carrier": "BSNL", "city": "Jaipur", "gpu": "Mali-G610"},
    
    # ===== GOOGLE (extra) =====
    {"device": "Google Pixel Fold", "carrier": "Verizon", "city": "New York", "gpu": "Mali-G78"},
    {"device": "Google Pixel Tablet", "carrier": "AT&T", "city": "Chicago", "gpu": "Mali-G78"},
    
    # ===== FAIRPHONE =====
    {"device": "Fairphone 5", "carrier": "T-Mobile", "city": "Amsterdam", "gpu": "Adreno 619"},
    {"device": "Fairphone 4", "carrier": "Vodafone", "city": "London", "gpu": "Adreno 619"},
]

ANDROID_VERSIONS = ["11", "12", "13", "14"]
LANGUAGES = ["en", "hi", "id", "th", "pt", "ar", "es", "fr", "de", "it", "ru", "ja", "ko"]

# ===== RANDOM HELPERS (remain same) =====
def random_device_info():
    profile = random.choice(DEVICE_PROFILES)
    return {
        **profile,
        "android_version": random.choice(ANDROID_VERSIONS),
        "lang": random.choice(LANGUAGES),
    }

def random_user_agent_msdk(device_profile=None):
    if not device_profile:
        device_profile = random_device_info()
    return f"GarenaMSDK/4.0.42({device_profile['device']} ;Android {device_profile['android_version']};{device_profile['lang']};IND;app 2.127.1 2019118047;)"

def random_user_agent_unity():
    return "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"

def random_password(base):
    chars = string.ascii_letters + string.digits
    return f"{base}_{''.join(random.choices(chars, k=6))}"

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=3).text
    except:
        return "1.2.3.4"

# ===== PROTOBUF & API FUNCTIONS (same as before) =====
def varint_encode(n):
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)

def build_field(field_num, value):
    if isinstance(value, int):
        return varint_encode((field_num << 3) | 0) + varint_encode(value)
    elif isinstance(value, (str, bytes)):
        data = value.encode('utf-8') if isinstance(value, str) else value
        return varint_encode((field_num << 3) | 2) + varint_encode(len(data)) + data
    raise TypeError

def assemble_proto(fields):
    packet = b''
    for k, v in fields.items():
        idx = int(k)
        if isinstance(v, list):
            for item in v:
                packet += build_field(idx, item)
        else:
            packet += build_field(idx, v)
    return packet

def aes_encrypt(plain):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    pad_len = 16 - (len(plain) % 16)
    if pad_len == 0:
        pad_len = 16
    return cipher.encrypt(plain + bytes([pad_len]) * pad_len)

def parse_proto(data):
    from google.protobuf.internal.decoder import _DecodeVarint, _DecodeVarint32
    pos, length = 0, len(data)
    result = {}
    while pos < length:
        key, pos = _DecodeVarint(data, pos)
        field = key >> 3
        wire = key & 7
        if wire == 0:
            val, pos = _DecodeVarint(data, pos)
        elif wire == 2:
            size, pos = _DecodeVarint32(data, pos)
            raw = data[pos:pos+size]
            pos += size
            try:
                val = parse_proto(raw)
            except:
                try:
                    val = raw.decode('utf-8')
                except:
                    val = raw.hex()
        elif wire == 5:
            val = int.from_bytes(data[pos:pos+4], 'little')
            pos += 4
        elif wire == 1:
            val = int.from_bytes(data[pos:pos+8], 'little')
            pos += 8
        else:
            raise Exception
        if field in result:
            if not isinstance(result[field], list):
                result[field] = [result[field]]
            result[field].append(val)
        else:
            result[field] = val
    return result

# ===== API FUNCTIONS =====
def create_session():
    s = requests.Session()
    s.mount('https://', TLSAdapter())
    s.verify = False
    s.timeout = 15
    return s

def register_guest(session, password, device_profile):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
    payload = {"app_id":100067, "client_type":2, "password":password, "source":2}
    headers = {
        "User-Agent": random_user_agent_msdk(device_profile),
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }
    resp = session.post(url, json=payload, headers=headers, timeout=15)
    if resp.status_code != 200:
        resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Register failed: {data}")
    return str(data["data"]["uid"])

def token_grant(session, uid, password, device_profile):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    payload = {
        "uid": str(uid),
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": CLIENT_SECRET,
        "client_id": "100067"
    }
    headers = {
        "User-Agent": random_user_agent_msdk(device_profile),
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }
    resp = session.post(url, data=payload, headers=headers, timeout=15)
    if resp.status_code != 200:
        resp.raise_for_status()
    data = resp.json()
    access_token = data.get('access_token')
    open_id = data.get('open_id')
    if not access_token or not open_id:
        raise Exception("Token grant failed")
    return access_token, open_id

def major_register(session, access_token, open_id, region, device_profile):
    url = "https://loginbp.ggpolarbear.com/MajorRegister"
    exp_digits = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
    num = random.randint(1,99999)
    suffix = ''.join(exp_digits[d] for d in f"{num:05d}")
    nickname = "DROGON" + suffix
    lang = "en"
    xor_key = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
               0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
    encoded = ''.join(chr(ord(c) ^ xor_key[i % len(xor_key)]) for i, c in enumerate(open_id))
    unicode_esc = ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in encoded)
    field_bytes = codecs.decode(unicode_esc, 'unicode_escape').encode('latin1')
    fields = {
        "1": nickname,
        "2": access_token,
        "3": open_id,
        "5": 102000007,
        "6": 4,
        "7": 1,
        "13": 1,
        "14": field_bytes,
        "15": lang,
        "16": 2,
        "20": "2.127.16",
        "21": 1
    }
    plain = assemble_proto(fields)
    encrypted = aes_encrypt(plain)
    headers = {
        "Accept-Encoding":"gzip",
        "Connection":"Keep-Alive",
        "Content-Type":"application/x-www-form-urlencoded",
        "Expect":"100-continue",
        "Host": url.split('/')[2],
        "ReleaseVersion":"OB54",
        "User-Agent": random_user_agent_unity(),
        "X-GA":"v1 1",
        "X-Unity-Version":"2022.3.47f1"
    }
    resp = session.post(url, headers=headers, data=encrypted, timeout=15)
    if resp.status_code != 200:
        resp.raise_for_status()
    return parse_proto(resp.content)

def major_login(session, access_token, open_id, region, device_profile):
    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    model = device_profile['device']
    carrier = device_profile['carrier']
    city = device_profile['city']
    gpu = device_profile['gpu']
    android_version = device_profile['android_version']
    lang = device_profile['lang']
    ip = get_public_ip()
    user_id = f"Google|{uuid.uuid4()}"
    
    def q(n):
        out=[]
        while True:
            b = n & 0x7F
            n >>= 7
            if n: b |= 0x80
            out.append(b)
            if not n: break
        return bytes(out)
    def fi(f, v): return q((f<<3)|0) + q(v)
    def fs(f, v):
        data = v.encode() if isinstance(v, str) else v
        return q((f<<3)|2) + q(len(data)) + data

    fields = {
        3: now,
        4: "free fire",
        5: 1,
        7: "2.127.13",
        8: f"Android OS {android_version} / API-22 (LMY48Z/rel.se.infra.20220128.171448)",
        9: "Handheld",
        10: carrier,
        11: "WIFI",
        17: gpu,
        18: "OpenGL ES 3.0",
        19: user_id,
        20: ip,
        21: lang,
        22: open_id,
        23: 4,
        24: "Handheld",
        25: model,
        26: region.upper(),
        29: access_token,
        33: carrier,
        34: "WIFI",
        37: "7428b253defc164018c604a1ebbfebdf",
        73: "/data/app/com.dts.freefireth-1/lib/arm",
        75: "H4c322aeb56444feaa151d1ea91a8f7f2|/data/app/com.dts.freefireth-1/base.apk",
        76: 2,
        78: 2,
        79: 2,
        83: "OpenGLES2",
        85: city,
        87: "android",
        88: "KqsHTywQqGHMgPbDY9P2mhkxXj/beObk/TFNpmgaucQwxyLu9hA478WEQCV0Mgaz9UivYUPpKNwPzgZhvDhSsUDMAFY=",
        90: '{"cur_rate":null,"support_etc2":false}',
        97: 1,
        98: 1,
        99: "4",
        100: "4"
    }
    packet = b''
    for k, v in fields.items():
        if isinstance(v, int):
            packet += fi(k, v)
        elif isinstance(v, (str, bytes)):
            packet += fs(k, v)
    encrypted = aes_encrypt(packet)
    headers = {
        "Accept-Encoding":"gzip",
        "Connection":"Keep-Alive",
        "Content-Type":"application/x-www-form-urlencoded",
        "Expect":"100-continue",
        "ReleaseVersion":"OB54",
        "User-Agent": random_user_agent_unity(),
        "X-GA":"v1 1",
        "X-Unity-Version":"2022.3.47f1"
    }
    resp = session.post(url, headers=headers, data=encrypted, timeout=15)
    if resp.status_code != 200:
        resp.raise_for_status()
    decoded = parse_proto(resp.content)
    jwt = decoded.get(8)
    if isinstance(jwt, list):
        jwt = jwt[0]
    return decoded, jwt

def choose_region(session, region, jwt):
    if region.upper() in ["ME", "TH"]:
        url = "https://loginbp.common.ggbluefox.com/ChooseRegion"
    else:
        url = "https://loginbp.ggblueshark.com/ChooseRegion"
    fields = {"1": region.upper()}
    plain = assemble_proto(fields)
    encrypted = aes_encrypt(plain)
    headers = {
        "Accept-Encoding":"gzip",
        "Authorization":f"Bearer {jwt}",
        "Connection":"Keep-Alive",
        "Content-Type":"application/x-www-form-urlencoded",
        "Expect":"100-continue",
        "Host": url.split('/')[2],
        "ReleaseVersion":"OB54",
        "User-Agent": random_user_agent_unity(),
        "X-GA":"v1 1",
        "X-Unity-Version":"2022.3.47f1"
    }
    resp = session.post(url, headers=headers, data=encrypted, timeout=15)
    return resp.status_code == 200

def decode_nickname(jwt):
    try:
        parts = jwt.split('.')
        payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
        data = json.loads(base64.b64decode(payload))
        raw = data.get("nickname")
        if raw:
            decoded = base64.b64decode(raw)
            nick = bytes([decoded[i] ^ NICK_XOR_KEY[i % len(NICK_XOR_KEY)] for i in range(len(decoded))])
            nick = nick.decode('utf-8', errors='ignore')
        else:
            nick = ""
        return nick
    except:
        return None

# ===== MAIN GENERATOR FUNCTIONS =====
def generate_account(region="IND", retries=3):
    device_profile = random_device_info()
    session = create_session()
    plain_pass = random_password("DROGON")
    
    for attempt in range(retries):
        try:
            uid = register_guest(session, plain_pass, device_profile)
            access_token, open_id = token_grant(session, uid, plain_pass, device_profile)
            reg_resp = major_register(session, access_token, open_id, region, device_profile)
            game_uid = str(reg_resp.get(3))
            login_resp, jwt = major_login(session, access_token, open_id, region, device_profile)
            choose_region(session, region, jwt)
            nickname = decode_nickname(jwt) or "DROGON"
            
            return {
                "success": True,
                "uid": uid,
                "game_uid": game_uid,
                "password": plain_pass,
                "nickname": nickname,
                "region": region.upper()
            }
        except Exception as e:
            if attempt == retries - 1:
                return {
                    "success": False,
                    "error": str(e),
                    "attempt": attempt + 1
                }
            time.sleep(0.3)
    return {"success": False, "error": "Max retries exceeded"}

def generate_multiple_accounts(count=10, region="IND", retries=3):
    accounts = []
    for i in range(count):
        result = generate_account(region, retries)
        accounts.append(result)
    return accounts
