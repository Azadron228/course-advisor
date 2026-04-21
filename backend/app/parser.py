from bs4 import BeautifulSoup
from typing import List
from .api.v1.schemas.recommendations import TranscriptEntry

def parse_transcript_html(html_content: str) -> List[TranscriptEntry]:
    soup = BeautifulSoup(html_content, 'html.parser')
    entries = []
    
    # The courses are in a table with class 'commonTable'
    # We need the first table that has at least 7 columns in its rows (excluding header rows)
    tables = soup.find_all('table', class_='commonTable')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            # Typical row: [Index, Name, Credits, Percent, Alpha, Points, Traditional]
            if len(cols) >= 4:
                try:
                    # Skip header rows if they contain non-numeric data for credits/marks
                    name = cols[1].get_text(strip=True)
                    if not name or name.lower() in ['наименование дисциплины', 'courses']:
                        continue
                        
                    credits_str = cols[2].get_text(strip=True)
                    mark_str = cols[3].get_text(strip=True)
                    
                    # Basic check if it's a data row
                    credits = float(credits_str)
                    mark = float(mark_str)
                    
                    entries.append(TranscriptEntry(
                        subject_name=name,
                        credits=credits,
                        mark=mark
                    ))
                except (ValueError, IndexError):
                    continue
                    
    return entries
