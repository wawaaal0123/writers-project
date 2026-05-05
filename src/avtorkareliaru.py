import requests
from bs4 import BeautifulSoup
import re
import time

print("=" * 60)
print("ПАРСИНГ ПИСАТЕЛЕЙ КАРЕЛИИ")
print("=" * 60)

base_url = 'http://avtor.karelia.ru'
index_url = base_url + '/ukazatel.html'

response = requests.get(index_url)
soup = BeautifulSoup(response.content, 'html.parser', from_encoding='windows-1251')

author_links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    if '/about/' in href and '.html' in href:
        full_url = base_url + href
        if full_url not in author_links:
            author_links.append(full_url)

print(f"\nНайдено авторов: {len(author_links)}")
print("=" * 60)

def extract_dates(soup):
    """Универсальная функция поиска дат в разных форматах"""
    birth_date = None
    death_date = None
    
    full_text = soup.get_text()
    
    # Формат 1: (дд.мм.гггг - дд.мм.гггг) в теге b style="color:black;"
    date_tag = soup.find('b', style="color:black;")
    if date_tag:
        match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})', date_tag.text)
        if match:
            return match.group(1), match.group(2)
    
    # Формат 2: <p><b>Дата рождения:</b> дд.мм.гггг</p>
    for p in soup.find_all('p'):
        if 'Дата рождения:' in p.get_text():
            match = re.search(r'Дата рождения:\s*(\d{2}\.\d{2}\.\d{4})', p.get_text())
            if match:
                birth_date = match.group(1)
                break
    
    # Формат 3: просто две даты через дефис где-то на странице
    if not birth_date:
        match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*[-–]\s*(\d{2}\.\d{2}\.\d{4})', full_text)
        if match:
            return match.group(1), match.group(2)
    
    # Формат 4: только одна дата (рождение) в тексте
    if not birth_date:
        dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', full_text)
        if dates:
            birth_date = dates[0]
    
    return birth_date, death_date

def extract_birth_place(soup):
    """Универсальный поиск места рождения"""
    for p in soup.find_all('p'):
        if 'Место рождения:' in p.get_text():
            match = re.search(r'Место рождения:\s*(.+?)(?:\n|$)', p.get_text())
            if match:
                return match.group(1).strip()
    return None

for i, url in enumerate(author_links, 1):
    print(f"\n{'=' * 60}")
    print(f"ПИСАТЕЛЬ {i}/{len(author_links)}")
    print(f"{'=' * 60}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка: страница не найдена")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='windows-1251')
        
        # ФИО
        name_tag = soup.find('h1')
        full_name = name_tag.text.strip() if name_tag else None
        print(f"\nФИО: {full_name}")
        
        # Даты
        birth_date, death_date = extract_dates(soup)
        
        if birth_date:
            print(f"Дата рождения: {birth_date}")
        else:
            print(f"Дата рождения: не найдена")
            
        if death_date:
            print(f"Дата смерти: {death_date}")
        
        # Место рождения
        birth_place = extract_birth_place(soup)
        if birth_place:
            print(f"Место рождения: {birth_place}")
        
        # Биография целиком
        bio_parts = []
        found = False
        for p in soup.find_all('p'):
            if found:
                if p.find('b') and ('Библиография' in p.get_text() or 'Электронные издания' in p.get_text()):
                    break
                text = p.get_text().strip()
                if text and len(text) > 20:
                    bio_parts.append(text)
            elif p.find('b') and 'Общие сведения:' in p.get_text():
                found = True
        
        if bio_parts:
            print(f"\nБиография (целиком):")
            print("-" * 40)
            print('\n\n'.join(bio_parts))
            print("-" * 40)
        
        # Произведения целиком из библиографии автора
        works = []
        for p in soup.find_all('p'):
            if p.find('b') and 'Библиография автора:' in p.get_text():
                next_ol = p.find_next_sibling('ol')
                if next_ol:
                    for li in next_ol.find_all('li'):
                        work_text = li.get_text(strip=True)
                        if work_text and 'Подробный библиографический' not in work_text:
                            works.append(work_text)
                break
        
        if works:
            print(f"\nПроизведения автора (найдено {len(works)} шт.):")
            print("-" * 40)
            for idx, work in enumerate(works, 1):
                print(f"{idx}. {work}")
                print()
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    time.sleep(0.5)

print("\n" + "=" * 60)
print("ПАРСИНГ ЗАВЕРШЕН")
print("=" * 60)
