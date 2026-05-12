from django.core.management.base import BaseCommand
from categories.models import Category
from servers.models import Server
from applications.models import Application, ApplicationEnvironment, AppAdmin

class Command(BaseCommand):
    help = 'Seed initial data for App Catalog'

    def handle(self, *args, **options):
        # Create Categories
        data_cat, _ = Category.objects.get_or_create(
            name="Data Engineering", 
            slug="data-engineering",
            description="Tools for data ingestion and processing",
            color="#3b82f6",
            icon="fa-database"
        )
        web_cat, _ = Category.objects.get_or_create(
            name="Web Application", 
            slug="web-app",
            description="Front-facing web applications",
            color="#10b981",
            icon="fa-globe"
        )
        api_cat, _ = Category.objects.get_or_create(
            name="API Services", 
            slug="api-services",
            description="Backend REST/GraphQL APIs",
            color="#8b5cf6",
            icon="fa-server"
        )

        # Create Servers
        main_server, _ = Server.objects.get_or_create(
            name="Main Cluster",
            host_ip="192.168.1.100",
            os="Ubuntu 22.04 LTS",
            provider="DigitalOcean",
            location="Singapore"
        )

        # Create Applications
        nifi, _ = Application.objects.get_or_create(
            name="Apache NiFi",
            slug="apache-nifi",
            description="Powerful and reliable system to process and distribute data.",
            category=data_cat,
            framework="Java",
            database="H2"
        )
        ApplicationEnvironment.objects.get_or_create(
            application=nifi,
            environment="PROD",
            defaults={
                "server": main_server,
                "url": "https://nifi.apache.org",
                "local_ip": "192.168.1.100",
                "port": "8443",
            },
        )

        airflow, _ = Application.objects.get_or_create(
            name="Apache Airflow",
            slug="apache-airflow",
            description="Platform to programmatically author, schedule and monitor workflows.",
            category=data_cat,
            framework="Python/Django",
            database="PostgreSQL"
        )
        ApplicationEnvironment.objects.get_or_create(
            application=airflow,
            environment="BETA",
            defaults={
                "server": main_server,
                "url": "http://airflow.local",
                "local_ip": "192.168.1.100",
                "port": "8080",
            },
        )

        # Create Admins
        AppAdmin.objects.get_or_create(
            application=nifi,
            name="Budi Data",
            email="budi@data.com",
            role="Data Engineer",
            whatsapp="08123456789"
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))
