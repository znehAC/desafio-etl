import logging
import re
import time
import os
import dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import marshmallow
from models import Proposicao, Tramitacao, ProposicaoSchema, TramitacaoSchema

dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    ETL_MAX_WORKERS = int(os.getenv('ETL_MAX_WORKERS', 5))
    ETL_ENGINE_POOL_SIZE = int(os.getenv('ETL_ENGINE_POOL_SIZE', 10))
    ETL_RETRIES = int(os.getenv('ETL_RETRIES', 3))
    ETL_BACKOFF_FACTOR = float(os.getenv('ETL_BACKOFF_FACTOR', 0.3))
except Exception as e:
    logging.error('Failed to load environment variables. Error: %s', e)
    exit(1)

DB_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Configure connection pool
engine = create_engine(DB_URI, pool_size=ETL_ENGINE_POOL_SIZE, max_overflow=20)

def extract():
    """
    Extracts data from the API in a loop, processes the data in parallel, transforms it, and loads it into a database.

    Returns:
        None
    """
    base_url = "https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ano=2023&ord=3"
    page = 0
     
    total = 0
    while True:
        # Fetch pages in parallel, process as it's received
        with ThreadPoolExecutor(max_workers=ETL_MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_page, base_url, page, ETL_RETRIES, ETL_BACKOFF_FACTOR): page for page in range(page, page+ETL_MAX_WORKERS)}

            pages_fetched = False
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        #Transform and load into database
                        start = time.time()
                        transformed_propositions = transform(result)
                        transform_time = time.time() - start
                        start = time.time()
                        load(transformed_propositions)
                        load_time = time.time() - start
                        total += len(transformed_propositions)
                        logging.info(f'Proposicoes Criadas: {total} - Transform Time: {transform_time} - Load Time: {load_time}')
                        pages_fetched = True
                except Exception as e:
                    logging.error(f"Erro ao processar a página {futures[future]}: {e}")
            # If no pages were fetched, we're done
            if not pages_fetched:
                break
            page += ETL_MAX_WORKERS


def fetch_page(base_url, page, retries=3, backoff_factor=0.3):
    """
    Fetches a page from the specified base URL with retries and backoff strategy.

    Args:
        base_url (str): The base URL to fetch the page from.
        page (int): The page number to fetch.
        retries (int): The number of retries to attempt in case of failure.
        backoff_factor (float): The backoff factor for exponential backoff strategy.

    Returns:
        list or None: The list of fetched results from the page, or None if no results are retrieved.
    """
    for attempt in range(retries):
        try:
            response = requests.get(f"{base_url}&p={page}")
            response.raise_for_status()
            results = response.json().get("resultado", {}).get("listaItem", [])
            return results if results else None
        except requests.exceptions.RequestException as e:
            # Retry in case of failure
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
            else:
                logging.error(f"Erro na solicitação da página {page}: {e}")
                return None

def transform(propositions):
    """
    Transforms a list of propositions into a list of dictionaries with transformed data.

    Args:
        propositions (list): A list of dictionaries representing propositions.

    Returns:
        list: A list of dictionaries with transformed data. Each dictionary contains the following keys:
            - 'author' (str): The author of the proposition.
            - 'presentationDate' (datetime or None): The presentation date of the proposition.
            - 'ementa' (str): The 'resume' of the proposition.
            - 'regime' (str): The regime of the proposition.
            - 'situation' (str): The situation of the proposition.
            - 'propositionType' (str): The type of the proposition.
            - 'number' (str): The number of the proposition.
            - 'year' (int or None): The year of the proposition.
            - 'city' (str): The city of the proposition.
            - 'state' (str): The state of the proposition.
            - 'processings' (list): A list of dictionaries representing the processings of the proposition. Each dictionary contains the following keys:
                - 'createdAt' (datetime or None): The creation date of the processing.
                - 'description' (str): The description of the processing.
                - 'local' (str): The local of the processing.

    """
    transformed_propositions = []

    for prop in propositions:
        proposition_schema = ProposicaoSchema()

        transformed_proposition = {
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
        # Some proposition types don't have an ementa, so we're getting the "assunto"
        if not transformed_proposition['ementa']:
            transformed_proposition['ementa'] = prop.get('assunto', '')

        # Validate data integrity
        try:
            proposition_schema.load(transformed_proposition)
        except marshmallow.exceptions.ValidationError as ve:
            print(transformed_proposition['presentationDate'])
            logging.error(f"Validation error in proposition: {ve.messages}")
            continue

        # Convert date to datetime, if there is None, set it to 1900-01-01
        
        transformed_proposition['presentationDate'] = convert_date(transformed_proposition['presentationDate'])


        transformed_processings = []
        for tram in prop.get('listaHistoricoTramitacoes', []):
            tramitacao_schema = TramitacaoSchema()

            transformed_processing = {
                'createdAt': tram.get('data', None),
                'description': tram.get('historico', ''),
                'local': tram.get('local', ''),
            }

            # Validate data integrity
            try:
                tramitacao_schema.load(transformed_processing)
            except marshmallow.exceptions.ValidationError as ve:
                logging.error(f"Validation error in proposition: {ve.messages}")
                continue
            
            # Convert date to datetime, if there is None, set it to 1900-01-01
            transformed_processing['createdAt'] = convert_date(transformed_processing['createdAt'])

            transformed_processings.append(transformed_processing)

        transformed_proposition['processings'] = transformed_processings
        transformed_propositions.append(transformed_proposition)

    df = pd.DataFrame(transformed_propositions)
    df = df.where(pd.notnull(df), None)

    transformed_propositions = df.to_dict(orient='records')
    transformed_propositions = clean_data(transformed_propositions)
    return transformed_propositions

def convert_date(date):
    if date is not None:
        date = pd.to_datetime(date, errors='coerce')
    else:
        date = pd.Timestamp('1900-01-01')

    return date

def load(propositions):
    """
    A function that loads propositions into the database.
    
    Args:
        propositions (list): A list of propositions to be loaded into the database.
    
    Returns:
        None
    """
    try:
        with sessionmaker(bind=engine)() as session:
            proposition_objects = []

            for prop in propositions:
                processings_data = prop.pop('processings') 
                proposition = get_or_create(prop, session)
                for processing in processings_data:
                    processing_obj = Tramitacao(**processing)
                    if processing_obj not in proposition.tramitacoes:
                        proposition.tramitacoes.append(processing_obj)
                proposition_objects.append(proposition)

            # Bullk saving propositions, the processes are saved as well
            session.bulk_save_objects(proposition_objects)
            session.commit()
    # Error handlind for SQLAlchemy, usually data types are not compatible
    except SQLAlchemyError as e:
        logging.error(f"Erro ao carregar dados no banco de dados: {e}")
   
def get_or_create(proposition, session):
    existing_proposition = session.query(Proposicao).filter_by(
        author=proposition['author'],
        presentationDate=proposition['presentationDate'],
        ementa=proposition['ementa'],
        propositionType=proposition['propositionType'],
        number=proposition['number'],
        year=proposition['year']
    ).first()

    if not existing_proposition:
        proposition = Proposicao(**proposition)
    else:
        for key, value in proposition.items():
            setattr(existing_proposition, key, value)
        proposition = existing_proposition

    return proposition

def clean_data(propositions):
    """
    Cleans the data in the propositions list by removing unnecessary white spaces and special characters.
    
    Args:
        propositions (list): A list of propositions to be cleaned.
    
    Returns:
        list: The cleaned list of propositions.
    """
    for prop in propositions:
        cleaned_prop = {
            # Remove unnecessary white spaces and special characters
            key: re.sub(r'\s+', ' ', value.strip().replace('\n', ' ').replace('\t', ' '))
            if isinstance(value, str) else value
            for key, value in prop.items()
        }

        cleaned_prop['processings'] = [
            {
                key: re.sub(r'\s+', ' ', value.strip().replace('\n', ' ').replace('\t', ' '))
                if isinstance(value, str) else value
                for key, value in processing.items()
            }
            for processing in cleaned_prop['processings']
        ]

    return propositions

if __name__ == "__main__":
    extract()