from django.core.management.base import BaseCommand
from scrape_products import scrape_products


class Command(BaseCommand):
    help = "Scrapes products from ridesurronusa.com and imports them into Django database"

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help="Number of products to scrape (default: 10)")
        parser.add_argument('--all', action='store_true', help="Scrape all products without limit")
        parser.add_argument('--delete-existing', action='store_true', help="Delete existing products before scraping")

    def handle(self, *args, **options):
        limit = None if options.get('all') else options.get('limit')
        delete_existing = options.get('delete_existing', False)
        scrape_products(limit=limit, delete_existing=delete_existing)
