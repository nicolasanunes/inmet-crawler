from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page
from datetime import datetime, timedelta
import os
import asyncio


class InmetScraper:
    """
    Scraper para download automatizado de dados meteorológicos do INMET.
    Utiliza Playwright para simular interações no site oficial.
    """
    
    BASE_URL = "https://tempo.inmet.gov.br/TabelaEstacoes"
    MENU_SELECTOR = 'div.left.menu i.bars.icon'
    DATE_INPUT_SELECTOR = 'input[type="date"]'
    
    def __init__(self, download_dir: str = None, headless: bool = True, debug: bool = False):
        """
        Inicializa o scraper.
        
        Args:
            download_dir: Diretório para salvar arquivos baixados. Se None, usa 'downloads/' na raiz do projeto.
            headless: Se True, executa navegador em modo headless (sem interface gráfica).
            debug: Se True, ativa modo debug com logs detalhados e screenshots.
        """
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads')
        
        self.download_dir = download_dir
        self.headless = headless
        self.debug = debug
        os.makedirs(self.download_dir, exist_ok=True)
    
    def get_yesterday_date(self) -> datetime:
        """Retorna a data de ontem."""
        return datetime.now() - timedelta(days=1)
    
    async def _fill_date_field(self, page: Page, field_index: int, iso_date: str):
        """
        Preenche um campo de data e dispara eventos React.
        
        Args:
            page: Página do Playwright
            field_index: Índice do campo de data (0 para Data Início, 1 para Data Fim)
            iso_date: Data no formato ISO (YYYY-MM-DD)
        """
        date_field = page.locator(self.DATE_INPUT_SELECTOR).nth(field_index)
        
        await date_field.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        
        await date_field.click()
        await asyncio.sleep(0.3)
        await date_field.fill('')
        await asyncio.sleep(0.2)
        await date_field.fill(iso_date)
        await asyncio.sleep(0.3)
        
        # Dispara eventos React para notificar mudança
        await page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input[type="date"]');
                const input = inputs[{field_index}];
                
                if (input) {{
                    input.value = '{iso_date}';
                    
                    const nativeInputSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 
                        'value'
                    ).set;
                    nativeInputSetter.call(input, '{iso_date}');
                    
                    ['input', 'change', 'blur'].forEach(eventType => {{
                        input.dispatchEvent(new Event(eventType, {{ bubbles: true }}));
                    }});
                }}
            }}
        """)
        
        await asyncio.sleep(0.5)
    
    async def _open_side_menu(self, page: Page):
        """Abre o menu lateral da página."""
        menu_button = page.locator(self.MENU_SELECTOR).first
        
        if await menu_button.count() == 0:
            raise Exception("Menu lateral não encontrado")
        
        await menu_button.click()
        await asyncio.sleep(2)
    
    async def _click_generate_table_button(self, page: Page):
        """Clica no botão 'Gerar Tabela' usando hover + click."""
        await asyncio.sleep(2)
        
        all_buttons = page.locator('button')
        generate_button = all_buttons.nth(2)
        
        if await generate_button.count() == 0:
            raise Exception("Botão 'Gerar Tabela' não encontrado")
        
        await generate_button.scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        await generate_button.hover()
        await asyncio.sleep(0.3)
        await generate_button.click(force=True, delay=100)
        
        await asyncio.sleep(3)
    
    async def _find_download_button(self, page: Page):
        """Localiza o botão de download CSV."""
        selectors = [
            'a.ui.button:has-text("Baixar CSV")',
            'a.ui.button:has-text("CSV")',
            'a[download*="csv"]',
            'a[download*="CSV"]',
            'button:has-text("Baixar CSV")',
        ]
        
        for selector in selectors:
            try:
                button = page.locator(selector).first
                if await button.count() > 0:
                    return button
            except:
                continue
        
        raise Exception("Botão 'Baixar CSV' não encontrado")
    
    async def download_csv(self, station_code: str = "A569", target_date: datetime = None) -> str:
        """
        Baixa arquivo CSV de uma estação meteorológica do INMET.
        
        Workflow:
        1. Acessa página da estação
        2. Abre menu lateral
        3. Preenche datas de início e fim
        4. Clica em 'Gerar Tabela'
        5. Aguarda geração
        6. Baixa o CSV
        
        Args:
            station_code: Código da estação (ex: A569 para Brasília)
            target_date: Data dos dados. Se None, usa dia anterior
            
        Returns:
            Caminho completo do arquivo CSV baixado
            
        Raises:
            Exception: Em caso de erro no processo de download
        """
        if target_date is None:
            target_date = self.get_yesterday_date()
        
        url = f"{self.BASE_URL}/{station_code}"
        iso_date = target_date.strftime('%Y-%m-%d')
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            
            context = await browser.new_context(
                accept_downloads=True,
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # Acessa a página
                if self.debug:
                    print(f"[DEBUG] Acessando: {url}")
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)
                
                await self._open_side_menu(page)
                
                date_inputs = page.locator(self.DATE_INPUT_SELECTOR)
                count = await date_inputs.count()
                
                if count < 2:
                    raise Exception(f"Esperados 2 campos de data, encontrados {count}")
                
                await self._fill_date_field(page, 0, iso_date)
                await self._fill_date_field(page, 1, iso_date)
                
                await self._click_generate_table_button(page)
                
                download_button = await self._find_download_button(page)
                
                async with page.expect_download(timeout=30000) as download_info:
                    await download_button.click()
                
                download = await download_info.value
                
                filename = f"inmet_{station_code}_{target_date.strftime('%Y%m%d')}.csv"
                filepath = os.path.join(self.download_dir, filename)
                await download.save_as(filepath)
                
                return filepath
                
            except PlaywrightTimeoutError as e:
                raise Exception(f"Timeout ao acessar página do INMET: {str(e)}")
            except Exception as e:
                raise Exception(f"Erro ao baixar CSV: {str(e)}")
            finally:
                await context.close()
                await browser.close()
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """
        Remove arquivos antigos do diretório de downloads.
        
        Args:
            days: Número de dias para manter arquivos (padrão: 7)
            
        Returns:
            Quantidade de arquivos removidos
        """
        import time
        
        now = time.time()
        cutoff = now - (days * 86400)
        removed_count = 0
        
        for filename in os.listdir(self.download_dir):
            filepath = os.path.join(self.download_dir, filename)
            
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
                try:
                    os.remove(filepath)
                    removed_count += 1
                except:
                    pass
        
        return removed_count

