import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinvizScraper:
    def __init__(self):
        self.base_url = "https://finviz.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_news_for_stock(self, symbol: str, max_pages: int = 5) -> List[Dict]:
        """
        Scrape news articles for a specific stock symbol from Finviz
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            max_pages: Maximum number of pages to scrape (default: 5)
        
        Returns:
            List of dictionaries containing article information
        """
        articles = []
        
        try:
            news_url = f"{self.base_url}/quote.ashx?t={symbol.upper()}"
            
            
            response = self.session.get(news_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_table = soup.find('table', class_='body-table-news-wrapper news-table_wrapper')
            
            if not news_table:
                news_table = soup.find('table', {'id': 'news-table'})
                
            if not news_table:
                news_table = soup.find('table', class_=re.compile(r'news', re.I))
                if not news_table:
                    news_table = soup.find('table')
                    if news_table:
                        news_links = news_table.find_all('a', href=re.compile(r'http'))
                        if len(news_links) < 3:
                            news_table = None
            
            if not news_table:
                return articles
            
            rows = news_table.find_all('tr')
            
            for row in rows:
                try:
                    article_data = self._parse_news_row(row, symbol)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    continue
            
            
            seen_links = set()
            unique_articles = []
            symbol_upper = symbol.upper()
            
            search_terms = [symbol_upper]
            
            company_names = {
                'AAPL': ['APPLE'],
                'MSFT': ['MICROSOFT'],
                'GOOGL': ['GOOGLE', 'ALPHABET'],
                'AMZN': ['AMAZON'],
                'TSLA': ['TESLA'],
                'META': ['FACEBOOK', 'META'],
                'NVDA': ['NVIDIA'],
                'NFLX': ['NETFLIX'],
                'AMD': ['ADVANCED MICRO DEVICES'],
                'INTC': ['INTEL'],
                'CRM': ['SALESFORCE'],
                'ORCL': ['ORACLE'],
                'ADBE': ['ADOBE'],
                'PYPL': ['PAYPAL'],
                'UBER': ['UBER'],
                'LYFT': ['LYFT'],
                'SQ': ['SQUARE', 'BLOCK'],
                'ROKU': ['ROKU'],
                'ZM': ['ZOOM'],
                'DOCU': ['DOCUSIGN'],
                'SNOW': ['SNOWFLAKE'],
                'PLTR': ['PALANTIR'],
                'COIN': ['COINBASE'],
                'HOOD': ['ROBINHOOD'],
                'SPOT': ['SPOTIFY'],
                'TWTR': ['TWITTER'],
                'SNAP': ['SNAPCHAT'],
                'PINS': ['PINTEREST'],
                'SHOP': ['SHOPIFY'],
                'ABNB': ['AIRBNB'],
                'DDOG': ['DATADOG'],
                'NET': ['CLOUDFLARE'],
                'OKTA': ['OKTA'],
                'CRWD': ['CROWDSTRIKE'],
                'ZS': ['ZSCALER'],
                'PANW': ['PALO ALTO'],
                'FTNT': ['FORTINET'],
                'CHKP': ['CHECK POINT'],
                'CYBR': ['CYBERARK'],
                'SAIL': ['SAILPOINT'],
                'ESTC': ['ELASTIC'],
                'MDB': ['MONGODB'],
                'DIS': ['DISNEY'],
                'NKE': ['NIKE'],
                'SBUX': ['STARBUCKS'],
                'MCD': ['MCDONALDS'],
                'KO': ['COCA COLA'],
                'PEP': ['PEPSICO'],
                'WMT': ['WALMART'],
                'TGT': ['TARGET'],
                'HD': ['HOME DEPOT'],
                'LOW': ['LOWES'],
                'COST': ['COSTCO'],
                'AMAT': ['APPLIED MATERIALS'],
                'LRCX': ['LAM RESEARCH'],
                'KLAC': ['KLA'],
                'MU': ['MICRON'],
                'QCOM': ['QUALCOMM'],
                'AVGO': ['BROADCOM'],
                'TXN': ['TEXAS INSTRUMENTS'],
                'ADI': ['ANALOG DEVICES'],
                'MRVL': ['MARVELL'],
                'SWKS': ['SKYWORKS'],
                'QRVO': ['QORVO'],
                'CRUS': ['CIRRUS LOGIC'],
                'SLAB': ['SILICON LABS'],
                'MCHP': ['MICROCHIP'],
                'ON': ['ON SEMICONDUCTOR'],
                'MPWR': ['MONOLITHIC POWER'],
                'POWI': ['POWER INTEGRATIONS'],
                'DIOD': ['DIODES'],
                'ALGM': ['ALLEGRO'],
                'IMOS': ['CHIPMOS'],
                'UMC': ['UNITED MICROELECTRONICS'],
                'TSM': ['TAIWAN SEMICONDUCTOR'],
                'ASML': ['ASML'],
                'NXPI': ['NXP'],
                'STM': ['ST MICROELECTRONICS'],
                'INFN': ['INFINERA'],
                'LITE': ['LUMENTUM'],
                'ACIA': ['ACACIA'],
                'COHR': ['COHERENT'],
                'IIVI': ['II VI'],
                'NPTN': ['NEOPHOTONICS'],
                'AAOI': ['APPLIED OPTOELECTRONICS'],
                'OCCL': ['OPTICAL CABLE'],
                'EMAN': ['EMANATION'],
                'FNSR': ['FINISAR'],
                'OCLR': ['OCLARO'],
                'PXLW': ['PIXELWORKS'],
                'RPXC': ['RPX'],
                'SMTC': ['SEMTECH'],
                'SITM': ['SITIME'],
                'SYNA': ['SYNAPTICS'],
                'XLNX': ['XILINX']
            }
            
            if symbol_upper in company_names:
                search_terms.extend(company_names[symbol_upper])
            
            for article in articles:
                if article['link'] not in seen_links:
                    title = article.get('title', '')
                    
                    headline = title.split(' - ')[0].split(' | ')[0].split(' :: ')[0].split(' ... ')[0]
                    headline = headline.split(' (')[0].split(' [')[0].split(' {')[0]
                    headline_upper = headline.upper()
                    
                    import re
                    found_match = False
                    for term in search_terms:
                        pattern = r'\b' + re.escape(term) + r'\b'
                        if re.search(pattern, headline_upper):
                            found_match = True
                            break
                    
                    if found_match:
                        seen_links.add(article['link'])
                        unique_articles.append(article)
                    else:
                        continue
            
            return unique_articles
            
        except requests.RequestException as e:
            return articles
        except Exception as e:

            pass
            return articles
    
    def _parse_news_row(self, row, symbol: str) -> Optional[Dict]:
        """Parse a single news row from the news table"""
        try:
            cells = row.find_all('td')
            if len(cells) < 2:
                return None
            
            date_cell = cells[0]
            time_cell = cells[1] if len(cells) > 1 else None
            
            date_text = date_cell.get_text(strip=True)
            time_text = time_cell.get_text(strip=True) if time_cell else ""
            
            published_date = self._parse_datetime(date_text, time_text)
            
            title_cell = cells[2] if len(cells) > 2 else cells[1]
            title_link = title_cell.find('a')
            
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            link = title_link.get('href', '')
            
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            source = ""
            source_elem = title_cell.find('span', class_='news-source')
            if source_elem:
                source = source_elem.get_text(strip=True)
            
            return {
                'title': title,
                'link': link,
                'summary': '',
                'source': source,
                'stock_symbol': symbol.upper(),
                'published_date': published_date
            }
            
        except Exception as e:

            
            pass
            return None
    
    def _parse_news_page(self, soup: BeautifulSoup, symbol: str) -> List[Dict]:
        """Parse news from the dedicated news page"""
        articles = []
        
        try:
            news_items = soup.find_all(['div', 'tr'], class_=re.compile(r'news|article', re.I))
            
            for item in news_items:
                try:
                    title_link = item.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    link = title_link.get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = urljoin(self.base_url, link)
                    
                    date_elem = item.find(['span', 'div'], class_=re.compile(r'date|time', re.I))
                    published_date = None
                    if date_elem:
                        published_date = self._parse_datetime(date_elem.get_text(strip=True))
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': '',
                        'source': '',
                        'stock_symbol': symbol.upper(),
                        'published_date': published_date
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:

                    
            pass
        return articles
    
    def _parse_stock_news_page(self, soup: BeautifulSoup, symbol: str) -> List[Dict]:
        """Parse news from the stock-specific news page"""
        articles = []
        
        try:
            news_table = soup.find('table', {'id': 'news-table'})
            if news_table:
                rows = news_table.find_all('tr')
                for row in rows:
                    try:
                        article_data = self._parse_news_row(row, symbol)
                        if article_data:
                            articles.append(article_data)
                    except Exception as e:
                        continue
            
            news_items = soup.find_all(['div', 'tr'], class_=re.compile(r'news|article', re.I))
            
            for item in news_items:
                try:
                    title_link = item.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    link = title_link.get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = urljoin(self.base_url, link)
                    
                    date_elem = item.find(['span', 'div'], class_=re.compile(r'date|time', re.I))
                    published_date = None
                    if date_elem:
                        published_date = self._parse_datetime(date_elem.get_text(strip=True))
                    
                    source = ""
                    source_elem = item.find(['span', 'div'], class_=re.compile(r'source|publisher', re.I))
                    if source_elem:
                        source = source_elem.get_text(strip=True)
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': '',
                        'source': source,
                        'stock_symbol': symbol.upper(),
                        'published_date': published_date
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:

                    
            pass
        return articles
    
    def _extract_news_from_quote_page(self, soup: BeautifulSoup, symbol: str) -> List[Dict]:
        """Extract news headlines from the main quote page"""
        articles = []
        
        try:
            news_table = soup.find('table', {'id': 'news-table'})
            if news_table:
                rows = news_table.find_all('tr')
                for row in rows:
                    try:
                        article_data = self._parse_news_row(row, symbol)
                        if article_data:
                            articles.append(article_data)
                    except Exception as e:
                        continue
            
            if not articles:
                news_containers = soup.find_all(['div', 'table'], class_=re.compile(r'news|article', re.I))
                
                for container in news_containers:
                    links = container.find_all('a', href=True)
                    for link in links:
                        try:
                            href = link.get('href', '')
                            title = link.get_text(strip=True)
                            
                            if not title or len(title) < 10:
                                continue
                            
                            if href.startswith('/') or 'finviz.com' in href:
                                continue
                            
                            if not any(news_domain in href.lower() for news_domain in [
                                'reuters.com', 'bloomberg.com', 'cnbc.com', 'yahoo.com', 
                                'marketwatch.com', 'wsj.com', 'ft.com', 'seekingalpha.com',
                                'benzinga.com', 'investing.com', 'nasdaq.com', 'fool.com',
                                'barrons.com', 'forbes.com', 'businesswire.com', 'prnewswire.com',
                                'techcrunch.com', 'theverge.com', 'engadget.com', 'arstechnica.com'
                            ]):
                                continue
                            
                            if not href.startswith('http'):
                                href = urljoin(self.base_url, href)
                            
                            published_date = None
                            parent = link.parent
                            while parent and parent.name != 'body':
                                date_text = parent.get_text(strip=True)
                                if re.match(r'\d{1,2}:\d{2}', date_text) or re.match(r'\d{1,2}/\d{1,2}', date_text):
                                    published_date = self._parse_datetime(date_text)
                                    break
                                parent = parent.parent
                            
                            articles.append({
                                'title': title,
                                'link': href,
                                'summary': '',
                                'source': '',
                                'stock_symbol': symbol.upper(),
                                'published_date': published_date
                            })
                            
                        except Exception as e:
                            continue
                    
        except Exception as e:

                    
            pass
        return articles
    
    def _parse_news_section(self, soup: BeautifulSoup, symbol: str) -> List[Dict]:
        """Parse news from the dedicated news section page"""
        articles = []
        
        try:
            news_table = soup.find('table', {'id': 'news-table'})
            if news_table:
                rows = news_table.find_all('tr')
                for row in rows:
                    try:
                        article_data = self._parse_news_row(row, symbol)
                        if article_data:
                            articles.append(article_data)
                    except Exception as e:
                        continue
            
            news_items = soup.find_all(['div', 'tr'], class_=re.compile(r'news|article', re.I))
            
            for item in news_items:
                try:
                    title_link = item.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    link = title_link.get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = urljoin(self.base_url, link)
                    
                    date_elem = item.find(['span', 'div'], class_=re.compile(r'date|time', re.I))
                    published_date = None
                    if date_elem:
                        published_date = self._parse_datetime(date_elem.get_text(strip=True))
                    
                    source = ""
                    source_elem = item.find(['span', 'div'], class_=re.compile(r'source|publisher', re.I))
                    if source_elem:
                        source = source_elem.get_text(strip=True)
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': '',
                        'source': source,
                        'stock_symbol': symbol.upper(),
                        'published_date': published_date
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:

                    
            pass
        return articles
    
    def _parse_datetime(self, date_text: str, time_text: str = "") -> Optional[datetime]:
        """Parse date and time strings into datetime object"""
        try:
            date_text = date_text.strip()
            time_text = time_text.strip()
            
            now = datetime.now()
            
            if 'Today' in date_text or 'today' in date_text:
                date_obj = now.date()
            elif 'Yesterday' in date_text or 'yesterday' in date_text:
                from datetime import timedelta
                date_obj = (now - timedelta(days=1)).date()
            elif re.match(r'\d{1,2}-\d{1,2}', date_text):
                month, day = date_text.split('-')
                date_obj = now.replace(month=int(month), day=int(day)).date()
            else:
                try:
                    date_obj = datetime.strptime(date_text, '%b-%d-%y').date()
                except:
                    try:
                        date_obj = datetime.strptime(date_text, '%m-%d-%y').date()
                    except:
                        date_obj = now.date()
            
            time_obj = None
            if time_text:
                try:
                    time_obj = datetime.strptime(time_text, '%I:%M%p').time()
                except:
                    try:
                        time_obj = datetime.strptime(time_text, '%H:%M').time()
                    except:
                        pass
            
            if time_obj:
                return datetime.combine(date_obj, time_obj)
            else:
                return datetime.combine(date_obj, datetime.min.time())
                
        except Exception as e:

                
            pass
            return None
    
    def scrape_multiple_stocks(self, symbols: List[str], max_pages_per_stock: int = 5) -> Dict[str, List[Dict]]:
        """
        Scrape news for multiple stock symbols
        
        Args:
            symbols: List of stock symbols
            max_pages_per_stock: Maximum pages to scrape per stock
        
        Returns:
            Dictionary mapping stock symbols to their articles
        """
        results = {}
        
        for symbol in symbols:
            articles = self.get_news_for_stock(symbol, max_pages_per_stock)
            results[symbol] = articles
            
            time.sleep(1)
        
        return results
    
    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Scrape comprehensive stock data from Finviz
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
        
        Returns:
            Dictionary containing stock data or None if not found
        """
        try:
            quote_url = f"{self.base_url}/quote.ashx?t={symbol.upper()}"
            
            
            response = self.session.get(quote_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            quote_table = soup.find('table', {'class': 'snapshot-table2'})
            
            if not quote_table:
                return None
            
            stock_data = self._parse_stock_table(quote_table, symbol)
            
            if stock_data:
                return stock_data
            else:
                return None
                
        except requests.RequestException as e:
            return None
        except Exception as e:

            pass
            return None
    
    def _parse_stock_table(self, table, symbol: str) -> Optional[Dict]:
        """Parse the stock quote table and extract data"""
        try:
            stock_data = {
                'symbol': symbol.upper(),
                'name': '',
                'price': None,
                'change': None,
                'change_percent': None,
                'volume': None,
                'avg_volume': None,
                'market_cap': None,
                'pe_ratio': None,
                'eps': None,
                'dividend': None,
                'dividend_yield': None,
                'sector': None,
                'industry': None,
                'country': None,
                'exchange': None,
                'ipo_date': None,
                'currency': 'USD',
                'high_52w': None,
                'low_52w': None,
                'rsi': None,
                'sma_20': None,
                'sma_50': None,
                'sma_200': None
            }
            
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    for i in range(0, len(cells) - 1, 2):
                        label_cell = cells[i]
                        value_cell = cells[i + 1]
                        
                        label = label_cell.get_text(strip=True).lower()
                        value = value_cell.get_text(strip=True)
                        
                        if label == 'company':
                            stock_data['name'] = value
                        elif label == 'price':
                            stock_data['price'] = self._parse_float(value)
                        elif label == 'change':
                            stock_data['change'] = self._parse_float(value)
                        elif label == 'volume':
                            stock_data['volume'] = self._parse_int(value)
                        elif label == 'avg volume':
                            stock_data['avg_volume'] = self._parse_int(value)
                        elif label == 'market cap':
                            stock_data['market_cap'] = value
                        elif label == 'pe':
                            stock_data['pe_ratio'] = self._parse_float(value)
                        elif label == 'eps (ttm)':
                            stock_data['eps'] = self._parse_float(value)
                        elif label == 'dividend':
                            stock_data['dividend'] = self._parse_float(value)
                        elif label == 'dividend %':
                            stock_data['dividend_yield'] = self._parse_float(value)
                        elif label == 'sector':
                            stock_data['sector'] = value
                        elif label == 'industry':
                            stock_data['industry'] = value
                        elif label == 'country':
                            stock_data['country'] = value
                        elif label == 'exchange':
                            stock_data['exchange'] = value
                        elif label == 'ipo date':
                            stock_data['ipo_date'] = self._parse_date(value)
                        elif label == '52w high':
                            stock_data['high_52w'] = self._parse_float(value)
                        elif label == '52w low':
                            stock_data['low_52w'] = self._parse_float(value)
                        elif label == 'rsi (14)':
                            stock_data['rsi'] = self._parse_float(value)
                        elif label == 'sma20':
                            stock_data['sma_20'] = self._parse_float(value)
                        elif label == 'sma50':
                            stock_data['sma_50'] = self._parse_float(value)
                        elif label == 'sma200':
                            stock_data['sma_200'] = self._parse_float(value)
            
            if stock_data['price'] and stock_data['change'] and not stock_data['change_percent']:
                stock_data['change_percent'] = (stock_data['change'] / (stock_data['price'] - stock_data['change'])) * 100
            
            return stock_data
            
        except Exception as e:

            
            pass
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parse string value to float, handling various formats"""
        if not value or value == '-':
            return None
        
        try:
            cleaned = re.sub(r'[^\d.-]', '', value)
            if cleaned:
                return float(cleaned)
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Parse string value to int, handling various formats"""
        if not value or value == '-':
            return None
        
        try:
            cleaned = re.sub(r'[^\d.-]', '', value)
            if cleaned:
                return int(float(cleaned))
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _parse_date(self, value: str) -> Optional[date]:
        """Parse string value to date"""
        if not value or value == '-':
            return None
        
        try:
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        except (ValueError, TypeError):
            pass
        
        return None
    
    def get_popular_stocks(self) -> List[str]:
        """
        Get list of popular stock symbols from Finviz
        This is a predefined list of commonly traded stocks
        """
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B',
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
            'NFLX', 'CRM', 'INTC', 'CMCSA', 'PFE', 'ABT', 'TMO', 'COST', 'PEP',
            'WMT', 'DHR', 'VZ', 'ACN', 'NKE', 'TXN', 'QCOM', 'NEE', 'HON',
            'UNP', 'IBM', 'AMGN', 'PM', 'SPGI', 'RTX', 'LOW', 'SBUX', 'AMD',
            'INTU', 'CAT', 'GS', 'AXP', 'BLK', 'SYK', 'GILD', 'CVS', 'MDT'
        ]
    
    def get_stocks_by_sector(self, sector: str) -> List[str]:
        """
        Get stock symbols for a specific sector
        This would require scraping the sector page
        """
        sector_stocks = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'ADBE', 'CRM', 'INTC', 'AMD'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABT', 'TMO', 'DHR', 'AMGN', 'GILD', 'MDT', 'SYK'],
            'Financial': ['BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'AXP', 'BLK', 'SPGI'],
            'Consumer': ['PG', 'HD', 'DIS', 'COST', 'PEP', 'WMT', 'NKE', 'SBUX', 'LOW', 'TGT'],
            'Industrial': ['HON', 'UNP', 'CAT', 'RTX', 'LMT', 'BA', 'GE', 'MMM', 'UPS', 'FDX']
        }
        
        return sector_stocks.get(sector, [])

if __name__ == "__main__":
    scraper = FinvizScraper()
    
    articles = scraper.get_news_for_stock("AAPL")
    
    for article in articles[:3]:
        pass
    
    stock_data = scraper.get_stock_data("AAPL")
    if stock_data:
        pass