# aplicacao/management/commands/importar_dados.py
import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Avaliacao
    class Command(BaseCommand):
    help = 'Importa dados de avaliações de livros de um arquivo CSV'
    def add_arguments(self, parser):
    parser.add_argument('books-15k.csv', type=str, help='O caminho para o arquivo
    CSV')
    
    def handle(self, *args, **kwargs):
    caminho_csv = kwargs['caminho_csv']
    df = pd.read_csv(caminho_csv)
    for _, row in df.iterrows():
    Avaliacao.objects.create(**row.to_dict())
    self.stdout.write(self.style.SUCCESS('Dados importados com sucesso!'))