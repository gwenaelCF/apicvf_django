from django.core.management.base import BaseCommand
from procedere import gestion_retard

class Command(BaseCommand):
    help='''
    passe-plat pour démarrer la commande de check des cdp en retard
    '''

    def handle(self, *args, **options):
    	gestion_retard.check_retard()