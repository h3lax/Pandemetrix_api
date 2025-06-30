from flask_restx import Namespace, Resource, reqparse
from app.etl.components.mongodb import fetch_data
from config import Config
from datetime import datetime
import json

filtered_data_ns = Namespace("data", description="Filtered Data Operations")

parser = reqparse.RequestParser()
parser.add_argument("country", type=str, required=False, help="Country filter")
parser.add_argument("start_date", type=str, required=False, help="Start date (YYYY-MM-DD)")
parser.add_argument("end_date", type=str, required=False, help="End date (YYYY-MM-DD)")
parser.add_argument("page", type=int, default=1, help="Page number")
parser.add_argument("page_size", type=int, default=1000, help="Number of documents per page")

@filtered_data_ns.route("/")
class FilteredData(Resource):
    @filtered_data_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        country = args.get("country")
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        page = args.get("page")
        page_size = args.get("page_size")
        skip = (page - 1) * page_size
        
        # Build the MongoDB filter
        query = {}
        
        # Filtrer par pays seulement si spécifié
        if country:
            query['country'] = country
        # Sinon, récupérer TOUS les pays disponibles
        
        # Date filtering
        date_filter = {}
        if start_date:
            try:
                date_filter['$gte'] = start_date  # Garder en string pour MongoDB
            except ValueError:
                return {"error": "Invalid start date format. Use YYYY-MM-DD."}, 400
        if end_date:
            try:
                date_filter['$lte'] = end_date
            except ValueError:
                return {"error": "Invalid end date format. Use YYYY-MM-DD."}, 400
        
        if date_filter:
            query['date'] = date_filter
        
        # Fetch data avec aggregation pour diversifier
        try:
            # Si pas de filtres spécifiques, retourner tous les pays disponibles
            if not country and not start_date and not end_date:
                # Pipeline simple pour tous les pays avec données récentes
                pipeline = [
                    {'$sort': {'date': -1}},  # Plus récent d'abord
                    {'$limit': page_size},    # Limiter le nombre total
                    {'$project': {
                        '_id': 1,
                        'country': 1,
                        'date': 1,
                        'new_cases': 1,
                        'new_deaths': 1,
                        'total_cases': 1,
                        'total_deaths': 1
                    }}
                ]
                
                # Utiliser directement MongoDB
                from app.database.mongoClient import get_db
                db = get_db()
                collection = db['ml_cases_deaths']  # Collection principale
                
                data = list(collection.aggregate(pipeline))
                
                # Nettoyer les ObjectId
                for doc in data:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                
                return data, 200
            else:
                # Utiliser la fonction normale pour filtres spécifiques
                data = fetch_data("ml_cases_deaths", query, skip=skip, limit=page_size)
                return json.loads(data), 200
                
        except Exception as e:
            return {"error": str(e)}, 500
        
@filtered_data_ns.route("/countries")
class AllCountries(Resource):
    def get(self):
        """Retourne tous les pays disponibles avec leurs statistiques"""
        try:
            from app.database.mongoClient import get_db
            db = get_db()
            collection = db['ml_cases_deaths']
            
            # Exclure les continents et agrégations
            excluded_regions = [
                'World', 'Europe', 'Asia', 'Africa', 'North America', 'South America', 
                'Oceania', 'Antarctica', 'European Union', 'High income', 'Low income',
                'Lower middle income', 'Upper middle income', 'International'
            ]
            
            # Agrégation pour obtenir tous les pays avec leurs stats
            pipeline = [
                {'$match': {'country': {'$nin': excluded_regions}}},
                {'$group': {
                    '_id': '$country',
                    'totalCases': {'$sum': '$new_cases'},
                    'totalDeaths': {'$sum': '$new_deaths'},
                    'latestDate': {'$max': '$date'},
                    'firstDate': {'$min': '$date'},
                    'recordCount': {'$sum': 1}
                }},
                {'$project': {
                    'country': '$_id',
                    'totalCases': 1,
                    'totalDeaths': 1,
                    'latestDate': 1,
                    'firstDate': 1,
                    'recordCount': 1,
                    '_id': 0
                }},
                {'$sort': {'totalCases': -1}}
            ]
            
            countries = list(collection.aggregate(pipeline))
            
            return {
                'countries': countries,
                'total_countries': len(countries)
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

@filtered_data_ns.route("/all")
class AllData(Resource):
    @filtered_data_ns.expect(parser)
    def get(self):
        """Retourne toutes les données sans filtrage par pays"""
        args = parser.parse_args()
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        page = args.get("page")
        page_size = args.get("page_size", 2000)  # Plus de données par défaut
        skip = (page - 1) * page_size
        
        try:
            from app.database.mongoClient import get_db
            db = get_db()
            collection = db['ml_cases_deaths']
            
            # Query simple avec dates si spécifiées et exclusion des continents
            excluded_regions = [
                'World', 'Europe', 'Asia', 'Africa', 'North America', 'South America', 
                'Oceania', 'Antarctica', 'European Union', 'High income', 'Low income',
                'Lower middle income', 'Upper middle income', 'International'
            ]
            
            query = {'country': {'$nin': excluded_regions}}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter['$gte'] = start_date
                if end_date:
                    date_filter['$lte'] = end_date
                query['date'] = date_filter
            
            # Récupérer tous les pays
            data = list(collection.find(query)
                       .sort('date', -1)
                       .skip(skip)
                       .limit(page_size))
            
            # Nettoyer les ObjectId
            for doc in data:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return data, 200
            
        except Exception as e:
            return {"error": str(e)}, 500