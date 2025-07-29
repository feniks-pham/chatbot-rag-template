import os
import shutil
from markdown_crawler import md_crawl
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CrawlService:
    def __init__(self):
        self.crawler = None
    
    def _get_crawler(self):
        """Get or create crawler instance"""
        if self.crawler is None:
            logger.info("Creating new MarkdownCrawler instance")
            self.crawler = md_crawl
            logger.info("MarkdownCrawler created successfully")
        return self.crawler
    
    async def crawl_stores(self) -> str:
        """Crawl store information from the website"""
        from app.config.settings import settings
        base_dir = 'temp_crawl_stores'
        try:
            crawler = self._get_crawler()

            logger.info(f"🕸️ Starting crawl of {settings.store_url}")
            crawler(
                settings.store_url,
                max_depth=0,
                num_threads=1,
                base_dir=base_dir,
                is_debug=True
            )
            
            # Read the generated markdown file
            markdown_content = self._read_markdown_files(base_dir)
            
            # Cleanup temp directory
            self._cleanup_temp_dir(base_dir)
            
            if markdown_content:
                logger.info(f"Successfully crawled stores from {settings.store_url}")
                return markdown_content
            else:
                logger.error(f"Failed to crawl stores from {settings.store_url}")
                raise Exception(f"Failed to crawl stores from {settings.store_url}")
        except Exception as e:
            logger.error(f"Error crawling stores: {str(e)}")
            # Cleanup on error too
            self._cleanup_temp_dir(base_dir)
            raise
    
    async def crawl_products(self) -> str:
        """Crawl product information from the website"""
        from app.config.settings import settings
        base_dir = 'temp_crawl_products'
        
        try:
            crawler = self._get_crawler()
            
            logger.info(f"🕸️ Starting crawl of {settings.product_url}")
            crawler(
                settings.product_url,
                max_depth=0,
                num_threads=1,
                base_dir=base_dir,
                is_debug=True
            )
            
            # Read the generated markdown file
            markdown_content = self._read_markdown_files(base_dir)
            
            # Cleanup temp directory
            self._cleanup_temp_dir(base_dir)
            
            if markdown_content:
                logger.info(f"Successfully crawled products from {settings.product_url}")
                return markdown_content
            else:
                logger.error(f"Failed to crawl products from {settings.product_url}")
                raise Exception(f"Failed to crawl products from {settings.product_url}")
        except Exception as e:
            logger.error(f"Error crawling products: {str(e)}")
            # Cleanup on error too
            self._cleanup_temp_dir(base_dir)
            raise
    
    def _read_markdown_files(self, base_dir: str) -> str:
        """Read all markdown files from the crawled directory"""
        try:
            if not os.path.exists(base_dir):
                logger.warning(f"Directory {base_dir} does not exist")
                return ""
            
            markdown_content = []
            
            # Walk through all files in the directory
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                markdown_content.append(content)
                                logger.info(f"Read markdown file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error reading file {file_path}: {str(e)}")
            
            return "\n\n".join(markdown_content) if markdown_content else ""
            
        except Exception as e:
            logger.error(f"Error reading markdown files from {base_dir}: {str(e)}")
            return ""
    
    def _cleanup_temp_dir(self, base_dir: str):
        """Remove temporary crawl directory"""
        try:
            if os.path.exists(base_dir):
                shutil.rmtree(base_dir)
                logger.info(f"Cleaned up temporary directory: {base_dir}")
            else:
                logger.debug(f"Temporary directory {base_dir} does not exist, nothing to clean")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory {base_dir}: {str(e)}")
    
    async def close(self):
        """Close the crawler and cleanup any remaining temp files"""
        if self.crawler:
            logger.info("Closing MarkdownCrawler")
            # Cleanup any remaining temp directories
            self._cleanup_temp_dir('temp_crawl_stores')
            self._cleanup_temp_dir('temp_crawl_products')
            self.crawler = None
            logger.info("MarkdownCrawler closed successfully")
        else:
            logger.info("No crawler to close")

# Global crawler instance
crawl_service = CrawlService()
