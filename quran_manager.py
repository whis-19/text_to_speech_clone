"""
Quran Text Manager for the Quran Reciter application.
Handles loading, parsing, and retrieving Quran text by Surah and Ayah.
"""

import json
import os
from typing import List, Dict, Optional, Tuple


class QuranManager:
    """Manages Quran text data - loading, parsing, and retrieval."""
    
    # Surah metadata: (name_arabic, name_english, total_ayahs)
    SURAH_INFO = {
        1: ("الفاتحة", "Al-Fatiha", 7),
        2: ("البقرة", "Al-Baqarah", 286),
        3: ("آل عمران", "Aal-E-Imran", 200),
        4: ("النساء", "An-Nisa", 176),
        5: ("المائدة", "Al-Ma'idah", 120),
        6: ("الأنعام", "Al-An'am", 165),
        7: ("الأعراف", "Al-A'raf", 206),
        8: ("الأنفال", "Al-Anfal", 75),
        9: ("التوبة", "At-Tawbah", 129),
        10: ("يونس", "Yunus", 109),
        11: ("هود", "Hud", 123),
        12: ("يوسف", "Yusuf", 111),
        13: ("الرعد", "Ar-Ra'd", 43),
        14: ("إبراهيم", "Ibrahim", 52),
        15: ("الحجر", "Al-Hijr", 99),
        16: ("النحل", "An-Nahl", 128),
        17: ("الإسراء", "Al-Isra", 111),
        18: ("الكهف", "Al-Kahf", 110),
        19: ("مريم", "Maryam", 98),
        20: ("طه", "Ta-Ha", 135),
        21: ("الأنبياء", "Al-Anbiya", 112),
        22: ("الحج", "Al-Hajj", 78),
        23: ("المؤمنون", "Al-Mu'minun", 118),
        24: ("النور", "An-Nur", 64),
        25: ("الفرقان", "Al-Furqan", 77),
        26: ("الشعراء", "Ash-Shu'ara", 227),
        27: ("النمل", "An-Naml", 93),
        28: ("القصص", "Al-Qasas", 88),
        29: ("العنكبوت", "Al-Ankabut", 69),
        30: ("الروم", "Ar-Rum", 60),
        31: ("لقمان", "Luqman", 34),
        32: ("السجدة", "As-Sajdah", 30),
        33: ("الأحزاب", "Al-Ahzab", 73),
        34: ("سبأ", "Saba", 54),
        35: ("فاطر", "Fatir", 45),
        36: ("يس", "Ya-Sin", 83),
        37: ("الصافات", "As-Saffat", 182),
        38: ("ص", "Sad", 88),
        39: ("الزمر", "Az-Zumar", 75),
        40: ("غافر", "Ghafir", 85),
        41: ("فصلت", "Fussilat", 54),
        42: ("الشورى", "Ash-Shura", 53),
        43: ("الزخرف", "Az-Zukhruf", 89),
        44: ("الدخان", "Ad-Dukhan", 59),
        45: ("الجاثية", "Al-Jathiyah", 37),
        46: ("الأحقاف", "Al-Ahqaf", 35),
        47: ("محمد", "Muhammad", 38),
        48: ("الفتح", "Al-Fath", 29),
        49: ("الحجرات", "Al-Hujurat", 18),
        50: ("ق", "Qaf", 45),
        51: ("الذاريات", "Adh-Dhariyat", 60),
        52: ("الطور", "At-Tur", 49),
        53: ("النجم", "An-Najm", 62),
        54: ("القمر", "Al-Qamar", 55),
        55: ("الرحمن", "Ar-Rahman", 78),
        56: ("الواقعة", "Al-Waqi'ah", 96),
        57: ("الحديد", "Al-Hadid", 29),
        58: ("المجادلة", "Al-Mujadilah", 22),
        59: ("الحشر", "Al-Hashr", 24),
        60: ("الممتحنة", "Al-Mumtahanah", 13),
        61: ("الصف", "As-Saff", 14),
        62: ("الجمعة", "Al-Jumu'ah", 11),
        63: ("المنافقون", "Al-Munafiqun", 11),
        64: ("التغابن", "At-Taghabun", 18),
        65: ("الطلاق", "At-Talaq", 12),
        66: ("التحريم", "At-Tahrim", 12),
        67: ("الملك", "Al-Mulk", 30),
        68: ("القلم", "Al-Qalam", 52),
        69: ("الحاقة", "Al-Haqqah", 52),
        70: ("المعارج", "Al-Ma'arij", 44),
        71: ("نوح", "Nuh", 28),
        72: ("الجن", "Al-Jinn", 28),
        73: ("المزمل", "Al-Muzzammil", 20),
        74: ("المدثر", "Al-Muddaththir", 56),
        75: ("القيامة", "Al-Qiyamah", 40),
        76: ("الإنسان", "Al-Insan", 31),
        77: ("المرسلات", "Al-Mursalat", 50),
        78: ("النبأ", "An-Naba", 40),
        79: ("النازعات", "An-Nazi'at", 46),
        80: ("عبس", "Abasa", 42),
        81: ("التكوير", "At-Takwir", 29),
        82: ("الانفطار", "Al-Infitar", 19),
        83: ("المطففين", "Al-Mutaffifin", 36),
        84: ("الانشقاق", "Al-Inshiqaq", 25),
        85: ("البروج", "Al-Buruj", 22),
        86: ("الطارق", "At-Tariq", 17),
        87: ("الأعلى", "Al-A'la", 19),
        88: ("الغاشية", "Al-Ghashiyah", 26),
        89: ("الفجر", "Al-Fajr", 30),
        90: ("البلد", "Al-Balad", 20),
        91: ("الشمس", "Ash-Shams", 15),
        92: ("الليل", "Al-Layl", 21),
        93: ("الضحى", "Ad-Duha", 11),
        94: ("الشرح", "Ash-Sharh", 8),
        95: ("التين", "At-Tin", 8),
        96: ("العلق", "Al-Alaq", 19),
        97: ("القدر", "Al-Qadr", 5),
        98: ("البينة", "Al-Bayyinah", 8),
        99: ("الزلزلة", "Az-Zalzalah", 8),
        100: ("العاديات", "Al-Adiyat", 11),
        101: ("القارعة", "Al-Qari'ah", 11),
        102: ("التكاثر", "At-Takathur", 8),
        103: ("العصر", "Al-Asr", 3),
        104: ("الهمزة", "Al-Humazah", 9),
        105: ("الفيل", "Al-Fil", 5),
        106: ("قريش", "Quraysh", 4),
        107: ("الماعون", "Al-Ma'un", 7),
        108: ("الكوثر", "Al-Kawthar", 3),
        109: ("الكافرون", "Al-Kafirun", 6),
        110: ("النصر", "An-Nasr", 3),
        111: ("المسد", "Al-Masad", 5),
        112: ("الإخلاص", "Al-Ikhlas", 4),
        113: ("الفلق", "Al-Falaq", 5),
        114: ("الناس", "An-Nas", 6),
    }
    
    def __init__(self, quran_file_path: str = None):
        """Initialize the Quran manager."""
        self.quran_data = {}
        self.file_path = quran_file_path
        
        if quran_file_path and os.path.exists(quran_file_path):
            self.load_quran_file(quran_file_path)
    
    def load_quran_file(self, file_path: str) -> bool:
        """
        Load Quran text from a file.
        Supports JSON and TXT formats.
        """
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.json':
                return self._load_json(file_path)
            elif ext == '.txt':
                return self._load_txt(file_path)
            else:
                print(f"Unsupported file format: {ext}")
                return False
        except Exception as e:
            print(f"Error loading Quran file: {e}")
            return False
    
    def _load_json(self, file_path: str) -> bool:
        """Load Quran from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if 'data' in data and 'surahs' in data['data']:
            # AlQuran.cloud API format
            for surah in data['data']['surahs']:
                surah_num = surah['number']
                self.quran_data[surah_num] = {
                    'name': surah.get('name', ''),
                    'englishName': surah.get('englishName', ''),
                    'ayahs': {}
                }
                for ayah in surah['ayahs']:
                    ayah_num = ayah['numberInSurah']
                    self.quran_data[surah_num]['ayahs'][ayah_num] = ayah['text']
        
        elif 'surahs' in data:
            # Simple surahs array format
            for surah in data['surahs']:
                surah_num = surah.get('number', surah.get('id'))
                self.quran_data[surah_num] = {
                    'name': surah.get('name', ''),
                    'englishName': surah.get('englishName', surah.get('english_name', '')),
                    'ayahs': {}
                }
                ayahs = surah.get('ayahs', surah.get('verses', []))
                for ayah in ayahs:
                    ayah_num = ayah.get('numberInSurah', ayah.get('id', ayah.get('verse_number')))
                    text = ayah.get('text', ayah.get('verse', ''))
                    self.quran_data[surah_num]['ayahs'][ayah_num] = text
        
        else:
            # Try to detect format automatically
            # Format: {surah_num: {ayah_num: text}}
            for key, value in data.items():
                surah_num = int(key)
                if isinstance(value, dict):
                    self.quran_data[surah_num] = {
                        'name': self.SURAH_INFO.get(surah_num, ('', '', 0))[0],
                        'englishName': self.SURAH_INFO.get(surah_num, ('', '', 0))[1],
                        'ayahs': {int(k): v for k, v in value.items()}
                    }
        
        print(f"Loaded {len(self.quran_data)} surahs from JSON.")
        return len(self.quran_data) > 0
    
    def _load_txt(self, file_path: str) -> bool:
        """
        Load Quran from TXT file.
        Expected format: surah_num|ayah_num|text (one per line)
        Or: surah_num:ayah_num text
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try different delimiters
            parts = None
            if '|' in line:
                parts = line.split('|', 2)
            elif '\t' in line:
                parts = line.split('\t', 2)
            elif ':' in line:
                # Format: 1:1 بسم الله...
                ref_text = line.split(' ', 1)
                if len(ref_text) == 2 and ':' in ref_text[0]:
                    ref_parts = ref_text[0].split(':')
                    parts = [ref_parts[0], ref_parts[1], ref_text[1]]
            
            if parts and len(parts) >= 3:
                try:
                    surah_num = int(parts[0])
                    ayah_num = int(parts[1])
                    text = parts[2].strip()
                    
                    if surah_num not in self.quran_data:
                        self.quran_data[surah_num] = {
                            'name': self.SURAH_INFO.get(surah_num, ('', '', 0))[0],
                            'englishName': self.SURAH_INFO.get(surah_num, ('', '', 0))[1],
                            'ayahs': {}
                        }
                    
                    self.quran_data[surah_num]['ayahs'][ayah_num] = text
                except ValueError:
                    continue
        
        print(f"Loaded {len(self.quran_data)} surahs from TXT.")
        return len(self.quran_data) > 0
    
    def get_surah_list(self) -> List[Tuple[int, str, str, int]]:
        """
        Get list of all surahs.
        Returns: List of (number, arabic_name, english_name, total_ayahs)
        """
        return [
            (num, info[0], info[1], info[2])
            for num, info in self.SURAH_INFO.items()
        ]
    
    def get_surah_name(self, surah_num: int) -> Tuple[str, str]:
        """Get surah name (arabic, english)."""
        info = self.SURAH_INFO.get(surah_num)
        if info:
            return info[0], info[1]
        return "", ""
    
    def get_total_ayahs(self, surah_num: int) -> int:
        """Get total number of ayahs in a surah."""
        info = self.SURAH_INFO.get(surah_num)
        return info[2] if info else 0
    
    def get_ayah(self, surah_num: int, ayah_num: int) -> Optional[str]:
        """Get a specific ayah text."""
        if surah_num in self.quran_data:
            return self.quran_data[surah_num]['ayahs'].get(ayah_num)
        return None
    
    def get_ayah_range(self, surah_num: int, start: int, end: int) -> str:
        """
        Get text for a range of ayahs.
        Returns concatenated text with ayah markers.
        """
        if surah_num not in self.quran_data:
            return ""
        
        ayahs = self.quran_data[surah_num]['ayahs']
        texts = []
        
        for ayah_num in range(start, end + 1):
            if ayah_num in ayahs:
                texts.append(ayahs[ayah_num])
        
        return ' '.join(texts)
    
    def get_full_surah(self, surah_num: int) -> str:
        """Get full surah text."""
        if surah_num not in self.quran_data:
            return ""
        
        ayahs = self.quran_data[surah_num]['ayahs']
        total = self.get_total_ayahs(surah_num)
        
        texts = []
        for ayah_num in range(1, total + 1):
            if ayah_num in ayahs:
                texts.append(ayahs[ayah_num])
        
        return ' '.join(texts)
    
    def is_loaded(self) -> bool:
        """Check if Quran data is loaded."""
        return len(self.quran_data) > 0
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded data."""
        total_ayahs = sum(
            len(surah['ayahs']) 
            for surah in self.quran_data.values()
        )
        return {
            'total_surahs': len(self.quran_data),
            'total_ayahs': total_ayahs,
            'file_path': self.file_path
        }


# Global instance
quran = QuranManager()


def load_quran(file_path: str) -> bool:
    """Load Quran data from file."""
    return quran.load_quran_file(file_path)


def get_ayah_text(surah: int, start: int, end: int = None) -> str:
    """Get ayah text for given range."""
    if end is None:
        end = start
    return quran.get_ayah_range(surah, start, end)
