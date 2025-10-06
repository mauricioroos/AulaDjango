import pandas as pd
from django.core.management.base import BaseCommand
from aplicacao.models import Avaliacao

class Command(BaseCommand):
    help = 'Importa dados de avaliacoes de livros de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('caminho_csv', type=str, help='O caminho para o arquivo CSV')

    def handle(self, *args, **kwargs):
        caminho_csv = kwargs['caminho_csv']
        df = pd.read_csv(caminho_csv)

        Avaliacao.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Base de dados antiga limpa...'))

        for _, row in df.iterrows():
            Avaliacao.objects.create(
                title=row.get('title'),
                price=row.get('price'),
                user_id=row.get('user_id'),
                profile_name=row.get('profile_name'),
                review_helpfulness=row.get('review_helpfulness'),
                review_score=row.get('review_score'),
                review_time=row.get('review_time'),
                review_summary=row.get('review_summary'),
                texto_review=row.get('review_text')
            )
        self.stdout.write(self.style.SUCCESS('Dados importados com sucesso!'))