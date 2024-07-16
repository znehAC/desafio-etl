import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Proposicao, Tramitacao

import re
import dotenv
import os

dotenv.load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

def extract():
    base_url = "https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ano=2023&ord=3"
    propositions = []
    page = 0

    while True:
        try:
            # Make a request to the API for each page
            response = requests.get(f"{base_url}&p={page}")
            response.raise_for_status()
            results = response.json().get("resultado", {}).get("listaItem", [])

            if not results:
                break

            # Transform the data, cleanning text and dates
            transformed_propositions = transform(results)
            # Load the data into the database
            load(transformed_propositions)
            
            propositions.extend(results)
            print('Proposicoes Criadas:', len(propositions))
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na solicitação: {e}")
            break
        except Exception as e:
            print(f"Erro ao processar a resposta: {e}")
            break

def transform(propositions):
    transformed_propositions = []

    for prop in propositions:
        transformed_prop = {
            'author': prop.get('autor', ''),
            'presentationDate': prop.get('dataPublicacao', None),
            'ementa': prop.get('ementa', ''),
            'regime': prop.get('regime', ''),
            'situation': prop.get('situacao', ''),
            'propositionType': prop.get('tipoProjeto', ''),
            'number': prop.get('numero', ''),
            'year': prop.get('ano', None),
            'city': 'Belo Horizonte',
            'state': 'Minas Gerais'
        }

        if transformed_prop['presentationDate']:
            transformed_prop['presentationDate'] = pd.to_datetime(transformed_prop['presentationDate'], errors='coerce')
        
        # adding Processings (Tramitacoes)
        transformed_processings = []
        for tram in prop.get('listaHistoricoTramitacoes', []):
            transformed_processing = {
                'createdAt': tram.get('data', None),
                'description': tram.get('historico', ''),
                'local': tram.get('local', ''),
            }

            if transformed_processing['createdAt']:
                transformed_processing['createdAt'] = pd.to_datetime(transformed_processing['createdAt'], errors='coerce')
            
            transformed_processings.append(transformed_processing)

        transformed_prop['processings'] = transformed_processings

        transformed_propositions.append(transformed_prop)

        # Cleaning text
        transformed_propositions = clean_data(transformed_propositions)

    return transformed_propositions

def load(propositions):
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for prop in propositions:
            processings_data = prop.pop('processings') 

            # Check if the proposition already exists
            existing_proposition = session.query(Proposicao).filter_by(
                author=prop['author'],
                presentationDate=prop['presentationDate'],
                ementa=prop['ementa'],
                regime=prop['regime'],
                situation=prop['situation'],
                propositionType=prop['propositionType'],
                number=prop['number'],
                year=prop['year']
            ).first()

            # If new proposition, add it
            if not existing_proposition:
                proposition = Proposicao(**prop)
                for processing in processings_data:
                    processing = Tramitacao(**processing)
                    proposition.tramitacoes.append(processing)

                session.add(proposition)
            # If it already exists, update it
            else:
                for key, value in prop.items():
                    setattr(existing_proposition, key, value)

                for processing in processings_data:
                    processing = Tramitacao(**processing)
                    if processing not in existing_proposition.tramitacoes:
                        existing_proposition.tramitacoes.append(processing)


        session.commit()
    except Exception as e:
        print(f"Erro ao carregar dados no banco de dados: {e}")
        session.rollback()
    finally:
        session.close()

def clean_data(propositions):
    for prop in propositions:
        for key, value in prop.items():
            if isinstance(value, str):
                value = value.strip()
                value = value.replace('\n', ' ')
                value = value.replace('\t', ' ')
                value = re.sub(r'\s+', ' ', value).strip()
                prop[key] = value

        for processing in prop['processings']:
            for key, value in processing.items():
                if isinstance(value, str):
                    value = value.strip()
                    value = value.replace('\n', ' ')
                    value = value.replace('\t', ' ')
                    value = re.sub(r'\s+', ' ', value).strip()

                    processing[key] = value
    return propositions


extract()